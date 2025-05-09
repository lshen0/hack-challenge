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
    follower_count = db.Column(db.Integer, default=0)
    following_count = db.Column(db.Integer, default=0)

    # Relationships: 1 user to many reviews; many users to many connections
    # This user's followers are instances where this user's id is the following id in Connection
    followers = db.relationship("Connection", foreign_keys="[Connection.following_id]", back_populates="following",  cascade="delete")
    # This user's following are instances where this user's id is the follower id in Connection
    following = db.relationship("Connection", foreign_keys="[Connection.follower_id]", back_populates="follower",  cascade="delete")
    # 1
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
        self.average_rating = 0
        self.ranking = 0 # ranking 0 means you haven't ranked eateries yet
        # ranking is given based on number of reviews, then recency of reviews (in case of tie)
        self.follower_count = 0
        self.following_count = 0
 
    def simple_serialize(self):
        """
        Simple serialize User object (without reviews and followers/following).
        """
        return {
            "id": self.id,
            "name": self.name,
            "username": self.username,
            "bio": self.bio,
            "location": self.location,
            "timestamp": self.timestamp.isoformat(),
            "ratings_count": self.ratings_count,
            "average_rating": self.average_rating,
            "ranking": self.ranking,
            "follower_count": self.follower_count,
            "following_count": self.following_count 
        }

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
            "average_rating": self.average_rating,
            "ranking": self.ranking,
            "follower_count": self.follower_count,
            "following_count": self.following_count,
            "reviews": [ r.serialize() for r in self.reviews ]
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
        db.CheckConstraint("follower_id != following_id", name="check_not_following_self")
    )

    # Relationships: many-to-many with User
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
            "follower": self.follower.simple_serialize() if self.follower else None,
            "following": self.following.simple_serialize() if self.following else None,
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
    location = db.Column(db.String, nullable=True) 
    average_rating = db.Column(db.Float, default=0)

    # Relationship: 1 eatery to many reviews
    reviews = db.relationship("Review", back_populates="eatery",  cascade="delete")

    def __init__(self, **kwargs):
        """
        Initialize Eatery object.
        """
        self.name = kwargs.get("name")
        self.description = kwargs.get("description")
        self.location = kwargs.get("location")
        self.average_rating = 0

    def serialize(self):
        """
        Serialize Eatery object (without reviews).
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "location": self.location,
            "average_rating": self.average_rating
        }

class Review(db.Model):
    """
    Review model.
    Each row is a rating (float 1-10) and optional review by one user for one eatery.
    """
    __tablename__ = "review"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    eatery_id = db.Column(db.Integer, db.ForeignKey("eatery.id"), nullable=False)
    rating = db.Column(db.Float, nullable=False)  # 1-10 value
    review_text = db.Column(db.String, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)

    # Table constraints: rating must be between 0 and 10
    __table_args__ = (
        db.CheckConstraint("rating >= 1 AND rating <= 10", name="checking_rating_range"),
        db.UniqueConstraint("user_id", "eatery_id", name='unique_user_eatery_review')
    ) 

    # Relationship: many reviews to 1 user, many reviews to 1 eatery
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