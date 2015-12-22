import os

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

WHOOSH_BASE = os.path.join(basedir, 'search.db')

OAUTH_CREDENTIALS = {
    'facebook': {
        'credentials': {
            'id': '586101134861886',
            'secret': '94b3ad852aa93e589832757faed03d5d'
        },
        'request_token_url': '',
        'authorize_url': 'https://graph.facebook.com/oauth/authorize',
        'access_token_url': 'https://graph.facebook.com/oauth/access_token',
        'base_url': 'https://graph.facebook.com/'
    },
    'twitter': {
        'credentials': {
            'id': 'Y3OxNi2Q9ATk7VAdYyBmycXw4',
            'secret': 'b4Kszm26FU8Gai4ysNpsM7KvuNV0b8Je5HFzswZNPkl4B8uXoh'
        },
        'request_token_url': 'https://api.twitter.com/oauth/request_token',
        'authorize_url': 'https://api.twitter.com/oauth/authorize',
        'access_token_url': 'https://api.twitter.com/oauth/access_token',
        'base_url': 'https://api.twitter.com/1.1/'
    }
}

# email server
MAIL_SERVER = 'mail.uetunited.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

# administrator list
ADMINS = ['quannh@uetunited.com']

# pagination
POSTS_PER_PAGE = 20
# searching
MAX_SEARCH_RESULTS = 50
