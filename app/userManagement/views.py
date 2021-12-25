import os
import secrets
import time
from flask import Blueprint, render_template, url_for, request, flash, redirect
from flask_login.utils import login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from werkzeug.utils import secure_filename
from app.models import User, Plans
from app import db, mail, create_app


# Create Blueprint
auth_login_view = Blueprint('auth_login_view',
                            __name__,
                            static_folder='static',
                            template_folder='templates')

@auth_login_view.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main_view.index',page_num=1))

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
            return redirect(url_for('auth_login_view.login'))


        user = User.query.filter_by(user_email=login_email).first()

        # Check if user (email) exists
        if user:
            if check_password_hash(user.user_pword, login_pwd):
                # flash("Login Successful.")
                login_user(user,remember=login_remember)
                return redirect(url_for('main_view.index',page_num=1))
            else:
                error = 'Login Failed. Please try again.'
        else:
            error= 'Login Failed. Do you have an account?'

        if error:
            flash(f"{error}")
            return redirect(url_for('auth_login_view.login'))

    return render_template("userManagement/login.html")


@auth_login_view.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main_view.index',page_num=1))

    if request.method == 'POST':
        register_form = request.form
        register_fname = register_form['registerFirst']
        register_lname = register_form['registerLast']
        register_email = register_form['registerEmail']
        register_pwd = register_form['registerPassword']
        register_confirmPwd = register_form['registerConfirmPassword']
        register_updates = 1 #if request.form.get("registerUpdates") else 0

        #* INPUT VALIDATION
        error=""
        if register_fname == "" or register_lname == "" or register_email == "" or register_pwd == "":
            error="Please fill in all the fields."
            flash(
                f"{error}")
            return redirect(url_for('auth_login_view.register'))

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
            return redirect(url_for('auth_login_view.register'))

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
            return redirect(url_for('auth_login_view.login'))
        except Exception as e:
            # Log this SERIOUS issue > Report to Developer
            error = e
            print(error)





    return render_template("userManagement/register.html")

@auth_login_view.route('/register_business/', methods=['GET', 'POST'])
def register_business():
    """Registers a business account. A business account can list and thus sell property
    on the platform
    """
    default_business_plan = int(Plans.query.filter_by(plan_name='Standard Business Account').first().id)
    print(f"default_business_plan: {default_business_plan}")
    if current_user.is_authenticated:
        return redirect(url_for('main_view.index',page_num=1))

    if request.method == 'POST':
        register_form = request.form
        register_fname = register_form['registerBusinessFirst']
        register_lname = register_form['registerBusinessLast']
        register_email = register_form['registerBusinessEmail']
        register_pwd = register_form['registerBusinessPassword']
        register_confirmPwd = register_form['registerBusinessConfirmPassword']
        register_updates = 1 if request.form.get("registerBusinessUpdates") else 0

        # This is the only difference between a regular user and a seller / property owner
        businessAccount = 1 # Admin-ish feature
        businessName = register_form['registerBusinessName']

        #* INPUT VALIDATION
        error=""
        if register_fname == "" or register_lname == "" or register_email == "" or register_pwd == "":
            error="Please fill in all the required fields."
            flash(
                f"{error}")
            return redirect(url_for('auth_login_view.register'))

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
            return redirect(url_for('auth_login_view.register'))

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
            user_updates=register_updates,
            businessAccount = businessAccount,
            businessName = businessName,
            businessPlan=default_business_plan
        )

        try:
            # Try adding user object to database.
            db.session.add(new_user)
            db.session.commit()

            flash(
                f"Your Account was Successfully Created. Proceed to Login")
            return redirect(url_for('auth_login_view.login'))
        except Exception as e:
            # Log this SERIOUS issue > Report to Developer
            error = e
            print(error)

    return render_template("userManagement/register_business.html")


@auth_login_view.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main_view.index',page_num=1))


@auth_login_view.route('/profile/', methods=['GET','POST'])
@login_required
def profile():
    accountType = current_user.businessAccount
    plan = None
    # Check if user is on business account; then get the business plan (tier)
    if accountType == 1:
        businessPlanID = current_user.businessPlan
        plan = Plans.query.filter_by(id=businessPlanID).first()
        print(plan)

    # Nyupal Contact
    nyupalContact = {
        'businessName':"Nyupal",
        "businessEmail":"support@nyupal.com",
        "businessPhone":"+254712345678",
    }

    if request.method == 'POST':
        editProfileForm = request.form
        profileFirst = editProfileForm['profileFirst']
        profileLast = editProfileForm['profileLast']
        profileEmail = editProfileForm['profileEmail']
        profilePhone = editProfileForm['profilePhone']

        # Not all Accounts are Business Accounts thus this field is optional.
        profileBusinessName = editProfileForm.get('profileBusinessName')

        # * INPUT VALIDATION
        error = ""
        if profileFirst == "" or profileLast == "" or profileEmail == "" or profilePhone == "" :
            error = "Please fill in all the Required Fields."
            flash(
                f"{error}")
            return redirect(url_for('auth_login_view.profile'))

        #! IMAGE PROCESSING, MORE OR LESS
        profile_image=''
        profile_image_name = None
        if request.files != None:
            # Main Image
            editProfilePic = request.files['profilePic']
            #! SECURITY CHECK - Do not allow malicious uploads
            if editProfilePic.filename:
                # * 2. Ensure file extension is allowed. (Images only) -> As defined in config.py
                if allowed_image(editProfilePic.filename):
                    # print(os.getcwd())
                    # * 3. Ensure the file itself isn't dangerous.
                    editProfilePic_filename = secure_filename(editProfilePic.filename)
                    # image = property/{property_type}/random_str_timestamp.extension
                    profile_image_name = f'{secrets.token_hex(2)}{secrets.token_hex(3)}_{str(time.time()).split(".")[0]}.{editProfilePic_filename.split(".")[-1].lower()}'
                    profile_image = f'userManagement/users/{profile_image_name}'
                    # print(editProfilePic_filename)
                    #! Restrict Filesize
                    # ? By default Flask throws a HTTP 413 error if MAX_CONTENT_LENGTH is exceeded.
                    # Save the image
                    editProfilePic.save(os.path.join(
                        create_app().config["IMAGE_UPLOADS_USER"], profile_image))

                else:
                    error_message = "Please upload an image with accepted extension (.png, .jpeg, .jpg)"
                    flash(f"{error_message}")
                    print(error_message)
                    return redirect(url_for('auth_login_view.profile'))

        user = User.query.filter_by(id=current_user.id).first()

        try:
            user.first_name = profileFirst
            user.last_name = profileLast
            user.user_email = profileEmail
            user.user_phone = profilePhone
            user.businessName = profileBusinessName if profileBusinessName else None
            user.user_pic = profile_image_name if profile_image_name else user.user_pic
            
            # Write changes to DB
            db.session.commit()

            flash("Your Profile Has Been Updated Successfully.")
            return redirect(url_for('auth_login_view.profile'))
        except Exception as e:
            flash("An Error Ocurred: Changes Not Saved!")
            print(f"Error: {e}")
            return redirect(url_for('auth_login_view.profile'))


    return render_template("userManagement/profile.html",
                           plan=plan,
                           owner=nyupalContact)



def send_reset_email(user):
	token = user.get_reset_token()
	msg = Message('Nyupal Password Reset',  # Title for the E-mail
					sender='noreply@nyupal.com',
					recipients=[user.user_email])
	msg.body = f''' To reset your password, visit the following link:
{url_for('auth_login_view.reset_token', token=token, _external=True)}

If you did not make this request, simply ignore this email and no changes will be made.
Please DO NOT REPLY to this email.
'''
	mail.send(msg)


@auth_login_view.route("/reset_password/", methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main_view.index',page_num=1))
    
    if request.method == 'POST':
        reset_form = request.form
        reset_email = reset_form['resetEmail']
	
        user = User.query.filter_by(user_email=reset_email).first()
        if user:
            #! Bypassing email for now
            # send_reset_email(user)
            # flash('An email has been sent with instructions to reset your password.')
            token = user.get_reset_token()
            return redirect(url_for('auth_login_view.reset_token', token=token))
        else:
            flash("That Email does not exist. Check the spelling & Try Again.")
            return redirect(url_for('auth_login_view.reset_request'))
        

    return render_template('userManagement/reset_request.html')


@auth_login_view.route("/reset_password/<token>", methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main_view.index',page_num=1))

    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an Invalid or Expired Token')
        return redirect(url_for('auth_login_view.reset_request'))

    if request.method == 'POST':
        reset_form = request.form
        reset_pwd = reset_form['resetPassword']
        reset_confirmPwd = reset_form['resetConfirmPassword']

        #* INPUT VALIDATION
        error=""
        if reset_pwd == "" or reset_confirmPwd == "":
            error="Please fill in all the fields."
            flash(
                f"{error}")
            return redirect(url_for('auth_login_view.reset_token',token=token))

        # Ensure Passwords Match
        if reset_pwd != reset_confirmPwd:
            error = "The passwords do not match. Please Try Again."
            flash(
                f"{error}")
            return redirect(url_for('auth_login_view.reset_token',token=token))
        
        # Generate hash from the pword and update db
        hashed_pwd = generate_password_hash(reset_pwd,method='sha256')
        user.user_pword = hashed_pwd
        db.session.commit()

        flash("Your Password Has Been Updated! You are now able to Log In")
        return redirect(url_for('auth_login_view.login'))
    
    return render_template('userManagement/reset_pword.html')



def allowed_image(filename):

    # We only want files with a . in the filename
    if not "." in filename:
        return False

    # Split the extension from the filename
    ext = filename.rsplit(".", 1)[1]

    # Check if the extension is in ALLOWED_IMAGE_EXTENSIONS
    if ext.upper() in create_app().config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False
