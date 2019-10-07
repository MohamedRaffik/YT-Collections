from flask import Flask, render_template, redirect
from flask_cors import CORS
from flask_login import LoginManager, current_user
from os import getenv, urandom, environ
from redis import Redis
from rq import Queue

STATIC_FOLDER = 'dist'

if getenv('FLASK_ENV') == 'development':
    from dotenv import load_dotenv

    STATIC_FOLDER = 'build'
    load_dotenv('.env')
    environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    

app = Flask(__name__, static_folder=f'../client/{STATIC_FOLDER}', static_url_path='/', template_folder=f'../client/{STATIC_FOLDER}')
app.secret_key = urandom(16)

queue = Queue('tasks', connection=Redis.from_url('redis://'))

login_manager = LoginManager(app)

from server.models.users import User

@login_manager.user_loader
def load_user(email):
    return User.get(email)

CORS(app)

from server.routes.auth import auth
from server.routes.subscriptions import subscriptions

@subscriptions.before_request
def f():
    if not current_user.is_authenticated:
        return ('/')

app.register_blueprint(auth, url_prefix='/api/auth')
app.register_blueprint(subscriptions, url_prefix='/api/subscriptions')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    return render_template('index.html')