from server.models.users import User
from queue import Queue
from threading import Thread
from requests import get, post
from urllib import parse
from base64 import b64encode
from os import getenv, urandom
from time import sleep

scopes = [
    'https://www.googleapis.com/auth/userinfo.email',
    'openid', 
    'https://www.googleapis.com/auth/youtube' 
]

def create_oauth_url(callback_url: str) -> tuple:
    params = {
        'client_id': getenv('CLIENT_ID'),
        'redirect_uri': callback_url,
        'scope': ' '.join(scopes),
        'response_type': 'code',
        'access_type': 'offline',
        'include_granted_scopes': 'true',
        'state': b64encode(urandom(16)).decode('utf-8'),
    }
    url = 'https://accounts.google.com/o/oauth2/v2/auth?' + parse.urlencode(params)
    return ( params['state'], url )


def get_oauth_tokens(callback_url: str, code: str) -> dict:
    params = {
        'code': code,
        'client_id': getenv('CLIENT_ID'),
        'client_secret': getenv('CLIENT_SECRET'),
        'redirect_uri': callback_url,
        'grant_type': 'authorization_code'
    }
    return post('https://oauth2.googleapis.com/token', data=params).json()


def get_user_email(access_token: str) -> str:
    return get(
        url='https://www.googleapis.com/oauth2/v2/userinfo', 
        headers={ 'Authorization': f'Bearer {access_token}' },
        params={ 'fields': 'email' }
    ).json()['email']


def create_credentials(oauth_response: dict) -> dict:
    return {
        'access_token': oauth_response['access_token'], 
        'refresh_token': oauth_response['refresh_token'],
        'expires in': oauth_response['expires_in'],
        'scope': oauth_response['scope']
    }


def build_collections(access_token: str, username: str):
    subs, info = [], { 'nextPageToken': '' }
    q = Queue()
    threads = []

    params = {
        'part': 'snippet',
        'mine': True,
        'maxResults': 50,
        'pageToken': info['nextPageToken']
    }

    while 'nextPageToken' in info:
        info = get(
            url='https://www.googleapis.com/youtube/v3/subscriptions',
            headers={ 'Authorization': f'Bearer {access_token}' }, 
            params={**params, 'pageToken': info['nextPageToken']}
        ).json()
        subs.append({ item['snippet']['resourceId']['channelId']: None for item in info['items'] }) 
        threads.append( Thread(target=getTopics, args=(subs[-1].keys(), q)) )
        threads[-1].start()

    topic_map = {
        '/m/04rlf': 'Music',
        '/m/0bzvm2': 'Gaming',
        '/m/06ntj': 'Sports',
        '/m/02jjt': 'Entertainment',
        '/m/019_rr': 'Lifestyle',
        '/m/01k8wb': 'Knowledge',
        '/m/098wr': 'Society'
    }

    collections = {
        'Music': [ {} ],
        'Gaming': [ {} ],
        'Sports': [ {} ],
        'Entertainment': [ {} ],
        'Lifestyle': [ {} ],
        'Knowledge': [ {} ],
        'Society': [ {} ]
    }

    pages = {
        'Music': 0,
        'Gaming': 0,
        'Sports': 0,
        'Entertainment': 0,
        'Lifestyle': 0,
        'Knowledge': 0,
        'Society': 0
    }

    for thread in threads:
        thread.join()

        info = q.get()

        for item in info['items']:
            if 'topicDetails' in item:
                for topic in set(item['topicDetails']['topicIds']):
                    if topic in topic_map:
                        t = topic_map[topic]
                        if len(collections[t][pages[t]]) == 50:
                            collections[t].append({})
                            pages[t] += 1
                        collections[t][pages[t]][item['id']] = None   

    user = User.get(username)
    user.update( 
        { 
            'subscriptions': subs, 
            'collections': collections,
            'job_id': None 
        } 
    )
    print('finished')

def getTopics(subscriptions, q):
    params = {
        'part': 'topicDetails',
        'id': ','.join(subscriptions),
        'maxResults': '50',
        'key': getenv('API_KEY'),
    }

    q.put(get('https://www.googleapis.com/youtube/v3/channels', params=params).json())
