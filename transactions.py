from app.models import PaymentGateway
from app import create_app, db


transact_id = ['x79FqQ','w9Q0MA','pM6aAg',
                'op8Axg','fXD9Rg','qS1Xuw']

with create_app().app_context():
    for transact in transact_id:
        p = PaymentGateway(
            transaction_id = transact.upper()
        )

        db.session.add(p)
        db.session.commit()
        print(f"Added Transaction: {transact.upper()}")
