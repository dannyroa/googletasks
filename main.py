#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from libraries.googleapiclient import httplib2

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from libraries.googleapiclient.oauth2client.client import OAuth2WebServerFlow

STEP2_URI = 'http://www.dannylocal.com:8082/callback'

CLIENT_ID = '33691209862-ds6afl606ateo3nucq573003ba6i0gni.apps.googleusercontent.com'
CLIENT_SECRET = 'kGn5a8li6irL-nDqYP8l-KR5'
SCOPE = 'https://www.googleapis.com/auth/tasks'
APP_NAME = 'GTasks for Android Tablet'


FLOW = OAuth2WebServerFlow(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            scope=SCOPE,
            user_agent='%s/0.1' % APP_NAME,
            response_type='code'
        )

class ConnectHandler(webapp.RequestHandler):

    def get(self):
        
        authorize_url = FLOW.step1_get_authorize_url(STEP2_URI)
        
        self.redirect(authorize_url)


class CallbackHandler(webapp.RequestHandler):

    def get(self):
        credentials = FLOW.step2_exchange(self.request.params)
        self.response.out.write(credentials.access_token)


class MainHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write('Hello world!')


def main():
    application = webapp.WSGIApplication([('/', MainHandler)
                                        , ('/connect', ConnectHandler)
                                        , ('/callback', CallbackHandler)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
