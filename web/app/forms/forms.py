from flask_wtf import FlaskForm
from wtforms import (StringField, EmailField, PasswordField, BooleanField, IntegerField, TextAreaField, SelectField, HiddenField )
from wtforms.validators import InputRequired, Length , NumberRange
from flask_wtf.file import FileField, FileAllowed, FileRequired
import re
from app import images

class SignUpForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(),
                                             Length(min=4, max=24)])
    email = EmailField('Email', validators=[InputRequired(),
                                            Length(max=255)])
    password = PasswordField('Password', validators=[InputRequired(), Length(max=100)])

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[InputRequired(),
                                            Length(max=255)])
    password = PasswordField('Password', validators=[InputRequired(), Length(max=100)])
    remember = BooleanField('Remember me')

class ProfileForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(),
                                             Length(min=4, max=24)])
    email = EmailField('Email', validators=[InputRequired(),
                                            Length(max=255)])
    password = PasswordField('Password', validators=[InputRequired(), Length(max=100)])

class EditArtForm(FlaskForm):
    title = StringField('Name of Artwork', validators=[InputRequired(),
                                             Length(max=30)])
    price = IntegerField('Price', validators=[InputRequired(),NumberRange(min=1, max=9999999999,)])
    type = SelectField('Type of Artwork', choices=[(1,'Oil'), (2,'Acrylic'), (3,'Watercolors'), (4, 'Gouache'), (5, 'Pastels'), (6, 'Encaustic'), (7, 'Ink painting'), (8, 'Digital painting'), (9, 'Other')], validators=[InputRequired()])
    detail = TextAreaField('Detail', validators=[InputRequired(),
                                             Length(max=600)] , render_kw={'class': 'form-control', 'rows': 7})
class CreateArtForm(FlaskForm):
    title = StringField('Name of Artwork', validators=[InputRequired(),
                                             Length(max=30)])
    price = IntegerField('Price', validators=[InputRequired(),NumberRange(min=1, max=9999999999,)])
    type = SelectField('Type of Artwork', choices=[(1,'Oil'), (2,'Acrylic'), (3,'Watercolors'), (4, 'Gouache'), (5, 'Pastels'), (6, 'Encaustic'), (7, 'Ink painting'), (8, 'Digital painting'), (9, 'Other')], validators=[InputRequired()])
    detail = TextAreaField('Detail', validators=[InputRequired(),
                                             Length(max=600)], render_kw={'class': 'form-control', 'rows': 7})
    image = FileField('Image Upload', [FileRequired(), FileAllowed(images, 'File upload is support only image.')])

class FavouriteArtFrom(FlaskForm):
    art_id = HiddenField(validators=[InputRequired()])

class SearchForm(FlaskForm):
    search = StringField(validators=[Length(max=30)])

class FilterForm(FlaskForm):
    type = SelectField(choices=[(0,'All'), (1,'Oil'), (2,'Acrylic'), (3,'Watercolors'), (4, 'Gouache'), (5, 'Pastels'), (6, 'Encaustic'), (7, 'Ink painting'), (8, 'Digital painting'), (9, 'Other')], validators=[InputRequired()])
