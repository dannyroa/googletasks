import os

CLIENT_ID = '33691209862-hitq5jjglon9s40dksvan2uq25fl1392.apps.googleusercontent.com'
CLIENT_SECRET = 'maIzDLqg6QugKy0sXBACYEUA'
SCOPE = 'https://www.googleapis.com/auth/tasks'
APP_NAME = 'GTasks for Android Tablet'
API_KEY = 'AIzaSyACNb_rkthfSuvBWgomeA6p8xWLx2xmQxI'

if not os.environ.get('SERVER_SOFTWARE','').startswith('Goog'):
    CLIENT_ID = '33691209862-ds6afl606ateo3nucq573003ba6i0gni.apps.googleusercontent.com'
    CLIENT_SECRET = 'kGn5a8li6irL-nDqYP8l-KR5'    