from flask import Blueprint, render_template, url_for, request, flash, redirect
from flask_login.utils import login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from werkzeug.utils import secure_filename
from app.models import User, Property, Plans
from app import db, mail, create_app
import time
import os
import secrets

# Create Blueprint
messenger_view = Blueprint('messenger_view',
                                __name__,
                                static_folder='static',
                                template_folder='templates')


def send_email(owner,message):
    msg = Message('Nyupal Message Alert',  # Title for the E-mail
					sender=f'{current_user.user_email}',
					recipients=[owner.user_email])
    msg.body = f'''You have a new Message from a Prospective Client:

{message}

Nyupal 2021
'''

    mail.send(msg)
    print("email sent")



@messenger_view.route('/send_message/<propertyId>', methods=['POST'])
@login_required
def send_message(propertyId):

    # Get message from form
    messageForm = request.form
    message = messageForm['msgText'].strip()

    # Input Validation
    error=""
    if len(message) == 0:
        error = "You Cannot Send a Blank Email Message!"
        
    # Get necessary info from DB
    property = Property.query.filter_by(id=int(propertyId)).first()
    owner = User.query.filter_by(id=property.property_owner).first()

    if error:
        flash(error)
        return redirect(url_for('more_info_view.more_info',property_id=propertyId))
    
    # Send Message
    send_email(owner,message)
    flash("Message Sent Successfully")
    return redirect(url_for('more_info_view.more_info',property_id=propertyId))


@messenger_view.route('/send_nyupal_message', methods=['POST'])
@login_required
def send_nyupal_message():


    flash("Message Sent Successfully")
    return redirect(url_for('main_view.index',page_num=1))

