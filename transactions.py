from app.models import PaymentGateway
from app import create_app, db


transact_id = 'ABC123'

with create_app().app_context():
    p = PaymentGateway(
        transaction_id = transact_id
    )

    db.session.add(p)
    db.session.commit()
    print(f"Added Transaction: {transact_id}")
