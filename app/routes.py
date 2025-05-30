# app/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db, openai_client
from app.models.user import User
from app.models.game import Game
from app.models.purchase import purchases
from app.auth.forms import LoginForm, RegistrationForm, AddGameForm, EditGameForm
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import datetime
import os
from app import csrf

main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)
admin_bp = Blueprint('admin', __name__)
developer_bp = Blueprint('developer', __name__)

def login_required_with_timeout(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if 'last_activity' in session:
            last_activity = datetime.fromtimestamp(session['last_activity'])
            if datetime.now() - last_activity > current_app.config['PERMANENT_SESSION_LIFETIME']:
                logout_user()
                flash('Session expired. Please log in again.', 'warning')
                return redirect(url_for('auth.login'))
        session['last_activity'] = datetime.now().timestamp()
        return f(*args, **kwargs)
    return decorated_function

# Main Blueprint routes
@main_bp.route('/')
def index():
    search_query = request.args.get('q', '').strip()
    if search_query:
        games = Game.query.filter(Game.title.ilike(f'%{search_query}%')).all()
    else:
        games = Game.query.all()
    return render_template('index.html', games=games, search_query=search_query)

@main_bp.route('/profile')
@login_required_with_timeout
def profile():
    return render_template('profile.html', user=current_user)

@main_bp.route('/purchase/<int:game_id>', methods=['POST'])
@login_required_with_timeout
def purchase_game(game_id):
    if current_user.is_developer or current_user.is_admin:
        flash('Only regular users can purchase games.', 'danger')
        return redirect(url_for('main.index'))

    game = Game.query.get_or_404(game_id)
    if game in current_user.purchased_games:
        flash('You have already purchased this game!', 'warning')
    else:
        current_user.purchased_games.append(game)
        db.session.commit()
        flash('Game purchased successfully!', 'success')
    return redirect(url_for('main.index'))

@main_bp.route('/library')
@login_required_with_timeout
def library():
    if current_user.is_developer or current_user.is_admin:
        flash('Access denied: Library is for regular users only.', 'danger')
        return redirect(url_for('main.index'))
    return render_template('library.html', games=current_user.purchased_games.all())

@main_bp.route('/chat')
def chat():
    return render_template('chat.html')


@main_bp.route('/chatbot', methods=['POST'])
@csrf.exempt
def chatbot_response():
    user_input = request.form.get('message')
    print(f'Received message: {user_input!r}')
    if not user_input:
        return jsonify({'response': 'Error: Message didnt send'}), 400

    try:

        games = Game.query.all()
        game_info = "\n".join([
                                  f"- {game.title} (Price: ${game.price}, Description: {game.description[:50]}{'...' if len(game.description) > 50 else ''})"
                                  for game in games])
        context = f"list of Games :\n{game_info}\nUsers question: {user_input}"

        completion = openai_client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": current_app.config.get('SITE_URL', 'http://localhost:5000'),
                "X-Title": current_app.config.get('SITE_NAME', 'Game Store'),
            },
            extra_body={},
            model="deepseek/deepseek-r1-0528:free",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful FAQ assistant for a game store.If the question is in any language, the answer should be in that language.but the main language is English. Provide concise answers about game purchasing, searching, or platform usage. Use the provided context about available games to give detailed and accurate responses. If asked about specific games, analyze the context and offer additional info like price or description. Context: " + context
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        )
        response = completion.choices[0].message.content
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'response': f'Error: {str(e)}'}), 500

# Auth Blueprint routes
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data)
        user.set_password(form.password.data)
        user.is_developer = (form.role.data == 'developer')
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            elif user.is_developer:
                return redirect(url_for('developer.dashboard'))
            return redirect(url_for('main.index'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

# Admin Blueprint routes
@admin_bp.route('/dashboard')
@login_required_with_timeout
def dashboard():
    if not current_user.is_admin:
        flash('Access denied: Admins only.', 'danger')
        return redirect(url_for('main.index'))
    purchase_records = db.session.query(User, Game).join(purchases, User.id == purchases.c.user_id).join(Game, Game.id == purchases.c.game_id).all()
    return render_template('admin_dashboard.html', purchases=purchase_records)

@admin_bp.route('/manage_users', methods=['GET', 'POST'])
@login_required_with_timeout
def manage_users():
    if not current_user.is_admin:
        flash('Access denied: Admins only.', 'danger')
        return redirect(url_for('main.index'))

    users = User.query.all()
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        action = request.form.get('action')
        user = User.query.get_or_404(user_id)

        if action == 'delete':
            if user.id == current_user.id:
                flash('You cannot delete yourself!', 'danger')
            else:
                db.session.delete(user)
                db.session.commit()
                flash('User deleted successfully!', 'success')
        elif action == 'update_role':
            role = request.form.get('role')
            if role == 'admin':
                user.is_admin = True
                user.is_developer = False
            elif role == 'developer':
                user.is_admin = False
                user.is_developer = True
            else:  # role == 'user'
                user.is_admin = False
                user.is_developer = False
            db.session.commit()
            flash('User role updated successfully!', 'success')
        return redirect(url_for('admin.manage_users'))

    return render_template('manage_users.html', users=users)

# Developer Blueprint routes
@developer_bp.route('/dashboard')
@login_required_with_timeout
def dashboard():
    if not current_user.is_developer:
        flash('Access denied: Developers only.', 'danger')
        return redirect(url_for('main.index'))
    return render_template('developer_dashboard.html')

@developer_bp.route('/add_game', methods=['GET', 'POST'])
@login_required_with_timeout
def add_game():
    if not current_user.is_developer:
        flash('Access denied: Developers only.', 'danger')
        return redirect(url_for('main.index'))

    form = AddGameForm()
    if form.validate_on_submit():
        game = Game(
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            developer_id=current_user.id
        )
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            form.image.data.save(filepath)
            game.image_path = f"uploads/{filename}"
        db.session.add(game)
        db.session.commit()
        flash('Game added successfully!', 'success')
        return redirect(url_for('developer.dashboard'))
    return render_template('add_game.html', form=form)

@developer_bp.route('/games')
@login_required_with_timeout
def view_games():
    if not current_user.is_developer:
        flash('Access denied: Developers only.', 'danger')
        return redirect(url_for('main.index'))
    games = Game.query.filter_by(developer_id=current_user.id).all()
    return render_template('developer_games.html', games=games)

@developer_bp.route('/edit_game/<int:game_id>', methods=['GET', 'POST'])
@login_required_with_timeout
def edit_game(game_id):
    if not current_user.is_developer:
        flash('Access denied: Developers only.', 'danger')
        return redirect(url_for('main.index'))

    game = Game.query.get_or_404(game_id)
    if game.developer_id != current_user.id:
        flash('You are not authorized to edit this game.', 'danger')
        return redirect(url_for('developer.dashboard'))

    form = EditGameForm(obj=game)
    if form.validate_on_submit():
        game.title = form.title.data
        game.description = form.description.data
        game.price = form.price.data
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            form.image.data.save(filepath)
            game.image_path = f"uploads/{filename}"
        db.session.commit()
        flash('Game updated successfully!', 'success')
        return redirect(url_for('developer.view_games'))
    return render_template('edit_game.html', form=form, game=game)

@developer_bp.route('/delete_game/<int:game_id>', methods=['POST'])
@login_required_with_timeout
def delete_game(game_id):
    if not current_user.is_developer:
        flash('Access denied: Developers only.', 'danger')
        return redirect(url_for('main.index'))

    game = Game.query.get_or_404(game_id)
    if game.developer_id != current_user.id:
        flash('You are not authorized to delete this game.', 'danger')
        return redirect(url_for('developer.view_games'))

    db.session.delete(game)
    db.session.commit()
    flash('Game deleted successfully!', 'success')
    return redirect(url_for('developer.view_games'))