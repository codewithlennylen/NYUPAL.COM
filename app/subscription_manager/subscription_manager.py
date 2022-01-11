from app.models import Subscription, User
from datetime import date


def validate(user_id):
    
    user = User.query.filter_by(id=user_id).first()
    subscription = Subscription.query.filter_by(user_id=user.id).first()

    today = date.today()
    subscription_expiry_date = subscription.end_date

    # check for subscription expiry.
    if today > subscription_expiry_date:
        return False
    else:
        return True