from server import  app
from flask_login import UserMixin
from flask_pymongo import PyMongo
from google.cloud import firestore
from os import getenv

DEV_MODE = getenv('FLASK_ENV') == 'development'

db = PyMongo(app, uri=getenv('DATABASE_URI')).db

class User(UserMixin):
    def __init__(self, _id, subscriptions, collections, credentials, job_id, last_updated):
        self._id= _id
        self.subscriptions = subscriptions
        self.collections = collections
        self.credentials = credentials
        self.job_id = job_id
        self.last_updated = last_updated

    def insert(self):
        if DEV_MODE:
            db.Users.insert_one(self.to_dict())
        else:
            db.collection('Users').document(self._id).set(self.to_dict())

    def update(self, new_attributes):
        if DEV_MODE:
            db.Users.update_one({'_id': self._id}, {'$set': new_attributes})
        else:
            db.collection('Users').document(self._id).update(new_attributes)

    @staticmethod
    def get(email):
        user = db.Users.find_one({'_id': email}) if DEV_MODE else db.collection('Users').document(email).get().to_dict()
        if user:
            return User(**user)
        return None

    def to_dict(self):
        return {
            '_id': self._id,
            'subscriptions': self.subscriptions,
            'collections': self.collections,
            'credentials': self.credentials,
            'job_id': self.job_id,
            'last_updated': self.last_updated
        }

    def get_id(self) -> str:
        return self._id

    def get_collection(self, collection_name: str, page: int):
        return list(self.collections[collection_name][page].keys())

    def get_subscriptions(self, page:int):
        return ( len(self.subscriptions), list(self.subscriptions[page].keys()) )

    def remove_channel(self, channel_id):
        for page in self.subscriptions:
            if channel_id in page:
                page.pop(channel_id)
                break

        for collection in self.collections:
            for page in collection:
                if channel_id in page:
                    page.pop(channel_id)
                    break

        self.update({'subscriptions': self.subscriptions, 'collections': self.collections})

