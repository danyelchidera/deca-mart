from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///decaMart.db'
app.config['SECRET_KEY'] = '05d859a0f7e32182c3bacc8b'

# File Upload Folder
UPLOAD_FOLDER = '/Users/hp/Desktop/group_4_project/Deca-Mart/core/static/media'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


# File upload config
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app) 
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
from core import routes