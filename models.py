import urllib, hashlib

from google.appengine.ext import db
import string

from libraries.googleapiclient.oauth2client.appengine import CredentialsProperty


class Credentials(db.Model):
  credentials = CredentialsProperty()

class UserProfile(db.Model):
    user = db.UserProperty()
    access_token = db.StringProperty(required=False)