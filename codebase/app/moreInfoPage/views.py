from flask import Blueprint, render_template, url_for, request, flash, redirect
from flask_login.utils import login_required, logout_user
from flask_login import login_user, logout_user, login_required, current_user

from app.models import User
from app import db, mail


# Create Blueprint
more_info_view = Blueprint('more_info_view',
                            __name__,
                            static_folder='static',
                            template_folder='templates')

@more_info_view.route('/', methods=['GET', 'POST'])
def more_info():
    
    if request.method == 'POST':
       pass

    return render_template("moreInfoPage/moreInfoPage.html")


# @more_info_view.route('/profile/', methods=['GET','POST'])
# def profile():
#     return render_template("userManagement/profile.html")


