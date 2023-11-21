from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from app import db
from datetime import datetime

class FavouriteArt(db.Model, UserMixin, SerializerMixin):
    __tablename__ = 'favourite_arts'

    id = db.Column(db.Integer, primary_key=True)
    art_id = db.Column(db.Integer, db.ForeignKey('arts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('auth_users.id'), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, art_id, user_id):
        self.art_id = art_id
        self.user_id = user_id