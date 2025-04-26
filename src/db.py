from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

class User(db.Model):
    """
    User model.
    Many-to-many relationship with Connection.
    """
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False)
    bio = db.Column(db.String, nullable=True)
    location = db.Column(db.String, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    ratings_count = db.Column(db.Integer, default=0)
    average_rating = db.Column(db.Float, default=0)
    ranking = db.Column(db.Integer, default=0)
    # TODO: badges

    # This user's followers are instances where this user's id is the following id in Connection
    followers = db.relationship("Connection", foreign_keys="[Connection.following_id]", back_populates="following")
    # This user's following are instances where this user's id is the follower id in Connection
    following = db.relationship("Connection", foreign_keys="[Connection.follower_id]", back_populates="follower")

    def __init__(self, **kwargs):
        """
        Initialize User object.
        """
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.username = kwargs.get("username")
        self.bio = kwargs.get("bio")
        self.location = kwargs.get("location")
        self.timestamp = datetime.datetime.now()
        # TODO: self.ratings_count = calculate!! # TODO 
        # TODO: self.average_rating = calculate!!
        # TODO: self.ranking
        # TODO: self.badges = calculate!!

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
            "ranking": self.ranking
            # TODO: badges
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
    timestamp = db.Column(db.DateTime,nullable=False) 

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
        self.id = kwargs.get("id")
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
    Many-to-many relationship with Review.
    """
    __tablename__ = "eatery"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String(150), nullable=True)
    cuisine = db.Column(db.String, nullable=True) # TODO: maybe input as comma separated values?
    location = db.Column(db.String, nullable=True) 
    average_rating = db.Column(db.Float, default=0)
    # TODO: reviews

    def __init__(self, **kwargs):
        """
        Initialize Eatery object.
        """
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.description = kwargs.get("description")
        self.cuisine = kwargs.get("cuisine")
        self.location = kwargs.get("location")
        # TODO: self.average_rating = calculate!!

        # TODO: relationships.

    def serialize(self):
        """
        Serialize Eatery object (without reviews).
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.name,
            "cuisine": self.cuisine,
            "location": self.location,
            "average_rating": self.average_rating
        }
