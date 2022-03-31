import os.path
from app import db, aws_client
from app.models import User, Property, PropertyDocuments
from app.config import  AWS_S3_BUCKET, VERIFICATION_PATH
from app.subscription_manager import subscription_manager
from flask_login import login_required, current_user
from flask import Blueprint, render_template, url_for, request, flash, redirect, Markup


# Create Blueprint
verification_portal_view = Blueprint('verification_portal_view',
                                __name__,
                                static_folder='static',
                                template_folder='templates')


@verification_portal_view.route('/', methods=['GET', 'POST'])
@login_required
def verification_dashboard():
    #! Check if user is nyupal admin!
    if current_user.businessAccount != 1:
        return redirect(url_for('main_view.index',page_num=1))

    #* list of property owners
    owners = User.query.filter_by(businessAccount=1).all()

    # list of properties listed / owned by the user.
    propertys = current_user.property
    print(f'propertys {propertys}')

    # business plan
    # userPlan = Plans.query.filter_by(id=current_user.businessPlan).first()

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
    

    return render_template("verification_portal/verification_dashboard.html",
                           owners=owners,
    )

@verification_portal_view.route('/property/<owner_id>/', methods=['GET', 'POST'])
@login_required
def owner_property(owner_id):
    # Check if user is admin!
    if current_user.businessAccount != 1:
        return redirect(url_for('main_view.index',page_num=1))

    # propertyTypes = ["Residential", "Commercial", "Land"]
    # This will be used to display and Ad on the Add-Property Page
    bannerAd = url_for('static', filename='icons/banner.jpg')

    propertys = Property.query.filter_by(property_owner=owner_id).all()

    return render_template("verification_portal/owner_property.html",
                           bannerAd=bannerAd,
                           propertys=propertys,
                           owner_id=owner_id)


@verification_portal_view.route('/view/<property_id>', methods=['GET', 'POST'])
@login_required
def verification_status(property_id):
    """This controls the page that enables admins to update a property's verification
    status; view property documents and approve verification.


    Args:
        property_id (int): property's unique ID

    Returns:
        render_template: frontend
    """
    # Check if user is admin!
    if current_user.businessAccount != 1:
        return redirect(url_for('main_view.index',page_num=1))

    #! property_id should be randomCharacters -> Tom Scott
    property = Property.query.filter_by(id=int(property_id)).first()
    owner = User.query.filter_by(id=property.property_owner).first()

    # Getting the image dirs
    propertyImages = property.property_images.split('|')

    #* Verification documents s3 bucket
    #? We should get the doc from DB then download from Bucket.
    # verification_docs_bucket = aws_client.list_objects(Bucket=AWS_S3_BUCKET)['Contents']
    # verification_docs = [key['Key'] for key in verification_docs_bucket]
    # print(f"s3: {verification_docs}")

    #* verification documents from DB
    property_docs = property.documents
    is_verified = property_docs[0].verified if property_docs else None
    print(f'is_verified: {is_verified}')
    property_docs_logs = [(p.title_deed,p.national_id,p.tax_receipt) for p in property_docs]
    print(f'Property Documents: {property_docs_logs}')
    property_docs_dict = dict()
    local_property_docs_dict = {}
    #! Sketchy
    for p in property_docs:
        # 'rename' so as to avoid wrong redirect at the frontend
        property_docs_dict['title_deed'] = p.title_deed.replace('/','-')
        property_docs_dict['national_id'] = p.national_id.replace('/','-')
        property_docs_dict['tax_receipt'] = p.tax_receipt.replace('/','-')

        # download original filename
        download_property_document(p.title_deed)
        download_property_document(p.national_id)
        download_property_document(p.tax_receipt)

        # path to downloaded documents
        #* ephemeral filesystem advantage
        local_property_docs_dict['title_deed'] = f'downloads/{p.title_deed.split("/")[-1]}'
        local_property_docs_dict['national_id'] = f'downloads/{p.national_id.split("/")[-1]}'
        local_property_docs_dict['tax_receipt'] = f'downloads/{p.tax_receipt.split("/")[-1]}'


    # print(f'DB: {property_docs_dict}')
    # print(f'Local: {local_property_docs_dict}')


    #? Verification Status and Text => DB.Json Column?
    verification_dict = {
        0:('btn-warning','verification pending','We are currently working on getting your property verified.'),
        1:('btn-success','verified','Your property has been successfully verified!'),
        2:('btn-danger','verification failed','Your property does not meet requirements for verification. Contact us for more info.'),
        3:('btn-danger','verification flagged','Your property does not meet requirements for verification. Contact us for more info.'),
    }

    #  Edit Property Verification Status
    if request.method == 'POST':
        propertyEditForm = request.form
        print(propertyEditForm)
        pending = 1 if propertyEditForm.get("choice-0") else 0
        verified = 1 if propertyEditForm.get("choice-1") else 0
        failed = 1 if propertyEditForm.get("choice-2") else 0
        flagged = 1 if propertyEditForm.get("choice-3") else 0
        print(pending,
              verified,
              failed,
              flagged)
        # # .strip() removes trailing spaces

        verification_decision = 0
        if pending:
            verification_decision = 0
        elif verified:
            verification_decision = 1
        elif failed:
            verification_decision = 2
        elif flagged:
            verification_decision = 3
        else:
            verification_decision = 0
            print("invalid entry")

        print(f'verification_decision: {verification_decision}')
        property_docx = PropertyDocuments.query.filter_by(property_id=property.id).first()
        property_docx.verified = verification_decision
        # # Save changes to Database
        db.session.commit()

        # redirect -> Refresh the page to reflect the changes
        return redirect(url_for('verification_portal_view.verification_status', property_id=property.id))

    return render_template("verification_portal/verification_status.html",
                           is_verified=is_verified,
                           property=property,
                           owner=owner,
                           propertyImages=propertyImages,
                           verification_dict=verification_dict,
                           local_property_docs_dict=local_property_docs_dict)


def download_property_document(doc_name):
    """Download files from AWS S3

    Args:
        doc_name (str): name of the document to download
    """

    requested_file = f'{VERIFICATION_PATH}{doc_name}'
    # static files must be saved in the static sub-folder.
    file_save_location = f'app/verification_portal/static/verification_portal/downloads/{doc_name.split("/")[-1]}'
    print(f'\nrequested_file: {requested_file}')
    print(f'file_save_location: {file_save_location}')

    #* First check if requested file is in dir, avoid redundant downloads.
    file_check = os.path.exists(file_save_location)
    if not file_check:
        # :type Bucket: str
        # :param Bucket: The name of the bucket to download from.
        # :type Key: str
        # :param Key: The name of the key to download from.
        # :type Filename: str
        # :param Filename: The path to the file to download to.
        aws_client.download_file(AWS_S3_BUCKET, requested_file, file_save_location)
    # else:
    #     print("File exists")