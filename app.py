from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from dotenv import load_dotenv
import os

# Initialize extensions
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Load environment variables from .env file
    load_dotenv()

    # Configurations
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://your_username:your_password@localhost/your_database_name'
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

    # Import models and create database tables
    with app.app_context():
        from models import Product, Order  # Avoid circular import
        db.create_all()

    # Register routes
    from routes import order_bp
    app.register_blueprint(order_bp)

    return app
