from flask import Blueprint
from flask import render_template
from app.models import Property

# Create Blueprint
main_view = Blueprint('main_view', __name__)

@main_view.route('/')
def index():
    propertys = Property.query.all()

    propertyImages = []
    for property in propertys:
        # Getting the image dirs
        images = property.property_images.split('|')
        profilePic = images[0] # get the primary image (property_profile_pic)
        propertyImages.append(profilePic) 

    print(propertyImages)

    return render_template("index.html",
                           propertys=propertys,
                           propertyImages=propertyImages)
