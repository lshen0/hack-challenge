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
    # user1 = User(name="Alice Smith", netid="as123")
    # user2 = User(name="Bob Johnson", netid="bj456")
    # user3 = User(name="Charlie Kim", netid="ck789")

    # Eateries
    eateries = [
        Eatery(name="104West!",                       location="104 West Avenue"),
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
    # conn1 = Connection(follower=user1, followee=user2)
    # conn2 = Connection(follower=user2, followee=user3)

    # Reviews
    # review1 = Review(user=user1, eatery=eatery1, rating=5, text="Amazing tacos!")
    # review2 = Review(user=user2, eatery=eatery2, rating=4, text="Loved the carbonara.")
    # review3 = Review(user=user3, eatery=eatery3, rating=3, text="Pretty average burgers.")

    # Add and commit
    db.session.add_all(eateries)
    db.session.commit()

    print("✅ Database seeded with sample data.")
