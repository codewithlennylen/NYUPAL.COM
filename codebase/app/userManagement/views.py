from flask import Blueprint, render_template, url_for, request, flash, redirect
from app.models import User
from app import db


# Create Blueprint
login_view = Blueprint('login_view',
                            __name__,
                            static_folder='static',
                            template_folder='templates')

@login_view.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_form = request.form
        login_email = login_form['loginEmail']
        login_pwd = login_form['loginPassword']
        login_remember = login_form['loginRemember']

        user = User.query.filter_by(user_email=login_email).first()

    return render_template("userManagement/login.html")


@login_view.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        register_form = request.form
        register_fname = register_form['registerFirst']
        register_lname = register_form['registerLast']
        register_email = register_form['registerEmail']
        register_pwd = register_form['registerPassword']
        register_confirmPwd = register_form['registerConfirmPassword']
        register_updates = register_form['registerUpdates']

        #* USER VALIDATION
        # Ensure email is unique
        emailsInDB = User.query.query.filter_by(user_email=register_email).first()
        if emailsInDB:
            error = "This Account Already Exists. Log in instead."

        # Ensure Passwords Match
        if register_pwd != register_confirmPwd:
            error = "The passwords do not match. Please Try Again."

        #* Edgecase-Failed: Redirect to register page for user to try again
        if error:
            flash(
                f"Registration Failed:  {error}")
            return redirect(url_for('login_view.register'))

        # Newsletter Subscriptions?
        if register_updates:
            register_updates = 1
        
        new_user = User(
            first_name=register_fname,
            last_name=register_lname,
            user_email=register_email,
            user_pword=register_pwd,
            user_updates=register_updates
        )

        try:
            # Try adding user object to database.
            db.session.add(new_user)
            db.session.commit()

            flash(
                f"Your Account was Successfully Created. Proceed to Login")
            return redirect(url_for('login_view.login'))
        except Exception as e:
            # Log this SERIOUS issue > Report to Developer
            error = e
            print(error)





    return render_template("userManagement/register.html")
