from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from .art import Art
from .buyer import Buyer
from app import db

class AuthUser(db.Model, UserMixin, SerializerMixin):
    __tablename__ = "auth_users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    avatar_url = db.Column(db.String(100))
    arts = db.relationship('Art', cascade="all,delete", backref='user')
    buys = db.relationship('Buyer', cascade="all,delete", backref='user')

    def __init__(self, email, password, name, avatar_url):
        self.email = email
        self.password = password
        self.name = name
        self.avatar_url = avatar_url
    
    def update(self, email, name, avatar_url):
        self.email = email
        self.name = name
        self.avatar_url = avatar_url