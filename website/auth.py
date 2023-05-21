from datetime import datetime

from flask import Blueprint, redirect, render_template, request, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for, session, flash)

auth = Blueprint('auth', __name__)
users = db.Users


# Logging in the user
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if "username" in session:
        return redirect(url_for("views.editor"))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = users.find_one({"email": email})
        if user:
            if check_password_hash(user['password'], password):
                session["username"] = user['username']
                # BUGGED OUT FIX LATER
                # flash('Logged in successfully!', category='success')
                return redirect(url_for('views.editor'))
            else:
                if "username" in session:
                    return redirect(url_for('views.editor'))
                flash('Incorrect password, try again.', category='error')

        else:
            flash("Username does not exist, try registering an account!", category='error')

    return render_template("login.html", user=False)


# Logging out the user
@auth.route('/logout')
def logout():
    if "username" in session:
        session.pop('username', None)
        return redirect(url_for("views.index"))
    return redirect(url_for('views.index'))


# Registering the user
@auth.route('/register', methods=['GET', 'POST'])
def register():
    print(session)
    if "username" in session:
        print(session)
        return redirect(url_for("views.editor"))

    if request.method == 'POST':
        username = request.form['name']
        email = request.form['email']
        password1 = request.form['password']
        password2 = request.form['password2']

        user = users.find_one({"email": email})
        if user:
            flash("Email already exists!", category='error')
        elif password1 != password2:
            flash("Passwords must match!", category='error')
        elif len(username) > 100:
            flash("Business name is over 24 chars!", category='error')
        elif len(username) < 2:
            flash("Business name to short!", category='error')
        else:
            print(email)
            user_input = {'username': username,
                          'email': email,
                          'password': generate_password_hash(password1, method='sha256'),
                          'profile_picture': '',
                          'banner': '',
                          'bio': '',
                          'posts': [],
                          'timestamp': datetime.utcnow(),
                          'address': '',
                          'link_url': ''
                          }
            users.insert_one(user_input)
            return redirect(url_for('views.about'))

    return render_template("signup.html", user=False)
