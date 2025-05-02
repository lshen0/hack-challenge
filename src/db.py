from flask_sqlalchemy import SQLAlchemy
import datetime
from sqlalchemy import func, event
from sqlalchemy.orm import Session

db = SQLAlchemy()

class User(db.Model):
    """
    User model.
    Many-to-many relationship with Connection.
    """
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    bio = db.Column(db.String, nullable=True)
    location = db.Column(db.String, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    ratings_count = db.Column(db.Integer, default=0)
    average_rating = db.Column(db.Float, default=0)
    ranking = db.Column(db.Integer, default=0)

    # Relationships
    # This user's followers are instances where this user's id is the following id in Connection
    followers = db.relationship("Connection", foreign_keys="[Connection.following_id]", back_populates="following",  cascade="delete")
    # This user's following are instances where this user's id is the follower id in Connection
    following = db.relationship("Connection", foreign_keys="[Connection.follower_id]", back_populates="follower",  cascade="delete")
    # Review
    reviews = db.relationship("Review", back_populates="user", cascade="delete")

    def __init__(self, **kwargs):
        """
        Initialize User object.
        """
        self.name = kwargs.get("name")
        self.username = kwargs.get("username")
        self.bio = kwargs.get("bio", "")
        self.location = kwargs.get("location", "")
        self.timestamp = datetime.datetime.now()
        self.ratings_count = 0
        # TODO: self.average_rating = calculate!!
        self.ranking = 0

    def serialize(self):
        """
        Serialize User object (without followers/following).
        """
        return {
            "id": self.id,
            "name": self.name,
            "username": self.username,
            "bio": self.bio,
            "location": self.location,
            "timestamp": self.timestamp.isoformat(),
            "ratings_count": self.ratings_count,
            # "average_rating": self.average_rating,
            "ranking": self.ranking,
            "reviews": [ r.serialize() for r in self.reviews ]
            # TODO: followers/following
        }

class Connection(db.Model):
    """ 
    Connection model.
    Many-to-many relationship with User.
    """
    __tablename__ = "connection"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    follower_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    following_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    timestamp = db.Column(db.DateTime,nullable=False, default=datetime.datetime.now) 

    # Connections must be unique
    __table_args__ = (
        db.UniqueConstraint("follower_id", "following_id", name='unique_user_connection'),
    )

    # TODO: check follower/following logic
    follower = db.relationship("User", foreign_keys=[follower_id], back_populates="following")
    following = db.relationship("User", foreign_keys=[following_id], back_populates="followers")

    def __init__(self, **kwargs):
        """
        Initialize Connection object.
        """
        self.follower_id = kwargs.get("follower_id")
        self.following_id = kwargs.get("following_id")
        self.timestamp = datetime.datetime.now()

    def serialize(self):
        """
        Serialize Connection object.
        """
        return {
            "id": self.id,
            "follower": self.follower.serialize() if self.follower else None,
            "following": self.following.serialize() if self.following else None,
            "timestamp": self.timestamp.isoformat()
        }
    
class Eatery(db.Model):
    """
    Eatery model.
    """
    __tablename__ = "eatery"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String(150), nullable=True)
    cuisine = db.Column(db.String, nullable=True) # TODO: maybe input as comma separated values?
    location = db.Column(db.String, nullable=True) 
    average_rating = db.Column(db.Float, default=0)
    # TODO: reviews
    reviews = db.relationship("Review", back_populates="eatery",  cascade="delete")


    def __init__(self, **kwargs):
        """
        Initialize Eatery object.
        """
        self.name = kwargs.get("name")
        self.description = kwargs.get("description", "")
        self.cuisine = kwargs.get("cuisine", "")
        self.location = kwargs.get("location", "")
        # TODO: self.average_rating = calculate!!
        # self.average_rating = 0

    def serialize(self):
        """
        Serialize Eatery object (without reviews).
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "cuisine": self.cuisine,
            "location": self.location,
            "average_rating": self.average_rating
        }

class Review(db.Model):
    """
    Review model.
    Each row is a rating (1-10) and optional review by one user for one eatery.
    Many-to-many relationship with Eatery.
    """
    __tablename__ = "review"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    eatery_id = db.Column(db.Integer, db.ForeignKey("eatery.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-10 value
    review_text = db.Column(db.String, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)

    # Table constraints: rating must be between 0 and 10
    __table_args__ = (
        db.CheckConstraint("rating >= 1 AND rating <= 10", name="checking_rating_range"),
    ) # TODO: should we check this and raise a value error instead?

    # Relationships
    user = db.relationship("User", back_populates="reviews")
    eatery = db.relationship("Eatery", back_populates="reviews")

    def __init__(self, **kwargs):
        self.user_id = kwargs.get("user_id")
        self.eatery_id = kwargs.get("eatery_id")
        self.rating = kwargs.get("rating")            
        self.review_text = kwargs.get("review_text")
        self.timestamp = datetime.datetime.now()

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "eatery_id": self.eatery_id,
            "rating": self.rating,
            "review_text": self.review_text,
            "timestamp": self.timestamp.isoformat()
        }

def update_user_rankings():
    """
    Updates each user's ranking based on how many reviews they have written.
    More reviews = higher rank (lower number).
    """
    session: Session = db.session  # Get current SQLAlchemy session

    # Query review count for each user, ordered by count descending
    user_review_counts = session.query(
        Review.user_id,
        func.count(Review.id).label("review_count")
    ).group_by(Review.user_id).order_by(func.count(Review.id).desc()).all()

    # Assign ranking based on index in sorted list (starting from 1)
    for rank, (user_id, count) in enumerate(user_review_counts, start=1):
        user = session.get(User, user_id)
        if user:
            user.ranking = rank
            user.ratings_count = count  # Optional: keep this in sync

    session.commit()