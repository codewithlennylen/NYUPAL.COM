from app.models import Plans
from app import create_app, db
import time


plans = {
    "Standard Business Account":500,
    "Verified Business Account":1500,
    "Premium Business Account":3000

}


with create_app().app_context():
    for plan in plans.keys():
        p = Plans(
            plan_name = plan,
            plan_price = plans[plan]
        )

        db.session.add(p)
        print(f"Added Plan: {plan} || {plans[plan]}")
        time.sleep(0.3)

    db.session.commit()
