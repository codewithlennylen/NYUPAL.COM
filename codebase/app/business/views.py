from flask import Blueprint, render_template, url_for, request, flash, redirect
from flask_login.utils import login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from app.models import User
from app import db, mail


# Create Blueprint
business_admin_view = Blueprint('business_admin_view',
                            __name__,
                            static_folder='static',
                            template_folder='templates')



@business_admin_view.route('/', methods=['GET', 'POST'])
@login_required
def property_dashboard():
    # Check if user is admin!
    if current_user.is_authenticated:
        return redirect(url_for('main_view.index'))

    if request.method == 'POST':
        login_form = request.form
        login_email = login_form['loginEmail']
        login_pwd = login_form['loginPassword']
        login_remember = True if request.form.get("loginRemember") else False

        #* INPUT VALIDATION
        error=""
        if login_email == "" or login_pwd == "":
            error="Please fill in all the fields."
            flash(
                f"{error}")
            return redirect(url_for('business_admin_view.login'))


        user = User.query.filter_by(user_email=login_email).first()

        # Check if user (email) exists
        if user:
            if check_password_hash(user.user_pword, login_pwd):
                # flash("Login Successful.")
                login_user(user,remember=login_remember)
                return redirect(url_for('main_view.index'))
            else:
                error = 'Login Failed. Please try again.'
        else:
            error= 'Login Failed. Do you have an account?'

        if error:
            flash(f"{error}")
            return redirect(url_for('business_admin_view.login'))

    return render_template("business/dashboard.html")


@business_admin_view.route('/add/', methods=['GET', 'POST'])
def add_property():
    # Check if user is admin!
    if current_user.is_authenticated:
        return redirect(url_for('main_view.index'))

    if request.method == 'POST':
        register_form = request.form
        register_fname = register_form['registerFirst']
        register_lname = register_form['registerLast']
        register_email = register_form['registerEmail']
        register_pwd = register_form['registerPassword']
        register_confirmPwd = register_form['registerConfirmPassword']
        register_updates = 1 if request.form.get("registerUpdates") else 0

        #* INPUT VALIDATION
        error=""
        if register_fname == "" or register_lname == "" or register_email == "" or register_pwd == "":
            error="Please fill in all the fields."
            flash(
                f"{error}")
            return redirect(url_for('business_admin_view.register'))

        #* USER VALIDATION
        
        # Ensure email is unique
        emailsInDB = User.query.filter_by(user_email=register_email).first()
        if emailsInDB:
            error = "This Account Already Exists. Log in instead."

        # Ensure Passwords Match
        if register_pwd != register_confirmPwd:
            error = "The passwords do not match. Please Try Again."

        #* Edgecase-Failed: Redirect to register page for user to try again
        if error:
            flash(
                f"{error}")
            return redirect(url_for('business_admin_view.register'))

        # Newsletter Subscriptions?
        # unnecessary logic due to the one liner used above (register_updates)
        if register_updates:
            pass
            # register_updates = 1
        
        new_user = User(
            first_name=register_fname,
            last_name=register_lname,
            user_email=register_email,
            user_pword=generate_password_hash(register_pwd,method='sha256'),
            user_updates=register_updates
        )

        try:
            # Try adding user object to database.
            db.session.add(new_user)
            db.session.commit()

            flash(
                f"Your Account was Successfully Created. Proceed to Login")
            return redirect(url_for('business_admin_view.login'))
        except Exception as e:
            # Log this SERIOUS issue > Report to Developer
            error = e
            print(error)





    return render_template("business/add.html")


@business_admin_view.route('/view/', methods=['GET','POST'])
@login_required
def view_property():
    # Check if user is admin!
    if current_user.is_authenticated:
        return redirect(url_for('main_view.index'))

    return render_template("business/view.html")