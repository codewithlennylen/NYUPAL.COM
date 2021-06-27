
from app import create_app
from app import db
from app.models import Property
import random
import time

# Self-Explanatory
random.seed(time.time())

property_names = ["Crimson Bay",
                  "Lake Homes",
                  "Blue Heights",
                  "Blue Diamond",]

property_images = ['a.png', 'b.png',
                   'c.png', 'd.png']
room_images = ['e.png', 'f.png', 'g.png', 'h.png']
land_images = ['i.png', 'j.png', 'k.png', 'l.png']

towns = ['Nairobi', 'Mombasa', 'Kisumu', 'Eldoret', 'Machakos', 'Nakuru']
streets = ['Kilimani', 'Pamoja', 'Kabachia', 'Kirichwa', 'Kahawa', 'Kimbo']
# dates = ['Mon','Tue','Wed',"Thur","Fri","Sat","Sun"]
property_types = ["Residential", "Commercial","Land"]

with create_app().app_context():
    for i in range(4):
        property_name = random.choice(property_names)
        property_description = "Lorem ipsum dolor sit amet consectetur adipisicing elit. Nam similique maxime eius soluta voluptates illum tempora voluptate at eligendi delectus doloribus commodi hic dignissimos alias suscipit, quibusdam accusantium illo facilis reiciendis, molestiae incidunt omnis? Quo ea delectus quod at doloremque molestias saepe sed. Commodi ad quos officia fugit quaerat eligendi?"
        # I could use 2 variables (integer-columns), lower limit & upper limit to simplify filter by price
        property_price = str(random.randrange(30000,120000,5000))
        property_type = random.choice(property_types)
        property_location = f"{random.choice(towns)},{random.choice(streets)}"

        
        if property_type == "Residential":
            property_images = f"property/residential/{random.choice(property_images)}|property/residential/{random.choice(room_images)}|property/residential/{random.choice(room_images)}|property/residential/{random.choice(room_images)}"
            property_features = random.choice(["Swimming Pool|Full DSQ|Fully Furnished","Swimming Pool|Fully Furnished","Swimming Pool",""])
        elif property_type == "Commercial":
            property_images = f"property/commercial/{random.choice(property_images)}|property/commercial/{random.choice(room_images)}|property/commercial/{random.choice(room_images)}|property/commercial/{random.choice(room_images)}"
            property_features = random.choice(["Conference Rooms Available|Indoor Cafeteria|Indoor Gym","Conference Rooms Available|Indoor Gym","Conference Rooms Available",""])
        else:
            property_images = f"property/land/{random.choice(land_images)}|property/land/{random.choice(land_images)}|property/land/{random.choice(land_images)}|property/land/{random.choice(land_images)}"
            property_features = random.choice(["24/7 Security Services|Adequate Street Lighting|Shopping Centers Nearby","24/7 Security Services|Shopping Centers Nearby","24/7 Security Services",""])

        # User.id -> Relationship. Who owns the property?
        property_owner = random.randint(1,5)
        # Additional Contact Information.
        additionalContactInfo = random.choice(["Lorem ipsum dolor, sit amet consectetur adipisicing elit.",""])

        new_pt = Property(
            property_name = property_name,
            property_description = property_description,
            property_price = property_price,
            property_type = property_type,
            property_location = property_location,
            property_images = property_images,
            property_features = property_features,
            property_owner = property_owner,
            additionalContactInfo = additionalContactInfo,
        )


        print(f"property_name : {new_pt.property_name}, property_price : {new_pt.property_price}, property_type : {new_pt.property_type}, property_images : {new_pt.property_images}, property_features : {new_pt.property_features}")

        # Add the object(new_pt) to the database
        db.session.add(new_pt)
        db.session.commit()

        # minor delay to ensure the transaction is completed.
        time.sleep(0.4)