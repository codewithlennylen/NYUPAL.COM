from flask import Blueprint, json, request, make_response, jsonify
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
        profilePic = images[0]  # get the primary image (property_profile_pic)
        propertyImages.append(profilePic)

    print(propertyImages)

    return render_template("index.html",
                           propertys=propertys,
                           propertyImages=propertyImages)


@main_view.route('/rating-clicked', methods=['POST'])
def rating_clicked():
    """Receives the rating; when a user stars a property

    Returns:
        json: success
    """
    rating_object = request.get_json()
    property_id = rating_object.get('string_id').split('_')[-1]
    property_rating = rating_object.get('rating')

    print(property_id,
          property_rating)

    response = make_response(jsonify({"result": "success"}), 200)

    return response
