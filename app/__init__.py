from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()

# Define app object > Application Factory Pattern.
def create_app():
    # Instantiate Flask Object
    app = Flask(__name__)
    app.config.from_pyfile('config.py')


    # initialize extensions
    db.init_app(app) # links to the database
    migrate.init_app(app, db) # Enables Database-Migrations
    mail.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth_login_view.login'
    login_manager.init_app(app)


    # Import and register Blueprints
    from .views import main_view
    from .userManagement.views import auth_login_view
    from .moreInfoPage.views import more_info_view
    from .business.views import business_admin_view
    from .finance.views import finance_view
    from .messenger.views import messenger_view

    # app.register_blueprint(main_view, url_prefix="/index/")
    app.register_blueprint(main_view)
    app.register_blueprint(auth_login_view, url_prefix="/user/")
    app.register_blueprint(more_info_view, url_prefix="/more_info/")
    app.register_blueprint(business_admin_view, url_prefix="/property_page/")
    app.register_blueprint(finance_view, url_prefix="/upgrade_account/")
    app.register_blueprint(messenger_view, url_prefix="/messenger/")

    # Make database accessible from app_context.
    from app import models

    #user-loader -> Flask-login specific
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))


    return app