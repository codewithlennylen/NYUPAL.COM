from flask import Blueprint, render_template, url_for, request, flash, redirect
from flask_login.utils import login_required, logout_user
from flask_login import login_user, logout_user, login_required, current_user

from app.models import Property, User
from app import db, mail
import random


# Create Blueprint
more_info_view = Blueprint('more_info_view',
                            __name__,
                            static_folder='static',
                            template_folder='templates')

@more_info_view.route('/property/<property_id>', methods=['GET', 'POST'])
def more_info(property_id):
    #! property_id should be randomCharacters -> Tom Scott
    property = Property.query.filter_by(id=int(property_id)).first()
    owner = User.query.filter_by(id=property.property_owner).first()

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


