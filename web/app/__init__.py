import os
from flask import Flask
from werkzeug.debug import DebuggedApplication
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
from flask_login import LoginManager
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__, static_folder='static')
# this DEBUG config here will be overridden by FLASK_DEBUG shell environment
app.config['DEBUG'] = False
app.config['SECRET_KEY'] = 'a8112ea716969327fc2a49fc8dd0e2ca9fa484033e771552'
app.config['JSON_AS_ASCII'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite://")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['GOOGLE_CLIENT_ID'] = os.getenv("GOOGLE_CLIENT_ID", None)
app.config['GOOGLE_CLIENT_SECRET'] = os.getenv("GOOGLE_CLIENT_SECRET", None)
app.config['GOOGLE_DISCOVERY_URL'] = os.getenv("GOOGLE_DISCOVERY_URL", None)
app.config['GOOGLE_AUTHORIZE_URL'] = os.getenv("GOOGLE_AUTHORIZE_URL", None)
app.config['UPLOADED_PHOTOS_DEST'] = 'static/uploads'

if app.debug:
    app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)

# Creating an SQLAlchemy instance
db = SQLAlchemy(app)
csrf = CSRFProtect(app)
oauth = OAuth(app)
images = UploadSet('photos', IMAGES)
configure_uploads(app, images)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)
from app import views  # noqa