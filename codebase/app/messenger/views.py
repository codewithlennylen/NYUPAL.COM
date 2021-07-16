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


@finance_view.route('/checkout/<plan>', methods=['GET', 'POST'])
@login_required
def checkout(plan):
    print(plan)
    # Check if user is admin!
    # if current_user.businessAccount != 1:
    #     return redirect(url_for('main_view.index'))

    if plan == "standard":
        planDetails = Plans.query.filter_by(plan_name="Standard Business Account").first()
    elif plan == "verified":
        planDetails = Plans.query.filter_by(plan_name="Verified Business Account").first()
    elif plan == "premium":
        planDetails = Plans.query.filter_by(plan_name="Premium Business Account").first()
    else:
        # Invalid URL
        return redirect(url_for('finance_view.pricing'))



    if request.method == 'POST':
        transactionForm = request.form
        transactionCode = transactionForm['transactionCode']
        
        # * INPUT VALIDATION
        error = ""
        if transactionCode == "" :
            error = "Please Enter the Transaction Code."
            flash(
                f"{error}")
            return redirect(url_for('finance_view.checkout', plan=plan))

        #! Verify & Record Transaction 
    #     new_property = Property(
    #         property_name=newPropertyName,
    #     )

    #     print(new_property.property_name,new_property.property_price,new_property.property_images,new_property.property_owner,)
        
    #     try:
    #         # Try adding property object to database.
    #         db.session.add(new_property)
    #         db.session.commit()
        #? Upgrade Account to Business, tier == plan
        user = User.query.filter_by(id=current_user.id).first()
        user.businessAccount = 1
        user.businessPlan = planDetails.id
        db.session.commit()

        #? Redirect to View-Property Page.
        flash("Congratulations! Your Account has been Upgraded.")
        flash("You can Manage Your property in this Dashboard made Just for You.")
        return redirect(url_for('business_admin_view.property_dashboard'))


    return render_template("finance/checkout.html",
                            planDetails=planDetails)
