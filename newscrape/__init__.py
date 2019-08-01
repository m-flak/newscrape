import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from newscrape.main.controllers import main
from newscrape.api.controllers import api
from .utils import get_secret_key

db  = SQLAlchemy()
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://newscrape:newscraper1@localhost/newscrape"
get_secret_key(app)
db.init_app(app)
login = LoginManager()
login.login_view = 'main.welcome'
login.init_app(app)
bootstrap = Bootstrap()
bootstrap.init_app(app)

app.register_blueprint(main, url_prefix='/')
app.register_blueprint(api, url_prefix='/api')

from newscrape import models
