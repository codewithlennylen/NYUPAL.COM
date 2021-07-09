import app
from app import db
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin


#! additionalContactInfo vs businessName


class User(db.Model, UserMixin):
    __tablename__ = 'user' # Explicit is better than implicit.

    # STUDENT INFORMATION   
    id = db.Column(db.Integer, primary_key = True) # user's default id
    first_name = db.Column(db.String(50), nullable=False) # Lenny
    last_name = db.Column(db.String(50), nullable=False) # Ng'ang'a
    user_email = db.Column(db.String, nullable = False)
    user_pword = db.Column(db.String, nullable = False)
    # Optional > Builds the User's Profile
    user_updates = db.Column(db.Integer, nullable = True, default=0) # newsletter subscriptions
    user_pic = db.Column(db.String, nullable = True, default='default.png') # image dir
    user_phone = db.Column(db.String, nullable = True) # phone number > OTP?
    
    # Used to determine whether user can list property. > 'Admin' Emulation
    businessAccount = db.Column(db.Integer, nullable = True, default=0)
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


# Property includes land and buildings
class Property(db.Model):
    __tablename__ = 'property' # Explicit is better than implicit.

    # STUDENT INFORMATION   
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