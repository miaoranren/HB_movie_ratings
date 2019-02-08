"""Models and database functions for Ratings project."""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from correlation import pearson

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of ratings website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=True)
    password = db.Column(db.String(64), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    zipcode = db.Column(db.String(15), nullable=True)

    movies = db.relationship("Movie",
                                secondary="ratings",
                                backref="users")

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"<User user_id={self.user_id} email={self.email}>"



    def similarity(self, other):
        """Return Pearson rating for user compared to other user."""

        u_ratings = {}
        paired_ratings = []

        for r in self.ratings:
            u_ratings[r.movie_id] = r

        for r in other.ratings:
            u_r = u_ratings.get(r.movie_id)
            if u_r:
                paired_ratings.append( (u_r.score, r.score) )

        if paired_ratings:
            return pearson(paired_ratings)

        else:
            return 0.0


    def predict_rating(self, movie):
        """Predict user's rating of a movie."""

        other_ratings = movie.ratings

        similarities = [
            (self.similarity(r.user), r)
            for r in other_ratings
        ]

        similarities = sorted(similarities, reverse=True, key=lambda x: x[0])
        sim, rating = similarities[0]

        return rating.score * sim

    # def predict_rating(self, movie):
    #     """Predict user's rating of a movie."""

    #     other_ratings = movie.ratings
    #     other_users = [ r.user for r in other_ratings ]

    #     similarities = [
    #         (self.similarity(other_user), other_user)
    #         for other_user in other_users
    #     ]

    #     similarities = sorted(similarities, reverse=True, key=lambda x: x[0])
    #     sim, best_match_user = similarities[0]

    #     for rating in other_ratings:
    #         if rating.user_id == best_match_user.user_id:
    #             return rating.score * sim



# Put your Movie and Rating model classes here.
class Rating(db.Model):

    __tablename__ = "ratings"

    rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    movie_id = db.Column(db.Integer,
                        db.ForeignKey('movies.movie_id'))
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.user_id'))
    score = db.Column(db.Integer)

    user = db.relationship("User", 
                            backref=db.backref("ratings"))

    movie = db.relationship("Movie", 
                            backref=db.backref("ratings"))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"""<Rating rating_id={self.rating_id}
                movie_id={self.movie_id}
                user_id={self.user_id}>"""



class Movie(db.Model):
    __tablename__ = "movies"

    movie_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(128))
    release_at = db.Column(db.DateTime)
    imdb_url = db.Column(db.String(200))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"<Movie movie_id={self.movie_id} title={self.title}>"



##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ratings'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    # db.create_all()
    print("Connected to DB.")
