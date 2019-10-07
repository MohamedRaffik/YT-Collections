from server.utils.google_api import build_collections
from rq import Connection, Worker
from os import getenv
from dotenv import load_dotenv
import sys

if getenv('FLASK_ENV') == 'development':
    load_dotenv('.env')

with Connection():
    qs = sys.argv[1:] or ['default']

    w = Worker(qs)
    w.work()