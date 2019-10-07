from flask import Blueprint, url_for, session, redirect, request
from flask_login import login_user, current_user
from server import queue
from server.models.users import User
import server.utils.google_api as google_api
from datetime import datetime, timedelta

auth = Blueprint(__name__, 'auth')

scopes = [
    'https://www.googleapis.com/auth/userinfo.email',
    'openid', 
    'https://www.googleapis.com/auth/youtube' 
]

@auth.route('/login')
def login():
    if current_user.is_authenticated:
        return { 'username': current_user.get_id(), 'redirect': False } 

    session['state'], url = google_api.create_oauth_url(url_for('server.routes.auth.callback', _external=True))
    return { 'redirect': True, 'redirect_url': url }

@auth.route('/oauth2callback')
def callback():
    if session.get('error', None):
        return redirect('/')

    if session['state'] != request.args.get('state', None):
        return redirect('/')

    tokens = google_api.get_oauth_tokens(url_for('server.routes.auth.callback', _external=True), request.args['code'])
    email = google_api.get_user_email(tokens['access_token'])
    user = User.get(email)

    if not user:
        user = User(
            _id=email,
            subscriptions=[],
            collections={},
            credentials=google_api.create_credentials(tokens),
            job_id=None,
            last_updated=datetime.utcnow()
        )
        job = queue.enqueue('server.utils.google_api.build_collections', access_token=tokens['access_token'], username=email)
        user.job_id = job.id
        user.insert()
    else:
        user.update({'credentials': google_api.create_credentials(tokens)})
    
    login_user(user, remember=True, duration=timedelta(30))

    return redirect('/')
