# app\models\game.py
from app import db

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    developer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    developer = db.relationship('User', backref=db.backref('games', lazy=True))
    image_path = db.Column(db.String(255), nullable=True)  # Сурет жолы
    purchases = db.relationship('User', secondary='purchases', backref=db.backref('purchased_games', lazy='dynamic'))

    def __repr__(self):
        return f'<Game {self.title}>'