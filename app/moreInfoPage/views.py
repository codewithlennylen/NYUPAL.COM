from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user
from app.models import Property, User
from app.send_mail_sms import send_mail
from app import db, mail
import random


# Create Blueprint
more_info_view = Blueprint('more_info_view',
                            __name__,
                            static_folder='static',
                            template_folder='templates')

#! Should this route accept POST Requests?
@more_info_view.route('/property/<property_id>', methods=['GET', 'POST'])
def more_info(property_id):
    #! property_id should be randomCharacters -> Tom Scott
    property = Property.query.filter_by(id=int(property_id)).first()
    owner = User.query.filter_by(id=property.property_owner).first()
    print(owner)

    if request.method == 'POST':
        contact_form = request.form
        # ! Take mail info direct from db? Can the frontend be hacked? 
        #? nvm; it's disabled
        # contact_email = contact_form['recipient_mail'].strip()
        client_message = contact_form['msgText'].strip()

        if not client_message:
            flash("You cannot send an empty message ⚠️")
            return redirect(url_for('more_info_view.more_info',property_id=property_id))

        #* send mail to property owner.
        subject = 'Nyupal Message Alert'
        recipients=[owner.user_email]
        # recipients = contact_email
        #! forbidden for now. We'll use default email (registered to sendgrid)
        # sender=f'{current_user.user_email}'
        # print(f"sender: {sender}")
        body = f'''
                    <p>You have a new Message from a Prospective Client:</p>
                    <br>
                    {client_message}

                    <p>Nyupal 2022</p>
                '''

        send_mail(recipients, subject,body)
        if send_mail:
            print("email sent ✔️")
            flash("Your Message has been sent ✔️")
        else:
            print("email failed ⚠️")
            flash("Your Message has not been sent ❎")

    
        

    similarProperty = Property.query.all()[:3]

    # Getting the image dirs
    propertyImages = property.property_images.split('|')
    similarPropertyImages = []
    for propty in similarProperty:
        images = propty.property_images.split('|')
        profilePic = images[0] # get the primary image (property_profile_pic)
        similarPropertyImages.append(profilePic) 

    print(propertyImages)
    print("\n")
    print(similarPropertyImages)

    if request.method == 'POST':
       pass

    return render_template("moreInfoPage/moreInfoPage.html",
                           property=property,
                           owner=owner,
                           similarProperty=similarProperty,
                           propertyImages=propertyImages,
                           similarPropertyImages=similarPropertyImages,)


# @more_info_view.route('/profile/', methods=['GET','POST'])
# def profile():
#     return render_template("userManagement/profile.html")


