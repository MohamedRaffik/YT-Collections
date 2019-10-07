from flask import Blueprint
from flask_login import current_user
from os import getenv
from requests import get

subscriptions = Blueprint(__name__, 'subscriptions')

@subscriptions.route('/page/<page>')
def index(page):
    if current_user.job_id:
        return { 'success': False }, 202

    total_pages, subs = current_user.get_subscriptions(page=int(page))

    params = {
        'part': 'snippet',
        'id': ','.join(subs),
        'key': getenv('API_KEY')
    }

    info = get('https://www.googleapis.com/youtube/v3/channels', params=params).json()

    subs_info = [
        {
            'id': item['id'],
            'title': item['snippet']['title'],
            'thumbnail': item['snippet']['thumbnails']['medium']
        }
        for item in info['items']
    ]

    return { 'total_pages': total_pages , 'subscriptions': subs_info }