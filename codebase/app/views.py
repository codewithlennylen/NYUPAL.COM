from flask import (Blueprint,
                   json,
                   request,
                   make_response,
                   jsonify,
                   render_template,
                   flash)
from flask_login import current_user
from app.models import Property, Rating
from app import db

# Create Blueprint
main_view = Blueprint('main_view', __name__)


@main_view.route('/index/<int:page_num>/')
def index(page_num):
    propertys = Property.query.paginate(
        per_page=12, page=page_num, error_out=True)

    propertyImages = []
    for property in propertys.items:
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
    THIS FUNCTION IS CALLED ASYNCHRONOUSLY BY THE JS FETCH API FROM THE FRONTEND

    Returns:
        json: success
    """
    rating_object = request.get_json()
    property_id = rating_object.get('string_id').split('_')[-1]
    property_rating = rating_object.get('rating')

    # print(property_id,
    #       property_rating)

    new_rating = Rating(
        user_id=current_user.id,
        property_id=int(property_id),
        rating=property_rating
    )

    try:
        db.session.add(new_rating)
        db.session.commit()
        print("Rating Success")
    except Exception as e:
        flash("Failed to Rate building")
        #! Log Error.
        print(f"Failed to Rate building: {e}")

    response = make_response(jsonify({"result": "success"}), 200)

    return response
