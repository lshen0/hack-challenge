from db import db, User, Connection, Eatery, Review, update_user_rankings
from flask import Flask, request
import json
import datetime

app = Flask(__name__)
db_filename = "beli.db" 

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()

# Generalized response formats
def success_response(body, code=200):
    return json.dumps(body), code

def failure_response(message, code=404):
    return json.dumps({"error": message}), code

# -- ROUTES -----------------------------------------------

# USER ROUTES
@app.route("/api/users/", methods=["POST"])
def create_user():
    """"
    Create user
    """
    try: 
        body = json.loads(request.data)
    except:
        return failure_response("Invalid JSON format!", 400)
    
    name = body.get("name")
    username = body.get("username")
    bio = body.get("bio")
    location = body.get("location")
    if name is None or username is None:
        return failure_response("Missing required fields!", 400)
    
    user = User(name=name, username=username, bio=bio, location=location, timestamp=datetime.datetime.now())
    db.session.add(user)
    db.session.commit()
    return success_response(user.serialize(), 201)

@app.route("/api/users/")
def get_users():
    """"
    Get all users
    """
    users = User.query.all()
    return success_response({"users" : [ u.serialize() for u in users ]})

@app.route("/api/users/<int:user_id>/", methods=["DELETE"])
def delete_user_by_id(user_id):
    """"
    Delete user by id
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("user not found")
    db.session.delete(user)
    db.session.commit()
    return success_response(user.serialize())

# EATERY ROUTES
@app.route("/api/eateries/", methods=["POST"])
def create_eatery():
    """
    Create eatery
    """
    try:
        body = json.loads(request.data)
    except:
        return failure_response("Invalid JSON format!", 400)
    
    name = body.get("name")
    description = body.get("description")
    cuisine = body.get("cuisine")
    location = body.get("location")
    if name is None:
        return failure_response("Missing required fields!", 400)
    
    eatery = Eatery(name=name, description=description, cuisine=cuisine, location=location, average_rating=0)
    db.session.add(eatery)
    db.session.commit()
    return success_response(eatery.serialize(), 201)

@app.route("/api/eateries/")
def get_eateries():
    """"
    Get all eateries
    """
    eateries = Eatery.query.all()
    return success_response({"eateries": [ e.serialize() for e in eateries ]})

@app.route("/api/eateries/<int:eatery_id>/", methods=["DELETE"])
def delete_eatery_by_id(eatery_id):
    """"
    Delete eatery by id
    """
    eatery = Eatery.query.filter_by(id=eatery_id).first()
    if eatery is None:
        return failure_response("eatery not found")
    db.session.delete(eatery)
    db.session.commit()
    return success_response(eatery.serialize())

# REVIEW ROUTES
@app.route("/api/reviews/", methods=["POST"])
def create_review():
    """
    Create a review 
    """
    try:
        body = json.loads(request.data)
    except:
        return failure_response("Invalid JSON format!", 400)
   
    user_id = body.get("user_id")
    eatery_id = body.get("eatery_id")
    rating = body.get("rating")
    review_text = body.get("review_text")
    if user_id is None or eatery_id is None or rating is None:
        return failure_response("Missing required fields!", 400)
    
    review = Review(user_id=user_id, eatery_id=eatery_id, rating=rating, review_text=review_text)
    db.session.add(review)
    db.session.commit()
    update_user_rankings()
    return success_response(review.serialize(), 201)

@app.route("/api/reviews/")
def get_reviews():
    """
    Get all reviews
    """
    reviews = Review.query.all()
    return success_response({"reviews": [ r.serialize() for r in reviews ]})

@app.route("/api/reviews/<int:review_id>/", methods=["DELETE"])
def delete_review_by_id(review_id):
    """"
    Delete review by id
    """
    review = Review.query.filter_by(id=review_id).first()
    if review is None:
        return failure_response("review not found")
    db.session.delete(review)
    db.session.commit()
    return success_response(review.serialize())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
