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
    print(f'propertys {propertys}')

    # business plan
    userPlan = Plans.query.filter_by(id=current_user.businessPlan).first()

    #? Verification Status and Text => DB.Json Column?
    verification_dict = {
        0:('btn-warning','verification pending','We are currently working on getting your property verified.'),
        1:('btn-success','verified','Your property has been successfully verified!'),
        2:('btn-danger','verification failed','Your property does not meet requirements for verification. Contact us for more info.'),
        3:('btn-danger','verification flagged','Your property does not meet requirements for verification. Contact us for more info.'),
    }

    # Property_PropertyDocuments
    property_verification_status = {}
    verification_prompt = 4
    for p in propertys:
        print(f'p; {p}')
        # docs = PropertyDocuments.query.filter_by(property_id=p.id).first()
        docs = p.documents
        print(f'docs; {docs}')
        if docs:
            property_verification_status[p] = docs[0].verified
        else:
            #* verification_prompt is an arbitrary flag that'll be used to dynamically alter the UI
            property_verification_status[p] = verification_prompt

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
    

    return render_template("business/dashboard.html",
                           propertys=propertys,
                           propertyImages=propertyImages,
                           userPlan=userPlan,
                           verification_dict=verification_dict,
                           property_verification_status=property_verification_status,
                           verification_prompt=verification_prompt)


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
        cloudinary.config(cloud_name=os.getenv('CLOUD_NAME'), api_key=os.getenv('API_KEY'),
                          api_secret=os.getenv('API_SECRET'))
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
                        cloudinary_imgFilename = os.path.join(create_app().config["IMAGE_UPLOADS_PROPERTY"],property_images)
                        # print(cloudinary_imgFilename)
                        upload_result = cloudinary.uploader.upload(cloudinary_imgFilename)
                        print(f"upload_result: {upload_result['secure_url']}")
                        property_images = upload_result['secure_url']

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
        
        # user_object
        user = User.query.filter_by(id=current_user.id).first()
        print(f"User Object: {user.first_name}")
        user.user_phone = newPhoneNumber

        try:
            # Try adding property object to database.
            db.session.add(new_property)
            db.session.commit()

            flash(
                f"Your Property was Successfully Listed.")
            subject = 'Nyupal Property Listing'
            recipients=[current_user.user_email]
            body = f''' Dear {current_user.first_name} {current_user.last_name},
                        <br>
                        <p> Your Property {newPropertyName} has been successfully enlisted on our platform.</p>
                        
                        <hr>
                        <b>Please DO NOT REPLY to this email</b>.
                    '''

            #* Send confirmation email
            send_mail(recipients,subject,body)

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
        cloudinary.config(cloud_name=os.getenv('CLOUD_NAME'), api_key=os.getenv('API_KEY'),
                          api_secret=os.getenv('API_SECRET'))
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
                        cloudinary_imgFilename = os.path.join(create_app().config["IMAGE_UPLOADS_PROPERTY"],property_images)
                        # print(cloudinary_imgFilename)
                        upload_result = cloudinary.uploader.upload(cloudinary_imgFilename)
                        print(f"upload_result: {upload_result['secure_url']}")
                        property_images = upload_result['secure_url']

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


@business_admin_view.route('/docs/<plan>', methods=['GET', 'POST'])
@login_required
def docs_upload(plan):
    userProperty = current_user.property

    if request.method == 'POST':
        print("POST Request Received")
        propertyEditForm = request.form
        selectedProperty = propertyEditForm["selectedProperty"].strip()

        if selectedProperty not in [str(uProperty.id) for uProperty in userProperty]:
            error_message = "Please Select the Property."
            flash(f"{error_message}")
            print(error_message)
            return redirect(url_for('business_admin_view.docs_upload',plan=plan))

        #! Should be uploaded to AWS S3 instead.
        #? 
        if request.files != None:
            # cloudinary.config(cloud_name=os.getenv('CLOUD_NAME'), api_key=os.getenv('API_KEY'),
            #               api_secret=os.getenv('API_SECRET'))
            propertyDocTitleDeed = request.files['propertyDocTitleDeed']
            propertyDocNatId = request.files['propertyDocNatId']
            propertyDocTaxReceipt = request.files['propertyDocTaxReceipt']

            print(f"??empty file: {propertyDocTitleDeed} ==> {propertyDocTitleDeed.filename}")

            expectedDocumentsList = [propertyDocTitleDeed, propertyDocNatId,
                                  propertyDocTaxReceipt]

            propertyDocumentsCombined = []
            for index, doc in enumerate(expectedDocumentsList):
                property_documents = ''
                #! SECURITY CHECK - Do not allow malicious uploads
                if doc.filename:
                    # * 2. Ensure file extension is allowed. (Images only) -> As defined in config.py
                    # print(doc.filename)
                    if allowed_image(doc.filename):
                        # print(os.getcwd())
                        # * 3. Ensure the file itself isn't dangerous.
                        doc_filename = secure_filename(doc.filename)
                        # document = property/random_str_timestamp.extension
                        property_documents = f'property/{secrets.token_hex(2)}{secrets.token_hex(3)}_{str(time.time()).split(".")[0]}.{doc_filename.split(".")[-1].lower()}'
                        # print(doc_filename)
                        # print(property_documents)
                        #! Restrict Filesize
                        # ? By default Flask throws a HTTP 413 error if MAX_CONTENT_LENGTH is exceeded.
                        # Save the image
                        doc.save(os.path.join(
                            create_app().config["IMAGE_UPLOADS_PROPERTY"], property_documents))
                        resultant_docFilename = os.path.join(create_app().config["IMAGE_UPLOADS_PROPERTY"],property_documents).replace('\\','/')
                        # print(resultant_docFilename)
                        # upload_result = cloudinary.uploader.upload(resultant_docFilename)

                        print(f'resultant_docFilename; {resultant_docFilename}')
                        print(f'AWS_S3_BUCKET; {create_app().config["AWS_S3_BUCKET"]}')
                        print(f'VERIFICATION_PATH (key); {create_app().config["VERIFICATION_PATH"]}'+property_documents)
                        upload_result = aws_client.upload_file(resultant_docFilename, create_app().config['AWS_S3_BUCKET'], f'{create_app().config["VERIFICATION_PATH"]}'+property_documents)
                        print(f"upload_result: {upload_result}")
                        # property_documents = upload_result['secure_url']

                    else:
                        error_message = "Please upload a Document with accepted extension (png, jpeg, jpg or pdf)"
                        flash(f"{error_message}")
                        print(error_message)
                        return redirect(url_for('business_admin_view.docs_upload',plan=plan))
                else:
                    error_message = "Please Upload All Documents as Directed."
                    flash(f"{error_message}")
                    print(error_message)
                    return redirect(url_for('business_admin_view.docs_upload',plan=plan))

                propertyDocumentsCombined.append(property_documents)


        # store property in db
        new_documents = PropertyDocuments(
            user_id = int(current_user.id),
            property_id = int(selectedProperty),
            title_deed = propertyDocumentsCombined[0],
            national_id = propertyDocumentsCombined[1],
            tax_receipt = propertyDocumentsCombined[2],
        )

        try:
            # Try adding PropertyDocuments object to database.
            db.session.add(new_documents)
            db.session.commit()

            #* Check whether subscription has expired.
            #! Pay per property implementation
            sub_plan = current_user.businessPlan
            if not subscription_manager.validate:
                flash(Markup(f"Verification won't start until Subscription is updated! Please proceed below."))
                return redirect(url_for('finance_view.checkout',plan=sub_plan))
            else:
                flash(
                    f"Your Documents have been Uploaded Successfully. Verification Takes 3 to 5 Business Days.")
                subject = 'Nyupal Property Verification'
                recipients=[current_user.user_email]
                body = f''' Dear {current_user.first_name} {current_user.last_name},
                                <br>
                                <p>We have received the documents regarding Your Property's verification.</p>
                                <p>Verification takes 3 to 5 busines days. We will update you on the progress as necessary. </p>

                                
                                <hr>
                                <b>Please DO NOT REPLY to this email</b>.
                            '''

                send_mail(recipients,subject,body)
                return redirect(url_for('business_admin_view.property_dashboard'))
        except Exception as e:
            # Log this SERIOUS issue > Report to Developer
            error = e
            print(error)
            flash(f"Failed!! Please Contact Nyupal for further assistance.")
        


    return render_template('business/verify_docs.html',
    userProperty=userProperty,
    plan=plan)


def allowed_image(filename):

    # We only want files with a . in the filename
    if not "." in filename:
        return False

    # Split the extension from the filename
    ext = filename.rsplit(".", 1)[1]

    # Check if the extension is in ALLOWED_IMAGE_EXTENSIONS
    # if ext.upper() in create_app().config["ALLOWED_IMAGE_EXTENSIONS"]:
    if ext.upper() in create_app().config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False
