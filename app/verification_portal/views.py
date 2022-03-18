import os
import time
import secrets
import cloudinary
import cloudinary.api
import cloudinary.uploader
from app import db, mail, create_app, aws_client
from app.send_mail_sms import send_mail
# from app.config import VERIFICATION_PATH, AWS_S3_BUCKET, ALLOWED_IMAGE_EXTENSIONS
from werkzeug.utils import secure_filename
from app.subscription_manager import subscription_manager
from flask_login.utils import login_required, logout_user
from app.models import Plans, User, Property, PropertyDocuments
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from flask import Blueprint, render_template, url_for, request, flash, redirect, Markup

# Create Blueprint
verification_portal_view = Blueprint('verification_portal_view',
                                __name__,
                                static_folder='static',
                                template_folder='templates')


@verification_portal_view.route('/', methods=['GET', 'POST'])
@login_required
def verification_dashboard():
    #! Check if user is nyupal admin!
    if current_user.businessAccount != 1:
        return redirect(url_for('main_view.index',page_num=1))

    #* list of property owners
    owners = User.query.filter_by(businessAccount=1).all()

    # list of properties listed / owned by the user.
    propertys = current_user.property
    print(f'propertys {propertys}')

    # business plan
    # userPlan = Plans.query.filter_by(id=current_user.businessPlan).first()

 
  
    # Get the images
    propertyImages = []
    for prop in propertys:
        propImages = prop.property_images.split('|')
        profilePic = propImages[0]
        propertyImages.append(profilePic)

    #! Check whether subscription has expired.
    sub_plan = current_user.businessPlan
    if not subscription_manager.validate:
        flash(Markup(f"Your Subscription has Expired. Please <b><a href='{url_for('finance_view.checkout',plan=sub_plan)}'>update subscription.</a></b>"))
    

    return render_template("verification_portal/verification_dashboard.html",
                           owners=owners,
    )

@verification_portal_view.route('/property/<owner_id>/', methods=['GET', 'POST'])
@login_required
def owner_property(owner_id):
    # Check if user is admin!
    if current_user.businessAccount != 1:
        return redirect(url_for('main_view.index',page_num=1))

    # propertyTypes = ["Residential", "Commercial", "Land"]
    # This will be used to display and Ad on the Add-Property Page
    bannerAd = url_for('static', filename='icons/banner.jpg')

    propertys = Property.query.filter_by(property_owner=owner_id).all()



    return render_template("verification_portal/owner_property.html",
                           bannerAd=bannerAd,
                           propertys=propertys,
                           owner_id=owner_id)


@verification_portal_view.route('/view/<property_id>', methods=['GET', 'POST'])
@login_required
def verification_status(property_id):
    # Check if user is admin!
    if current_user.businessAccount != 1:
        return redirect(url_for('main_view.index',page_num=1))

    #! property_id should be randomCharacters -> Tom Scott
    property = Property.query.filter_by(id=int(property_id)).first()
    owner = User.query.filter_by(id=property.property_owner).first()

    # Getting the image dirs
    propertyImages = property.property_images.split('|')

    #? Verification Status and Text => DB.Json Column?
    verification_dict = {
        0:('btn-warning','verification pending','We are currently working on getting your property verified.'),
        1:('btn-success','verified','Your property has been successfully verified!'),
        2:('btn-danger','verification failed','Your property does not meet requirements for verification. Contact us for more info.'),
        3:('btn-danger','verification flagged','Your property does not meet requirements for verification. Contact us for more info.'),
    }

    if request.method == 'POST':
        # Edit Property Info
        propertyEditForm = request.form
        print(propertyEditForm)
        # property.property_name = propertyEditForm["editPropertyName"]
        # # .strip() removes trailing spaces

        # owner.first_name = propertyEditForm["editContactName"].split(" ")[0]
        # #? EdgeCase: User has firstname only. e.g. Google? -> Far-fetched? Maybe. Possible? Yes.
        # owner.last_name = propertyEditForm["editContactName"].split(" ")[-1] if propertyEditForm["editContactName"].split(" ")[-1] else ''
        # owner.user_phone = propertyEditForm["editPhoneNumber"]
 
        # # Save changes to Database
        # db.session.commit()

        # redirect -> Refresh the page to reflect the changes
        return redirect(url_for('verification_portal_view.view_property', property_id=property.id))

    return render_template("verification_portal/verification_status.html",
                           property=property,
                           owner=owner,
                           propertyImages=propertyImages,
                           verification_dict=verification_dict)


