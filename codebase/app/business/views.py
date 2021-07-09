from flask import Blueprint, render_template, url_for, request, flash, redirect
from flask_login.utils import login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from werkzeug.utils import secure_filename
from app.models import User, Property
from app import db, mail, create_app
import time,os
import secrets

# Create Blueprint
business_admin_view = Blueprint('business_admin_view',
                            __name__,
                            static_folder='static',
                            template_folder='templates')



@business_admin_view.route('/', methods=['GET', 'POST'])
@login_required
def property_dashboard():
    # Check if user is admin!
    if current_user.businessAccount != 1:
        return redirect(url_for('main_view.index'))
    
    # list of properties listed / owned by the user.
    propertys = current_user.property
    # Get the images
    propertyImages = []
    for prop in propertys:
        propImages = prop.property_images.split('|')
        profilePic = propImages[0]
        propertyImages.append(profilePic)

    print(propertyImages)

    return render_template("business/dashboard.html",
                           propertys=propertys,
                           propertyImages=propertyImages)


@business_admin_view.route('/add/', methods=['GET', 'POST'])
@login_required
def add_property():
    # Check if user is admin!
    if current_user.businessAccount != 1:
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


@business_admin_view.route('/view/<property_id>', methods=['GET','POST'])
@login_required
def view_property(property_id):
    # Check if user is admin!
    if current_user.businessAccount != 1:
        return redirect(url_for('main_view.index'))
    
    #! property_id should be randomCharacters -> Tom Scott
    property = Property.query.filter_by(id=int(property_id)).first()
    owner = User.query.filter_by(id=property.property_owner).first()

    # Getting the image dirs
    propertyImages = property.property_images.split('|')
    
    if request.method == 'POST':
        # Edit Property Info
        propertyEditForm = request.form
        property.property_name = propertyEditForm["editPropertyName"]
        property.property_description = propertyEditForm["editPropertyDescription"].strip() # .strip() removes trailing spaces
        property.property_price = propertyEditForm["editPriceRange"]
        property.property_type = propertyEditForm["editPropertyType"]
        property.property_location = propertyEditForm["editPropertyLocation"]
        property.property_features = propertyEditForm["editPropertyMisc"]
        property.additionalContactInfo = propertyEditForm["editBusinessName"]

        #* Deal with the Images
        #? Pardon me for the somewhat terrible implementation of the image processing logic below. Especially for 
        #? the terribly confusing variable names
        if request.files != None:
            propertyProfileImage = request.files['editPropertyProfilePic'] # Main Image
            editPropertySecondaryImage1 = request.files['editPropertySecondaryImage1'] # Required Secondary Image
            #! I am thinking of not imposing restrictions on required vs optional images here. (Add Property??)
            #? Important Question: Also, what if a user wants to change one of the images and not all of them?
            editPropertySecondaryImage2 = request.files['editPropertySecondaryImage2'] # Optional Secondary Image
            editPropertySecondaryImage3 = request.files['editPropertySecondaryImage3'] # Optional Secondary Image
            # print(editPropertySecondaryImage1.filename)
            
            expectedImagesList = [propertyProfileImage,editPropertySecondaryImage1,editPropertySecondaryImage2,editPropertySecondaryImage3]

            propertyImagesCombined = ''
            for index,img in enumerate(expectedImagesList):
                property_images = ''
                #! SECURITY CHECK - Do not allow malicious uploads
                if img.filename:
                    #* 2. Ensure file extension is allowed. (Images only) -> As defined in config.py
                    # print(img.filename)
                    if allowed_image(img.filename):
                        # print(os.getcwd())
                        #* 3. Ensure the file itself isn't dangerous.
                        img_filename = secure_filename(img.filename)
                        # image = property/{property_type}/random_str_timestamp.extension
                        property_images = f'property/{property.property_type.lower()}/{secrets.token_hex(2)}{secrets.token_hex(3)}_{str(time.time()).split(".")[0]}.{img_filename.split(".")[-1].lower()}'
                        # print(img_filename)
                        # print(property_images)
                        #! Restrict Filesize
                        # Save the image
                        img.save(os.path.join(create_app().config["IMAGE_UPLOADS_PROPERTY"], property_images))

                    else:
                        error_message = "Please upload an image with accepted extension (.png, .jpeg, .jpg)"
                        flash(f"{error_message}")
                        print(error_message)
                        return redirect(url_for('business_admin_view.view_property',property_id=property.id))

                 # Format the Property Image string ('|' separated)
                
                else:
                    break

                propertyImagesCombined += f'{property_images}|'

                # if index == len(expectedImagesList)-1:
                #     propertyImagesCombined += f'{property_images}'
                # else:
                #     propertyImagesCombined += f'{property_images}|'

        # remove any empty fields
        propertyImagesCombinedList = [i for i in propertyImagesCombined.split('|') if i]
        propertyImagesCombinedString = ''
        for index,i in enumerate(propertyImagesCombinedList):
            if index != len(propertyImagesCombinedList)-1:
                propertyImagesCombinedString += f'{i}|'
            else:
                propertyImagesCombinedString += f'{i}'
        
        if len(propertyImagesCombinedString) > 10:
            #! Refer to Important Question above for more details; why this isn't a sustainable implementation.
            property.property_images = propertyImagesCombinedString
            print(propertyImagesCombinedString)

        # Edit Owner Info
        owner.first_name = propertyEditForm["editContactName"].split(" ")[0]
        owner.last_name = propertyEditForm["editContactName"].split(" ")[-1]
        owner.user_phone = propertyEditForm["editPhoneNumber"]
        owner.businessName = propertyEditForm["editBusinessName"]

        # print(owner.first_name,owner.last_name,property.property_type)

        # Save changes to Database
        db.session.commit()

        # redirect -> Refresh the page to reflect the changes
        return redirect(url_for('business_admin_view.view_property',property_id=property.id))

    return render_template("business/view.html",
                           property=property,
                           owner=owner,
                           propertyImages=propertyImages,)


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