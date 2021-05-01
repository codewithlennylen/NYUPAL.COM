from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate


# db = SQLAlchemy()
# migrate = Migrate()

# Define app object > Application Factory Pattern.
def create_app():
    # Instantiate Flask Object
    app = Flask(__name__)
    app.config.from_pyfile('config.py')


    # initialize extensions
    # db.init_app(app) # links to the database
    # migrate.init_app(app, db) # Enables Database-Migrations


    # Import and register Blueprints
    from .views import main_view
    # from .admin_dashboard.views import admin_dashboard_view

    app.register_blueprint(main_view)
    # app.register_blueprint(admin_dashboard_view, url_prefix="/admin_dashboard/")

    # Make database accessible from app_context.
    # from app import models


    return app