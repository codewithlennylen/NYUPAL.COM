from app import db


class User(db.Model):
    __tablename__ = 'user' # Explicit is better than implicit.

    # STUDENT INFORMATION   
    user_id = db.Column(db.Integer, primary_key = True) # user's default id
    first_name = db.Column(db.String(50), nullable=False) # Lenny
    last_name = db.Column(db.String(50), nullable=False) # Ng'ang'a
    user_email = db.Column(db.String, nullable = False)
    user_pword = db.Column(db.String, nullable = False)
    # Optional > Builds the User's Profile
    user_updates = db.Column(db.Integer, nullable = True) # newsletter subscriptions
    user_pic = db.Column(db.String, nullable = True) # image dir
    user_phone = db.Column(db.String, nullable = True) # phone number > OTP?
