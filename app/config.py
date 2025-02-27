import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env')) # When running the application.
# load_dotenv() # When using the dummy-database generators.

# Image Dirs
IMAGE_UPLOADS_USER = "./app/userManagement/static"
IMAGE_UPLOADS_PROPERTY = "./app/static"
ALLOWED_IMAGE_EXTENSIONS = ["JPEG", "JPG", "PNG", "GIF"]
MAX_CONTENT_LENGTH = 10 * 1024 * 1024 # Max-filesize set at 10MB. Otherwise throws HTTP 413 error

DEBUG = True
SQLALCHEMY_DATABASE_URI =  os.getenv("DATABASE_URI")
SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS")
SECRET_KEY = os.getenv("SECRET_KEY")

MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_PORT = os.getenv("MAIL_PORT")
MAIL_USE_TLS = os.getenv("MAIL_USE_TLS")
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")