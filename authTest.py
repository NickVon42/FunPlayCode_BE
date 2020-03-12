from classes import User, Story
from flask import Blueprint
from flask import render_template
from flask import request, redirect, url_for, jsonify
from database import db, login_manager
from flask_login import login_required, login_user, logout_user,current_user
import json
import re


authTest_blueprint = Blueprint('authTest',__name__, template_folder="/main/static/templates")


##LOGIN FOR USER AND PREVENT NON-USER FROM POSTING
@login_manager.user_loader
def user_loader(user_id):
    user = User.query.filter_by(username=user_id).first()
    return user

@authTest_blueprint.route("/login", methods = ["GET","POST"])
def loginHandler():
    error = None

    if request.method == 'POST':
        if request.json:
            username = request.json.get('username')
            password = request.json.get('password')
        else:
            username = request.form.get('username')
            password = request.form.get('password')
        checkUser = User.query.filter_by(username=username).first()

        if checkUser == None:
            error = 'User does not exist!'
        else:
            user = User.query.filter_by(username=username).first()
            if password == user.password:
                user.authenticated = True
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=True)

                if request.json:
                    return jsonify({'message': 'Data Matched'})
                else:
                    return render_template('welcome.html', user=user)
            else:
                error = 'Incorrect Password!'
    return render_template('login.html', error=error)

@authTest_blueprint.route("/logout", methods=["GET"])
@login_required
def logout():
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return render_template("login.html")

@authTest_blueprint.route("/register", methods=["POST", "GET"])
def registerHandler():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        authenticated = False

        ## Check Email Validity and Username Availability
        email_valid = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email)
        if email_valid == None:
            error = "Please enter a valid email address!"
        else:
            checkUser = User.query.filter_by(username=username).first()
            if checkUser != None:
                error = "Username is taken! Please try again!"
            else:
                ## Add user to database
                user = User(email=email, username=username, password=password, authenticated=authenticated)
                db.session.add(user)
                db.session.commit()
                ##Login user
                user.authenticated = True
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=True)
                return redirect(url_for('authTest.welcome', user=user))
    return render_template('register.html', error=error)

@authTest_blueprint.route("/home")
def welcome():
    isUser = None
    notGuest = None
    user = current_user
    if user.is_authenticated == False:
        user.username = 'Guest'
        notGuest = True
    else:
        isUser = True
    return render_template('welcome.html', user=user, notGuest=notGuest, isUser=isUser)

