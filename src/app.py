from db import db, User, Connection, Eatery, Review
from flask import Flask, request
import json
import datetime
from sqlalchemy import func

app = Flask(__name__)
db_filename = "beli.db" 

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)

# -- Generalized responses --------------------------------------------------------
def success_response(body, code=200):
    return json.dumps(body), code

def failure_response(message, code=404):
    return json.dumps({"error": message}), code

# -- Update rankings/average ratings ---------------------------------------------
def update_user_rankings():
    """
    Updates each user's ranking based on how many reviews they have written.
    More reviews = higher rank (lower number).
    """
    # Query review count for each user, ordered by count descending
    user_review_counts = db.session.query(
        Review.user_id,
        func.count(Review.id).label("review_count")
    ).group_by(Review.user_id).order_by(func.count(Review.id).desc()).all()

    # Assign ranking based on index in sorted list (starting from 1)
    for rank, (user_id, count) in enumerate(user_review_counts, start=1):
        user = db.session.get(User, user_id)
        if user:
            user.ranking = rank
            user.ratings_count = count  # Optional: keep this in sync

    db.session.commit()

def update_user_average_rating(user_id):
    """"
    Update user's average rating based on ratings across all reviews they have written.
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("user not found")
    reviews = user.reviews
    if len(reviews) == 0:
        user.average_rating = 0
    else:
        total = sum([review.rating for review in reviews])
        user.average_rating = round((float) (total) / len(reviews), 1)
    user.ratings_count = len(reviews)
    db.session.commit()

def update_eatery_average_rating(eatery_id):
    """"
    Update eatery's average rating based on ratings across all reviews written about them.
    """
    eatery = Eatery.query.filter_by(id=eatery_id).first()
    if eatery is None:
        return failure_response("eatery not found")
    reviews = eatery.reviews
    if len(reviews) == 0:
        eatery.average_rating = 0
    else:
        total = sum([review.rating for review in reviews])
        eatery.average_rating = round((float) (total) / len(reviews), 1)
    db.session.commit()

def initialize_statistics():
    """
    Initialize average ratings for users/eateries + user rankings.
    """
    for user in User.query.all():
        update_user_average_rating(user.id)
    for eatery in Eatery.query.all():
        update_eatery_average_rating(eatery.id)
    update_user_rankings()

# Initialize statistics
with app.app_context():
    initialize_statistics()

@app.route("/")
def hello_world():
    return "Hello world!"

# -- USER ROUTES -------------------------------------------------------------------

@app.route("/api/users/")
def get_users():
    """"
    Get all users
    """
    users = User.query.all()
    return success_response({"users" : [ u.serialize() for u in users ]})

@app.route("/api/users/<int:user_id>/")
def get_user_by_id(user_id):
    """
    Get user by id
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("user not found")
    return success_response(user.serialize())

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

@app.route("/api/users/<int:user_id>/followers/")
def get_user_followers(user_id):
    """
    Get all followers of a user
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("user not found")
    followers = Connection.query.filter_by(following_id=user_id)
    return success_response({"followers" : [ c.follower.simple_serialize() for c in followers ]})

@app.route("/api/users/<int:user_id>/following/")
def get_user_following(user_id):
    """
    Get all people this user is following
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("user not found")
    following = Connection.query.filter_by(follower_id=user_id)
    return success_response({"following" : [ c.following.simple_serialize() for c in following ]})

@app.route("/api/users/<int:user_id>/reviews/")
def get_user_reviews(user_id):
    """
    Get all reviews, ordered by rating (highest to lowest), made by this user
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("user not found")
    reviews = Review.query.filter_by(user_id=user_id)
    sorted_reviews = sorted(reviews, key=lambda r: r.rating, reverse=True)

    return success_response({"reviews": [ r.serialize() for r in sorted_reviews ]})

@app.route("/api/users/<int:user_id>/following_reviews/")
def get_user_following_reviews(user_id):
    """
    Get all reviews made by this user's following, sorted from most recent to least recent
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("user not found")
    following = user.following
    reviews = []
    for f in following:
        for r in Review.query.filter_by(user_id=f.id):
            reviews.append(r) 
    sorted_reviews =  sorted(reviews, key=lambda r: r.timestamp, reverse=True)

    return success_response({"reviews": [ r.serialize() for r in sorted_reviews ]})

@app.route("/api/users/<int:user_id>/ranking/")
def get_user_ranking(user_id): 
    """
    Get the ranking of a user
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("user not found")
    return success_response({"ranking": user.ranking})

@app.route("/api/users/<int:user_id>/average_rating/")
def get_user_average_rating(user_id):
    """
    Get the average rating of a user
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("user not found")
    return success_response({"average_rating": user.average_rating})

@app.route("/api/users/<int:user_id>/rating_count/")
def get_user_ratings_count(user_id):
    """
    Get the ratings_count of a user
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("user not found")
    return success_response({"ratings_count": user.ratings_count})

# -- CONNECTION ROUTES -------------------------------------------------------

@app.route("/api/connections/")
def get_connections():
    """
    Get all connections
    """
    connections = Connection.query.all()
    return success_response({"connections" : [ c.serialize() for c in connections ]})

@app.route("/api/connections/<int:connection_id>/")
def get_connection_by_id(connection_id):
    """
    Get connection by id
    """
    connection = Connection.query.filter_by(id=connection_id).first()
    if connection is None:
        return failure_response("connection not found")
    return success_response(connection.serialize())

@app.route("/api/connections/", methods=["POST"])
def follow():
    """"
    Have one user follow another
    """
    try: 
        body = json.loads(request.data)
    except:
        return failure_response("Invalid JSON format!", 400)
    
    follower_id = body.get("follower_id")
    following_id = body.get("following_id")
    if follower_id is None or following_id is None:
        return failure_response("Missing required fields!", 400)
    if follower_id == following_id:
        return failure_response("user cannot follow self", 400)

    follower = User.query.filter_by(id=follower_id).first()
    following = User.query.filter_by(id=following_id).first()
    if follower is None:
        return failure_response("follower not found")
    if following is None:
        return failure_response("following not found")

    connection = Connection(follower_id=follower_id, following_id=following_id)
    db.session.add(connection)

    # Update follower/following counts
    follower.following_count = follower.following_count + 1
    following.follower_count = following.follower_count + 1

    db.session.commit()
    return success_response(connection.serialize())

@app.route("/api/connections/", methods=["DELETE"])
def unfollow():
    """"
    Have one user unfollow another
    """
    try: 
        body = json.loads(request.data)
    except:
        return failure_response("Invalid JSON format!", 400)
    
    follower_id = body.get("follower_id")
    following_id = body.get("following_id")
    if follower_id is None or following_id is None:
        return failure_response("Missing required fields!", 400)
    
    follower = User.query.filter_by(id=follower_id).first()
    following = User.query.filter_by(id=following_id).first()
    if follower is None:
        return failure_response("follower not found")
    if following is None:
        return failure_response("following not found")

    connection = Connection.query.filter_by(follower_id=follower_id, following_id=following_id).first()
    if connection is None:
        return failure_response("connection does not exist", 404)
    db.session.delete(connection)
   
    follower.following_count = follower.following_count - 1
    following.follower_count = following.follower_count - 1
    db.session.commit()

    return success_response(connection.serialize())

# -- EATERY ROUTES ----------------------------------------------------------

@app.route("/api/eateries/")
def get_eateries():
    """"
    Get all eateries
    """
    eateries = Eatery.query.all()
    return success_response({"eateries": [ e.serialize() for e in eateries ]})

@app.route("/api/eateries/<int:eatery_id>/")
def get_eatery_by_id(eatery_id):
    """
    Get eatery by id
    """
    eatery = Eatery.query.filter_by(id=eatery_id).first()
    if eatery is None:
        return failure_response("eatery not found")
    return success_response(eatery.serialize())

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
    location = body.get("location")
    if name is None:
        return failure_response("Missing required fields!", 400)
    
    eatery = Eatery(name=name, description=description, location=location, average_rating=0)
    db.session.add(eatery)
    db.session.commit()
    return success_response(eatery.serialize(), 201)

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

@app.route("/api/eateries/<int:eatery_id>/reviews/")
def get_eatery_reviews(eatery_id):
    """
    Get all reviews for this eatery
    """
    eatery = Eatery.query.filter_by(id=eatery_id).first()
    if eatery is None:
        return failure_response("eatery not found")
    reviews = Review.query.filter_by(eatery_id=eatery_id)
    return success_response({"reviews": [ r.serialize() for r in reviews ]})

@app.route("/api/eateries/<int:eatery_id>/rating/")
def get_average_rating_eatery(eatery_id):
    """
    Get the average rating of an eatery
    """
    eatery = Eatery.query.filter_by(id=eatery_id).first()
    if eatery is None:
        return failure_response("eatery not found")
    return success_response({"average_rating": eatery.average_rating})

# -- REVIEW ROUTES ----------------------------------------------------------

@app.route("/api/reviews/")
def get_reviews():
    """
    Get all reviews
    """
    reviews = Review.query.all()
    return success_response({"reviews": [ r.serialize() for r in reviews ]})

@app.route("/api/reviews/<int:review_id>/")
def get_review_by_id(review_id):
    """
    Get review by id
    """
    review = Review.query.filter_by(id=review_id).first()
    if review is None:
        return failure_response("review not found")
    return success_response(review.serialize())

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
    # Update all user rankings; update this user's average rating; update this eatery's average rating
    update_user_rankings()
    update_user_average_rating(user_id)
    update_eatery_average_rating(eatery_id)

    return success_response(review.serialize(), 201)

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

    update_user_rankings()
    update_user_average_rating(review.user_id)
    update_eatery_average_rating(review.eatery_id)

    return success_response(review.serialize())

@app.route("/api/reviews/<int:review_id>/", methods=["PUT"])
def edit_review(review_id):
    """
    Edit a review by id
    """
    review = Review.query.filter_by(id=review_id).first()
    if review is None:
        return failure_response("review not found")

    try:
        body = json.loads(request.data)
    except:
        return failure_response("Invalid JSON format!", 400)
   
    rating = body.get("rating", review.rating)
    review_text = body.get("review_text", review.review_text)
    timestamp = datetime.datetime.now()
    if not (1 <= rating <= 10):
        return failure_response("rating must be between 1 and 10", 400)
    review.rating = rating
    review.review_text = review_text
    review.timestamp = timestamp

    db.session.commit()

    update_user_average_rating(review.user_id)
    update_eatery_average_rating(review.eatery_id)

    return success_response(review.serialize())
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)