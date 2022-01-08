from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, url_for, request, flash, redirect
from flask_login.utils import login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from werkzeug.utils import secure_filename
from app.models import User, Property, Plans, PaymentGateway, Subscription, Payment
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

    plans = Plans.query.order_by(Plans.plan_price).all()

    return render_template("finance/pricing_details.html", plans=plans)


#* This is a very sensitive route. Consider breaking it down?
@finance_view.route('/checkout/<plan>', methods=['GET', 'POST'])
@login_required
def checkout(plan):
    print(f"plan: {plan}")
    # Check if user is admin!
    #? Consider a regular user that wants to upgrade to a business plan.
    # if current_user.businessAccount != 1:
    #     return redirect(url_for('main_view.index'))

    #! Check for token to ensure user didn't skip document upload step.
    if int(plan) == 1 or int(plan) == 2 or int(plan) == 3:
        planDetails = Plans.query.filter_by(id=int(plan)).first()
    else:
        # Invalid URL
        return redirect(url_for('finance_view.pricing'))
 

    if request.method == 'POST':
        transactionForm = request.form
        transactionCode = transactionForm['transactionCode'].strip()
        
        # * INPUT VALIDATION
        error = ""
        if transactionCode == "" :
            error = "Please Enter the Transaction Code."
            flash(
                f"{error}")
            return redirect(url_for('finance_view.checkout', plan=plan))

        #
        payment_transaction = PaymentGateway.query.filter_by(transaction_id=transactionCode).first()
        if not payment_transaction:
            flash("We have not received your payment, please try again later.")
            return redirect(url_for('finance_view.checkout', plan=plan))
        
        #! EdgeCase: User inputs a previous transaction_code.
        #? Add is_used column, to confirm whether or not transaction_code has been used before.
        if payment_transaction.is_used:
            flash("That Transaction Code is Invalid")
            return redirect(url_for('finance_view.checkout', plan=plan))
        
        #! Confirm amount before proceeding. (amount_paid v. plan_price)
        #? specific to PaymentGateway

        #* Update Subscription
        # Subscription is valid for 30 days
        sub = Subscription(
            user_id=current_user.id,
            plan_id=planDetails.id,
            start_date=date.today(),
            end_date=date.today()+timedelta(days=30),
        )
        try:
            db.session.add(sub)
            db.session.commit()
        except Exception as e:
            #! log e
            print(f"Subscription_Error: {e}")
            flash("Failed. If Error Persists, Please Contact Nyupal")

        #* Finalize Payment
        pay = Payment(
            user_id=current_user.id,
            plan_id=planDetails.id,
            subscription_id=sub.id,
            payment_gateway_id=payment_transaction.id,
        )
        try:
            db.session.add(pay)
            db.session.commit()
        except Exception as e:
            #! log e
            print(f"Payment_Error: {e}")
            flash("Failed. If Error Persists, Please Contact Nyupal")


        #* Upgrade Account to Business, tier == plan
        user = User.query.filter_by(id=current_user.id).first()
        user.businessAccount = 1
        user.businessPlan = planDetails.id
        
        #* Consider transaction as complete, thus invalidate transaction_code
        payment_transaction.is_used = 1
        db.session.commit()

        #? Redirect to View-Property Page.
        flash("Congratulations! Your Account has been Upgraded.")
        flash("Use this Dashboard to manage Your Property.")
        return redirect(url_for('business_admin_view.property_dashboard'))


    return render_template("finance/checkout.html",
                            planDetails=planDetails)
