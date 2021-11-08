
from flask import (Blueprint,
                   json,
                   request,
                   make_response,
                   jsonify,
                   render_template,
                   flash)
from flask_login import current_user
from app.models import Property, Rating, User
from app import db

# Create Blueprint
main_view = Blueprint('main_view', __name__)

@main_view.route('/')
@main_view.route('/<int:page_num>/')
def index(page_num=1):
    propertys = Property.query.paginate(
        per_page=12, page=page_num, error_out=True)

    propertyImages = []
    property_verified = {}
    for property in propertys.items:
        # Getting the image dirs
        images = property.property_images.split('|')
        profilePic = images[0]  # get the primary image (property_profile_pic)
        propertyImages.append(profilePic)
        owner = User.query.filter_by(id=property.property_owner).first()
        if owner:
            property_verified[property.id] = 1 if owner.businessPlan == 2 or owner.businessPlan == 3 else 0

    # print(propertyImages)

    return render_template("index.html",
                           propertys=propertys,
                           propertyImages=propertyImages,
                           property_verified=property_verified)


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
