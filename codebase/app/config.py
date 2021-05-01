import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env')) # When running the application.
# load_dotenv() # When using the dummy-database generators.

DEBUG = True
SQLALCHEMY_DATABASE_URI =  os.getenv("DATABASE_URI")
SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS")
SECRET_KEY = os.getenv("SECRET_KEY")