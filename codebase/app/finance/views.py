from flask import Blueprint, render_template, url_for, request, flash, redirect
from flask_login.utils import login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from werkzeug.utils import secure_filename
from app.models import User, Property
from app import db, mail, create_app
import time
import os
import secrets

# Create Blueprint
finance_view = Blueprint('finance_view',
                                __name__,
                                static_folder='static',
                                template_folder='templates')


@finance_view.route('/pricing/', methods=['GET', 'POST'])
# EdgeCase: A regular user wants to checkout the prices for curiosity purposes?
#// @login_required
def pricing():
    # Check if user is admin! -> Not necessary. Pricing is free for the public.
    #// if current_user.businessAccount != 1:
    #//     return redirect(url_for('main_view.index'))

    return render_template("finance/pricing_details.html")


@finance_view.route('/checkout/', methods=['GET', 'POST'])
@login_required
def checkout():
    # Check if user is admin!
    # if current_user.businessAccount != 1:
    #     return redirect(url_for('main_view.index'))

    # propertyTypes = ["Residential", "Commercial", "Land"]
    # # This will be used to display and Ad on the Add-Property Page
    # bannerAd = url_for('static', filename='icons/banner.jpg')

    # if request.method == 'POST':
    #     registerProperty_form = request.form
    #     newPropertyName = registerProperty_form['newPropertyName']
        
    #     # * INPUT VALIDATION
    #     error = ""
    #     if newPropertyName == "" or newPropertyDescription == "" or newPropertyType not in propertyTypes or newPriceRange == "" or newPropertyLocation == "" or newContactName == "" or newPhoneNumber == "":
    #         error = "Please fill in all the Required Fields."
    #         flash(
    #             f"{error}")
    #         return redirect(url_for('finance_view.add_property'))


    #     new_property = Property(
    #         property_name=newPropertyName,
    #     )

    #     print(new_property.property_name,new_property.property_price,new_property.property_images,new_property.property_owner,)
        
    #     try:
    #         # Try adding property object to database.
    #         db.session.add(new_property)
    #         db.session.commit()

    #         flash(
    #             f"Your Property was Successfully Listed.")
    #         return redirect(url_for('finance_view.property_dashboard'))
    #     except Exception as e:
    #         # Log this SERIOUS issue > Report to Developer
    #         error = e
    #         print(error)

    return render_template("business/checkout.html")
