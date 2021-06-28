from flask import Blueprint
from flask import render_template
from app.models import Property

# Create Blueprint
main_view = Blueprint('main_view', __name__)

@main_view.route('/')
def index():
    propertys = Property.query.all()
    return render_template("index.html",propertys=propertys)