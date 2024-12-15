from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from dotenv import load_dotenv
import os
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # Add JWT Secret Key
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    jwt = JWTManager(app)

    # Load environment variables from .env file
    load_dotenv()

    # Configurations
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Flask-Mail Configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # SMTP server (change if you're using a different provider)
    app.config['MAIL_PORT'] = 465  # SSL port for Gmail
    app.config['MAIL_USE_SSL'] = True  # Use SSL
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')  # Your email
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  # App-specific password or your Gmail password
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')  # Set default sender to your email address

    # Initialize Flask-Mail
    mail = Mail(app)

    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    # Import models and create database tables
    with app.app_context():
        from models import Product, Order  # Avoid circular import
        db.create_all()

    # Register routes
    from auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    from routes import order_bp
    app.register_blueprint(order_bp, url_prefix='/orders')  # Set prefix if necessary

    return app
