from flask import Flask
from db import db, User, Connection, Eatery, Review

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///beli.db"  
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.drop_all() # Reset
    db.create_all() # Prepopulate database with existing data

    # Users
    user1 = User(name="Lydia",  username="lydia")
    user2 = User(name="Cam",    username = "cam")
    user3 = User(name="Claire", username="claire")
    user4 = User(name="Parsa", username="parsa")
    users = [
        user1, user2, user3, user4
    ] 

    # Eateries
    eatery1 = Eatery(name="104West!",                       location="104 West Avenue")
    eateries = [
        eatery1,
        Eatery(name="Libe Cafe",                      location="Olin Library"),
        Eatery(name="Atrium Cafe",                    location="Sage Hall"),
        Eatery(name="Bear Necessities",               location="Robert Purcell Community Center"),
        Eatery(name = "Becker House Dining Room",     location="Carl Becker House"),
        Eatery(name = "Big Red Barn",                 location="Big Red Barn"),
        Eatery(name = "Bus Stop Bagels",              location="Kennedy Hall"),
        Eatery(name = "Cafe Jennie",                  location="The Cornell Store"),
        Eatery(name = "Cook House Dining Room",       location="Alice Cook House"),
        Eatery(name = "Dairy Bar",                   location="Stocking Hall"),
        Eatery(name = "Crossing's Cafe",             location="Toni Morrison Hall"),
        Eatery(name = "Goldie's Cafe",               location="Physical Sciences Building"),
        Eatery(name = "Green Dragon",                location="Sibley Hall"),
        Eatery(name = "Bethe House Dining Room",     location="Hans Bethe House"),
        Eatery(name = "Jansen's Market",             location="Noyes Community Recreation Center"),
        Eatery(name = "Keeton House Dining Room",    location="William Keeton House"),
        Eatery(name = "Mann Cafe",                   location="Mann Library"),
        Eatery(name = "Martha's Cafe",               location="Martha Van Rensselaer Hall"),
        Eatery(name = "Mattin's Cafe",               location="Duffield Hall"),
        Eatery(name = "Morrison Dining",             location="Toni Morrison Hall"),
        Eatery(name = "North Star Dining Room",      location="Appel Commons"),
        Eatery(name = "Novick's Cafe",               location="Ruth Bader Ginsburg Hall"),
        Eatery(name = "Okenshields",                 location="Willard Straight Hall"),
        Eatery(name = "Risley Dining Room",          location="Risley Residential College"),
        Eatery(name = "Rose House Dining Room",      location="Flora Rose House"),
        Eatery(name = "Rusty's",                     location="Uris Hall"),
        Eatery(name = "Straight from the Market",    location="Willard Straight Hall"),
        Eatery(name = "Trillium",                    location="Kennedy Hall")
    ]

    # Connections
    conn1 = Connection(follower_id=1, following_id=2)
    conn2 = Connection(follower_id=1, following_id=3)
    conn3 = Connection(follower_id=1, following_id=4)
    conn4 = Connection(follower_id=2, following_id=1)
    conn5 = Connection(follower_id=3, following_id=1)
    conn6 = Connection(follower_id=4, following_id=1)
    connections = [
        conn1, conn2, conn3, conn4, conn5, conn6
    ]

    # Reviews
    reviews = [
        (Review(user_id=1, eatery_id=1, rating=5, review_text="was ok")),
        (Review(user_id=1, eatery_id=19, rating=10, review_text="duffadilla.")),
        (Review(user_id=2, eatery_id=6, rating=10, review_text="route 20 was delicious")),
        (Review(user_id=2, eatery_id=19, rating=8, review_text="free oyster crackers")),
        (Review(user_id=3, eatery_id=3, rating=7.2, review_text="go-to!")),
        (Review(user_id=3, eatery_id=9, rating=10, review_text="unbeatable")),
        (Review(user_id=3, eatery_id=19, rating=9, review_text="duffadilla")),
        (Review(user_id=4, eatery_id=21, rating=6.8, review_text="nacho bowls!!"))
        
    ]

    # Add and commit
    db.session.add_all(users + eateries + connections + reviews)
    db.session.commit()

    print("✅ Database seeded with sample data.")
