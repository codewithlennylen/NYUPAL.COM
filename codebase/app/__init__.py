from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
# from flask_mail import Mail

db = SQLAlchemy()
migrate = Migrate()


# login_manager = LoginManager(app)
# login_manager.login_view = 'login' # To make the login_required decorator work
# login_manager.login_message_category = 'info'

# Define app object > Application Factory Pattern.
def create_app():
    # Instantiate Flask Object
    app = Flask(__name__)
    app.config.from_pyfile('config.py')


    # initialize extensions
    db.init_app(app) # links to the database
    migrate.init_app(app, db) # Enables Database-Migrations


    # Import and register Blueprints
    from .views import main_view
    from .userManagement.views import auth_login_view

    app.register_blueprint(main_view)
    app.register_blueprint(auth_login_view, url_prefix="/user/")

    # Make database accessible from app_context.
    from app import models


    return app