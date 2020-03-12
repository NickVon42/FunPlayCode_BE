from database import db
from sqlalchemy import inspect
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from flask import current_app

class Story(db.Model):
    __tablename__='story'

    id = db.Column(db.Integer, unique = True, autoincrement = True, primary_key = True)
    title = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    #Relationships
    chapters = db.relationship('Chapter', backref='story', lazy='dynamic', uselist=True, cascade="all, delete-orphan")

    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
    #return 'Point(x=%s, y=%s)' % (self.x, self.y)
    #this is to create like a printable object
    def __repr__(self):
        return '<ID: %s; Title: %s; Description: %s>' % (
            self.id, self.title, self.description)

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, unique = True, autoincrement = True, primary_key = True)
    email = db.Column(db.String(35), unique = True, nullable = False)
    username = db.Column(db.String(20), unique=True, nullable = False)
    password = db.Column(db.String(15), nullable = False)
    authenticated = db.Column(db.Boolean, default=False, nullable = False)

    #Relationships
    stories = db.relationship('Story', backref='user', lazy='dynamic', uselist=True)
    chapters = db.relationship('Chapter', backref='chap_user', lazy='dynamic', uselist=True)

    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    def generate_auth_token(self, expiration=600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = User.query.get(data['id'])
        return user

    #def hash_password(self, password):
        #self.password_hash = pwd_context.encrypt(password)

   # def verify_password(self, password):
        #return pwd_context.verify(password, self.password_hash)

    def is_active(self):
        ##True, all users are considered active
        return True

    def get_id(self):
        ##return unique username to satisfy the Flask-Login requirements
        return self.username

    def is_authenticated(self):
        ##Returns true if the user is authenticated
        return self.authenticated

    def is_anonymous(self):
        ##Returns like, Guest User
        return False

    def __repr__(self):
        return '<Id: %s; Email: %s; Username: %s>' % (
            self.id, self.email, self.username)

class Chapter(db.Model):
    __tablename__ = 'chapter'

    id = db.Column(db.Integer, unique = True, autoincrement=True, primary_key = True)
    name = db.Column(db.String(50), unique = True, nullable = False)
    codes = db.Column(db.Text, nullable = False)
    story_id = db.Column(db.Integer, db.ForeignKey('story.id'), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    #Relationship
    #story = db.relationship('Story', back_populates='chapters')
    def __repr__(self):
        return '<ID: %s; Name: %s>' % (
            self.id, self.name)