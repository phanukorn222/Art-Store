from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from app import db
from .favourite_art import FavouriteArt
from .buyer import Buyer
from datetime import datetime

class Art(db.Model, UserMixin, SerializerMixin):
    __tablename__ = 'arts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    price = db.Column(db.BigInteger, nullable=False)
    detail = db.Column(db.String(600), nullable=False)
    img_url = db.Column(db.String(1000), nullable=False)
    type = db.Column(db.Integer, nullable=False)
    sold = db.Column(db.Boolean, default=False, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('auth_users.id'), nullable=False)
    favourites = db.relationship('FavouriteArt', cascade="all,delete", backref='art')
    buyers = db.relationship('Buyer', cascade="all,delete", backref='art')

    def __init__(self, title, price, detail, img_url, type, user_id):
        self.title = title
        self.price = price
        self.detail = detail
        self.img_url = img_url
        self.type = type
        self.user_id = user_id
    
    def update(self, title, price, detail, type):
        self.title = title
        self.price = price
        self.detail = detail
        self.type = type

    def update_sold(self, sold):
        self.sold = sold
