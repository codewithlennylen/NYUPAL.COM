import app
from app import db
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin


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