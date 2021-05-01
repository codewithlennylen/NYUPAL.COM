from flask import Blueprint
from flask import render_template

# Create Blueprint
main_view = Blueprint('main_view', __name__)

@main_view.route('/')
def index():
    return render_template("index.html")