"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    return render_template("homepage.html")


@app.route('/register', methods=['GET'])
def register_form():

    return render_template("register_form.html")


@app.route('/register', methods=['POST'])
def register():

    user_email = request.form.get('email')
    user_password = request.form.get('password')
    user_age = request.form.get('age')
    user_zipcode = request.form.get('zipcode')

    email_list = db.session.query(User.email).all()
    for email in email_list:

        if user_email == email[0]:
            flash("The email has been used to register.")
            return redirect('/')
        
    user = User(email=user_email, 
                password=user_password, 
                age=user_age, 
                zipcode=user_zipcode)

    db.session.add(user)

    db.session.commit()

    return redirect('/')


@app.route('/login', methods=['GET'])
def login_form():

    return render_template("login_form.html")


@app.route('/login', methods=['POST'])
def login():

    user_email = request.form.get('email')
    user_password = request.form.get('password')

    user = db.session.query(User).filter(User.email == user_email).first()

    if not user:
        flash("No such user.")
        return redirect('/login')

    if user_password != user.password:
        flash("Incorrect password.")
        return redirect('/login')
    else:
        flash("Logged in.")
        session['user_id'] = user.user_id
        return redirect('/')


@app.route('/logout')
def logout():
    del session['user_id']
    flash("Logged Out.")
    return redirect('/')


@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
