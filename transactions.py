from app.models import PaymentGateway
from app import create_app, db


transact_id = ['iQMxja','otY7I','VMApB8',
                'wydoLjf','wSA4NR','pDix9r']

with create_app().app_context():
    for transact in transact_id:
        p = PaymentGateway(
            transaction_id = transact.upper()
        )

        db.session.add(p)
        db.session.commit()
        print(f"Added Transaction: {transact.upper()}")
