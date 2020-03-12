from classes import Story, Chapter, User
from flask import Blueprint, abort, request, jsonify, g, url_for
from database import db, login_manager
from flask_login import login_required, login_user, logout_user, current_user
import re
from flask_httpauth import HTTPBasicAuth

APIUser_blueprint = Blueprint('APIUserRoute', __name__)
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@APIUser_blueprint.route('/api/users', methods=['POST'])
def verify_user():
    username = request.json.get('username')
    password = request.json.get('password')
    user = User.query.filter_by(username=username).first()
    print(username + password)
    print(user.username + user.password)
    if username is None or password is None:
        abort(400)    # missing arguments
        print('hey')

    if user.username == username and user.password == password:
        print(user.id)
        return jsonify({'user_name': user.username, 'user_id': user.id})

    if user.username != username or user.password != password:
        return jsonify({'status': 'Wrong username or password'})
        print('hey')

    return jsonify({'status': 'User logged in.'})

@APIUser_blueprint.route('/api/users', methods=['GET'])
def get_users():
    users=User.query.all()
    user_list = []

    for user in users:
        user_list.append(user.as_dict())

    user_json = {
        'users': user_list,
    }
    return jsonify(user_json)


@APIUser_blueprint.route('/api/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'status': 'Wrong username or password'})
    print(user.username)

    user_json = {
        'userName': user.username,
        'userId': user.id
    }
    return jsonify(user_json)


@APIUser_blueprint.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})


@APIUser_blueprint.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.username})































@APIUser_blueprint.route("/mobilelogin", methods = ["GET","POST"])
def loginHandler():
    username = request.json.get('username')
    password = request.json.get('password')
    print(username)
    print(password)
    checkUser = User.query.filter_by(username=username).first()

    if checkUser == None:
        return jsonify({'message': 'User does not exist'})
    else:
        user = User.query.filter_by(username=username).first()
        if password == user.password:
            user.authenticated = True
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True)
            return jsonify({'message': 'Data Matched'})
        else:
            return jsonify({'message': 'Incorrect password'})


@APIUser_blueprint.route("/mobile_register", methods=["POST", "GET"])
def registerHandler():
    error = None
    if request.method == 'POST':
        email = request.json.get('email')
        username = request.json.get('username')
        password = request.json.get('password')
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
    return jsonify({'message': ' user created'}), 200
