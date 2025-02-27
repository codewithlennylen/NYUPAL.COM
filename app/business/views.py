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
business_admin_view = Blueprint('business_admin_view',
                                __name__,
                                static_folder='static',
                                template_folder='templates')


@business_admin_view.route('/', methods=['GET', 'POST'])
@login_required
def property_dashboard():
    # Check if user is admin!
    if current_user.businessAccount != 1:
        return redirect(url_for('main_view.index',page_num=1))

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
        return redirect(url_for('main_view.index',page_num=1))

    propertyTypes = ["Residential", "Commercial", "Land"]
    # This will be used to display and Ad on the Add-Property Page
    bannerAd = url_for('static', filename='icons/banner.jpg')

    if request.method == 'POST':
        registerProperty_form = request.form
        newPropertyName = registerProperty_form['newPropertyName']
        newPropertyDescription = registerProperty_form['newPropertyDescription'].strip()
        newPropertyType = registerProperty_form['newPropertyType']
        newPriceRange = registerProperty_form['newPriceRange']
        newPropertyLocation = registerProperty_form['newPropertyLocation']
        newPropertyMisc = registerProperty_form['newPropertyMisc']
        newContactName = registerProperty_form['newContactName']
        newPhoneNumber = registerProperty_form['newPhoneNumber']
        newBusinessName = registerProperty_form['newBusinessName']

        # * INPUT VALIDATION
        error = ""
        if newPropertyName == "" or newPropertyDescription == "" or newPropertyType not in propertyTypes or newPriceRange == "" or newPropertyLocation == "" or newContactName == "" or newPhoneNumber == "":
            error = "Please fill in all the Required Fields."
            flash(
                f"{error}")
            return redirect(url_for('business_admin_view.add_property'))

        #! IMAGE PROCESSING, MORE OR LESS
        if request.files != None:
            # Main Image
            propertyProfilePic = request.files['addPropertyProfilePic']
            # Required Secondary Image
            propertySecondaryImage1 = request.files['addPropertySecondaryImage1']
            #! I am thinking of not imposing restrictions on required vs optional images here. (Add Property??)
            # ? Important Question: Also, what if a user wants to change one of the images and not all of them?
            # Optional Secondary Image
            propertySecondaryImage2 = request.files['addPropertySecondaryImage2']
            # Optional Secondary Image
            propertySecondaryImage3 = request.files['addPropertySecondaryImage3']
            # print(editPropertySecondaryImage1.filename)

            expectedImagesList = [propertyProfilePic, propertySecondaryImage1,
                                  propertySecondaryImage2, propertySecondaryImage3]

            propertyImagesCombined = ''
            for index, img in enumerate(expectedImagesList):
                property_images = ''
                #! SECURITY CHECK - Do not allow malicious uploads
                if img.filename:
                    # * 2. Ensure file extension is allowed. (Images only) -> As defined in config.py
                    # print(img.filename)
                    if allowed_image(img.filename):
                        # print(os.getcwd())
                        # * 3. Ensure the file itself isn't dangerous.
                        img_filename = secure_filename(img.filename)
                        # image = property/{property_type}/random_str_timestamp.extension
                        property_images = f'property/{newPropertyType.lower()}/{secrets.token_hex(2)}{secrets.token_hex(3)}_{str(time.time()).split(".")[0]}.{img_filename.split(".")[-1].lower()}'
                        # print(img_filename)
                        # print(property_images)
                        #! Restrict Filesize
                        # ? By default Flask throws a HTTP 413 error if MAX_CONTENT_LENGTH is exceeded.
                        # Save the image
                        img.save(os.path.join(
                            create_app().config["IMAGE_UPLOADS_PROPERTY"], property_images))

                    else:
                        error_message = "Please upload an image with accepted extension (.png, .jpeg, .jpg)"
                        flash(f"{error_message}")
                        print(error_message)
                        return redirect(url_for('business_admin_view.add_property', property_id=property.id))

                 # Format the Property Image string ('|' separated)

                else:
                    break

                propertyImagesCombined += f'{property_images}|'

                # if index == len(expectedImagesList)-1:
                #     propertyImagesCombined += f'{property_images}'
                # else:
                #     propertyImagesCombined += f'{property_images}|'

        # * 'Filtration' Process
        # remove any empty fields
        propertyImagesCombinedList = [
            i for i in propertyImagesCombined.split('|') if i]
        propertyImagesCombinedString = ''
        for index, i in enumerate(propertyImagesCombinedList):
            if index != len(propertyImagesCombinedList)-1:
                propertyImagesCombinedString += f'{i}|'
            else:
                propertyImagesCombinedString += f'{i}'

        if not len(propertyImagesCombinedString) > 10:
            #! Refer to Important Question above for more details; why this isn't a sustainable implementation.
            # property.property_images = propertyImagesCombinedString
            # print(propertyImagesCombinedString)
            error = "Please Upload The Required Images."
            flash(
                f"{error}")
            return redirect(url_for('business_admin_view.add_property'))

        new_property = Property(
            property_name=newPropertyName,
            property_description=newPropertyDescription,
            property_price=newPriceRange,
            property_type=newPropertyType,
            property_location=newPropertyLocation,
            property_images=propertyImagesCombinedString,
            property_features=newPropertyMisc,
            property_owner=current_user.id,
            additionalContactInfo=newBusinessName
        )

        print(new_property.property_name,new_property.property_price,new_property.property_images,new_property.property_owner,)
        
        try:
            # Try adding property object to database.
            db.session.add(new_property)
            db.session.commit()

            flash(
                f"Your Property was Successfully Listed.")
            return redirect(url_for('business_admin_view.property_dashboard'))
        except Exception as e:
            # Log this SERIOUS issue > Report to Developer
            error = e
            print(error)

    return render_template("business/add.html",
                           propertyTypes=propertyTypes,
                           bannerAd=bannerAd)


@business_admin_view.route('/view/<property_id>', methods=['GET', 'POST'])
@login_required
def view_property(property_id):
    # Check if user is admin!
    if current_user.businessAccount != 1:
        return redirect(url_for('main_view.index',page_num=1))

    #! property_id should be randomCharacters -> Tom Scott
    property = Property.query.filter_by(id=int(property_id)).first()
    owner = User.query.filter_by(id=property.property_owner).first()

    # Getting the image dirs
    propertyImages = property.property_images.split('|')

    if request.method == 'POST':
        # Edit Property Info
        propertyEditForm = request.form
        property.property_name = propertyEditForm["editPropertyName"]
        # .strip() removes trailing spaces
        property.property_description = propertyEditForm["editPropertyDescription"].strip(
        )
        property.property_price = propertyEditForm["editPriceRange"]
        property.property_type = propertyEditForm["editPropertyType"]
        property.property_location = propertyEditForm["editPropertyLocation"]
        property.property_features = propertyEditForm["editPropertyMisc"]
        property.additionalContactInfo = propertyEditForm["editBusinessName"]

        # * Deal with the Images
        # ? Pardon me for the somewhat terrible implementation of the image processing logic below. Especially for
        # ? the terribly confusing variable names
        if request.files != None:
            # Main Image
            propertyProfileImage = request.files['editPropertyProfilePic']
            # Required Secondary Image
            editPropertySecondaryImage1 = request.files['editPropertySecondaryImage1']
            #! I am thinking of not imposing restrictions on required vs optional images here. (Add Property??)
            # ? Important Question: Also, what if a user wants to change one of the images and not all of them?
            # Optional Secondary Image
            editPropertySecondaryImage2 = request.files['editPropertySecondaryImage2']
            # Optional Secondary Image
            editPropertySecondaryImage3 = request.files['editPropertySecondaryImage3']
            # print(editPropertySecondaryImage1.filename)

            expectedImagesList = [propertyProfileImage, editPropertySecondaryImage1,
                                  editPropertySecondaryImage2, editPropertySecondaryImage3]

            propertyImagesCombined = ''
            for index, img in enumerate(expectedImagesList):
                property_images = ''
                #! SECURITY CHECK - Do not allow malicious uploads
                if img.filename:
                    # * 2. Ensure file extension is allowed. (Images only) -> As defined in config.py
                    # print(img.filename)
                    if allowed_image(img.filename):
                        # print(os.getcwd())
                        # * 3. Ensure the file itself isn't dangerous.
                        img_filename = secure_filename(img.filename)
                        # image = property/{property_type}/random_str_timestamp.extension
                        property_images = f'property/{property.property_type.lower()}/{secrets.token_hex(2)}{secrets.token_hex(3)}_{str(time.time()).split(".")[0]}.{img_filename.split(".")[-1].lower()}'
                        # print(img_filename)
                        # print(property_images)
                        #! Restrict Filesize
                        # ? By default Flask throws a HTTP 413 error if MAX_CONTENT_LENGTH is exceeded.
                        # Save the image
                        img.save(os.path.join(
                            create_app().config["IMAGE_UPLOADS_PROPERTY"], property_images))

                    else:
                        error_message = "Please upload an image with accepted extension (.png, .jpeg, .jpg)"
                        flash(f"{error_message}")
                        print(error_message)
                        return redirect(url_for('business_admin_view.view_property', property_id=property.id))

                 # Format the Property Image string ('|' separated)

                else:
                    break

                propertyImagesCombined += f'{property_images}|'

                # if index == len(expectedImagesList)-1:
                #     propertyImagesCombined += f'{property_images}'
                # else:
                #     propertyImagesCombined += f'{property_images}|'

        # * 'Filtration' Process
        # remove any empty fields
        propertyImagesCombinedList = [
            i for i in propertyImagesCombined.split('|') if i]
        propertyImagesCombinedString = ''
        for index, i in enumerate(propertyImagesCombinedList):
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
        #? EdgeCase: User has firstname only. e.g. Google? -> Far-fetched? Maybe. Possible? Yes.
        owner.last_name = propertyEditForm["editContactName"].split(" ")[-1] if propertyEditForm["editContactName"].split(" ")[-1] else ''
        owner.user_phone = propertyEditForm["editPhoneNumber"]
        owner.businessName = propertyEditForm["editBusinessName"]

        # Save changes to Database
        db.session.commit()

        # redirect -> Refresh the page to reflect the changes
        return redirect(url_for('business_admin_view.view_property', property_id=property.id))

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
