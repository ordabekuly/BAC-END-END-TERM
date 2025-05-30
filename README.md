Game Store Web Application
Introduction
The Game Store is a full-stack web application built with Flask, designed to provide a platform for users to browse, purchase, and manage games, while developers can add and edit their games, and administrators can manage users and monitor purchases. The application integrates an AI-powered chatbot using the OpenRouter API to assist users with game-related queries, enhancing the user experience with intelligent, context-aware responses.
This project fulfills the requirements of a final project for a full-stack web development course, demonstrating proficiency in Flask, SQLAlchemy, WTForms, Jinja2, Bootstrap, and AI integration.
Objectives

Provide a secure, user-friendly platform for game purchasing and management.
Implement role-based access for regular users, developers, and administrators.
Integrate an AI chatbot to answer game-related questions.
Demonstrate object-oriented programming (OOP), modular design with Flask Blueprints, and secure session management.
Support file uploads for game images and advanced database operations.

Features
Core Functionality

User Registration and Login: Users can register with an email, username, and password, choosing a role (User or Developer). Passwords are securely hashed using werkzeug.security.
Role-Based Access:
Regular Users: Browse, search, and purchase games, and view their purchased games in a personal library.
Developers: Add, edit, and delete their own games, including uploading game images.
Administrators: View recent purchases and manage user roles (User, Developer, Admin) or delete users.


Game Management: Developers can create and update games with titles, descriptions, prices, and images. Users can purchase games, and purchases are tracked in a many-to-many relationship.
Search: A search feature allows users to find games by title using case-insensitive filtering.
File Uploads: Developers can upload game images (JPG, PNG, JPEG), with file type validation and secure storage.
AI Chatbot: An AI-powered FAQ chatbot answers questions about games, leveraging the OpenRouter API with game data as context.

Technical Features

Flask Blueprints: Modular code organization with separate blueprints for main, auth, admin, and developer routes.
SQLAlchemy ORM: Manages database operations with models for User, Game, and purchases (many-to-many table).
Session Management: Secure session handling with Flask-Login, including a 3-hour session timeout and a "Remember me" feature.
Form Validation: WTForms for form creation and validation, with custom checks for unique email/username.
Frontend: Responsive design using Bootstrap 5.3, custom CSS with a futuristic theme (Orbitron font, glow effects), and Jinja2 templates.
Database Relationships: One-to-many (User to Game) and many-to-many (User to Game via purchases) relationships with JOIN operations.
Security: CSRF protection, secure file uploads with secure_filename, and hashed passwords.

AI Integration
The application integrates an AI-powered chatbot using the OpenRouter API (DeepSeek model: deepseek/deepseek-r1-0528:free). The chatbot is logically connected to the project's theme by providing answers to game-related questions, such as game prices, descriptions, or platform usage. It uses a context string generated from the Game database table, including titles, prices, and truncated descriptions.
How It Works

The chatbot is accessible via the /chat route, where users can input questions in a sleek chat interface.
User messages are sent to the /chatbot endpoint, which queries the OpenRouter API with a context that includes all available games.
The API processes the query and returns a response, which is displayed in the chat UI with timestamps.
Example: A user might ask, "What is the price of Game X?" The chatbot retrieves the game's price from the context and responds accurately.

Technical Details

API: OpenRouter API with a custom openai_client initialized in app/__init__.py.
Context: Dynamically generated from Game.query.all() to include game titles, prices, and descriptions.
Implementation: The main_bp.route('/chatbot') handles POST requests, sends the user input with context to the API, and returns a JSON response.
Error Handling: Catches and displays API errors in the chat interface.

Code Structure
Directory Structure
game_store/
├── app/
│   ├── __init__.py           # Flask app initialization, extensions, and blueprints
│   ├── models/               # SQLAlchemy models
│   │   ├── game.py           # Game model
│   │   ├── purchase.py       # Purchases many-to-many table
│   │   ├── user.py           # User model with Flask-Login integration
│   ├── auth/                 # Authentication blueprint
│   │   ├── __init__.py
│   │   ├── forms.py          # WTForms for registration, login, and game forms
│   ├── admin/                # Admin blueprint
│   │   ├── __init__.py
│   ├── developer/            # Developer blueprint
│   │   ├── __init__.py
│   ├── main/                 # Main blueprint
│   │   ├── __init__.py
│   ├── routes.py             # All blueprint routes
│   ├── static/               # Static files (CSS, images)
│   │   ├── uploads/          # Uploaded game images
│   ├── templates/            # Jinja2 templates
│   │   ├── base.html         # Base template with navigation
│   │   ├── index.html        # Home page with game listing
│   │   ├── chat.html         # Chatbot interface
│   │   ├── profile.html      # User profile
│   │   ├── library.html      # User game library
│   │   ├── login.html        # Login page
│   │   ├── register.html     # Registration page
│   │   ├── admin_dashboard.html  # Admin dashboard
│   │   ├── manage_users.html     # User management
│   │   ├── developer_dashboard.html  # Developer dashboard
│   │   ├── developer_games.html  # Developer game list
│   │   ├── add_game.html     # Add game form
│   │   ├── edit_game.html    # Edit game form
├── config.py                 # Configuration (database URI, secret key, etc.)
├── run.py                   # Application entry point
├── .env                     # Environment variables (API keys, etc.)

OOP and Modularity

Models: User and Game classes inherit from db.Model and UserMixin for Flask-Login integration.
Forms: WTForms classes (RegistrationForm, LoginForm, etc.) for form handling and validation.
Blueprints: Separate main, auth, admin, and developer blueprints for modular routing.
Decorators: Custom login_required_with_timeout decorator for session timeout management.

ER Diagram
Below is a simplified Entity-Relationship (ER) diagram for the database:
[User] --(1:N)-- [Game]
  |                |
  |                |
(M:N)-----------[Purchases]


User:
id (Primary Key)
email (Unique)
username (Unique)
password (Hashed)
is_admin (Boolean)
is_developer (Boolean)


Game:
id (Primary Key)
title
description
price
developer_id (Foreign Key to User)
image_path


Purchases (Many-to-Many):
user_id (Foreign Key to User)
game_id (Foreign Key to Game)



Setup and Installation
Prerequisites

Python 3.8+
PostgreSQL
Git
Virtual environment (recommended)

Installation Steps

Clone the repository:git clone https://github.com/yourusername/game_store.git
cd game_store


Create and activate a virtual environment:python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install dependencies:pip install -r requirements.txt


Set up environment variables in .env:SECRET_KEY=your_secret_key
DATABASE_URL=postgresql://username:password@localhost:5432/game_store
OPENROUTER_API_KEY=your_openrouter_api_key


Initialize the database:flask db init
flask db migrate
flask db upgrade


Run the application:python run.py


Access the app at http://localhost:5000.

Dependencies

flask
flask-sqlalchemy
flask-login
flask-wtf
flask-migrate
openai
python-dotenv
werkzeug

Challenges and Solutions

Challenge: Integrating the OpenRouter API for the chatbot while ensuring relevant responses.
Solution: Dynamically generate context from the Game table and include it in API requests to provide accurate game-related answers.


Challenge: Secure file uploads with proper validation.
Solution: Used secure_filename and FileAllowed to restrict file types and ensure safe storage in app/static/uploads.


Challenge: Implementing session timeout without disrupting user experience.
Solution: Created a custom login_required_with_timeout decorator to check session age and log out users after 3 hours of inactivity.


Challenge: Designing a responsive and visually appealing UI.
Solution: Combined Bootstrap 5.3 with custom CSS (Orbitron font, glow effects) for a futuristic, user-friendly interface.



Screenshots

Home Page: Displays a searchable list of games with purchase options.
Chatbot Interface: Interactive AI chatbot for game queries.
Developer Dashboard: Allows developers to manage their games.
Admin Dashboard: Shows recent purchases and user management options.
User Library: Displays purchased games for regular users.

Note: Replace screenshots/*.png with actual screenshot paths after capturing them.
AI Justification
The AI chatbot enhances the Game Store by providing an interactive way for users to get information about games without navigating the entire site. It leverages the OpenRouter API to process natural language queries, using a context of available games to deliver precise answers. For example, asking "What is the price of Game X?" results in a response with the exact price and description, improving user engagement and accessibility.
Future Improvements

Game Recommendations: Add a recommender system based on user purchase history.
Comment System: Allow users to leave reviews or ratings for games.
Chat History: Store chatbot conversation history in the database or session.
Pagination: Implement pagination for game listings to improve performance.
Advanced Search: Add filters for genre, price range, or developer.

Conclusion
The Game Store is a robust, secure, and feature-rich web application that meets all requirements of a full-stack Flask project with AI integration. It demonstrates proficiency in backend development, database management, frontend design, and AI implementation, making it a comprehensive showcase of modern web development skills.
