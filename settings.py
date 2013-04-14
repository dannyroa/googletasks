import os

CLIENT_ID = 'xxx
CLIENT_SECRET = 'xxx'
SCOPE = 'https://www.googleapis.com/auth/tasks'
APP_NAME = 'GTasks for Android Tablet'
API_KEY = 'xxx'

if not os.environ.get('SERVER_SOFTWARE','').startswith('Goog'):
    CLIENT_ID = 'xxx'
    CLIENT_SECRET = 'xxx'    
