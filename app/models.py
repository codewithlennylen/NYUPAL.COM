import datetime
import app
from app import db, create_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin


#? additionalContactInfo vs businessName
# businessName supersedes additionalContactInfo. 
# All is well

class User(db.Model, UserMixin):
    __tablename__ = 'user' # Explicit is better than implicit.
  
    id = db.Column(db.Integer, primary_key = True) # user's default id
    first_name = db.Column(db.String(50), nullable=False) # Lenny
    last_name = db.Column(db.String(50), nullable=False) # Ng'ang'a
    user_email = db.Column(db.String, nullable = False)
    user_pword = db.Column(db.String, nullable = False)
    # Optional > Builds the User's Profile
    user_updates = db.Column(db.Integer, nullable = True, default=0) # newsletter subscriptions
    user_pic = db.Column(db.String, nullable = True, default=create_app().config["DEFAULT_IMAGE"]) # image dir
    user_phone = db.Column(db.String, nullable = True) # phone number > OTP?
    
    # Used to determine whether user can list property. > 'Admin' Emulation
    businessAccount = db.Column(db.Integer, nullable = True, default=0)
    businessPlan = db.Column(db.Integer, db.ForeignKey('plans.id') ,nullable=True)
    # This will be displayed on the Contact Card on the more_info page of a property
    businessName = db.Column(db.String(150), nullable = True) 

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.create_app().config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id' : self.id}).decode('utf-8')

    @staticmethod # Because we didn't use self in the parameters
    def verify_reset_token(token):
        s = Serializer(app.create_app().config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None

        return User.query.get(user_id)

    # RELATIONSHIPS
    # Property_Owned / In_Charge
    property = db.relationship(
        'Property',
        foreign_keys = 'Property.property_owner',
        backref = 'owner',
        lazy = True
    )

    # user's star-rating.
    ratings = db.relationship(
        'Rating',
        foreign_keys = 'Rating.user_id',
        backref = 'userRating',
        lazy = True
    )

    # user's star-rating.
    property_documents = db.relationship(
        'PropertyDocuments',
        foreign_keys = 'PropertyDocuments.user_id',
        backref = 'userPropertyDocuments',
        lazy = True
    )


# Property includes land and buildings
class Property(db.Model):
    __tablename__ = 'property' # Explicit is better than implicit.
 
    id = db.Column(db.Integer, primary_key = True) # Auto-generated default id
    property_name = db.Column(db.String(100), nullable=False)
    property_description = db.Column(db.String, nullable=False)
    # I could use 2 variables (integer-columns), lower limit & upper limit to simplify filter by price
    property_price = db.Column(db.String(100), nullable=True) # To enable range 50-60K
    property_type = db.Column(db.String, nullable=True)
    property_location = db.Column(db.String, nullable=True)
    #* I am thinking of adding land as a type / category
    # property_is_land = db.Column(db.String, nullable=True) 
    property_images = db.Column(db.String, nullable=True) # List of | separated img-dir names
    #* I plan to use PostgreSQL JSON column for better structure.
    # But I could work with | separated strings representing different features,
    # Then the template(moreInfoPage) could loop through and display the features
    property_features = db.Column(db.String, nullable=True) # List of | separated img-dir names

    # User.id -> Relationship. Who owns the property?
    property_owner = db.Column(db.Integer, db.ForeignKey('user.id') ,nullable=False)
    # Additional Contact Information.
    additionalContactInfo = db.Column(db.String, nullable=True) # e.g. Manager, ABC Property Limited
    
    # RELATIONSHIPS
    # star-rating tied to property.
    ratings = db.relationship(
        'Rating',
        foreign_keys = 'Rating.property_id',
        backref = 'buildingRating',
        lazy = True
    )

    # Documents tied to property.
    documents = db.relationship(
        'PropertyDocuments',
        foreign_keys = 'PropertyDocuments.property_id',
        backref = 'buildingPropertyDocuments',
        lazy = True
    )


class PropertyDocuments(db.Model):
    __tablename__ = 'property_docs' # Explicit is better than implicit.

    id = db.Column(db.Integer, primary_key = True) # Auto-generated default id
    user_id = db.Column(db.Integer, db.ForeignKey('user.id') ,nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id') ,nullable=False)
    title_deed = db.Column(db.String(100), nullable=False)
    national_id = db.Column(db.String(100), nullable=False)
    tax_receipt = db.Column(db.String(100), nullable=False)
    # 0 - ongoing, 1 - passed, 3 - rejected, 4 - flagged
    verified = db.Column(db.Integer, nullable=True, default = 0)


# Plans entail the various pricing models available
class Plans(db.Model):
    __tablename__ = 'plans' # Explicit is better than implicit.

    id = db.Column(db.Integer, primary_key = True) # Auto-generated default id
    plan_name = db.Column(db.String(100), nullable=False)
    plan_price = db.Column(db.Integer, nullable=False)
 
    # RELATIONSHIPS
    # accounts / users tied to a particular plan.
    accounts = db.relationship(
        'User',
        foreign_keys = 'User.businessPlan',
        backref = 'businessOwner',
        lazy = True
    )


class Rating(db.Model):
    __tablename__ = 'rating' # Explicit is better than implicit.

    id = db.Column(db.Integer, primary_key = True) # Auto-generated default id
    user_id = db.Column(db.Integer, db.ForeignKey('user.id') ,nullable=False)
    #! Property_id to Integer type -> enumeration vulnerability if integers are used
    property_id = db.Column(db.Integer, db.ForeignKey('property.id') ,nullable=False)
    rating = db.Column(db.String(10), nullable=False)
