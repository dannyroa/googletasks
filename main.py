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

from google.appengine.dist import use_library
use_library('django', '1.2')

import os
import pickle

from libraries.googleapiclient import httplib2

from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp

from google.appengine.ext.webapp import util
from google.appengine.ext.webapp.util import login_required

from libraries.googleapiclient.apiclient.discovery import build
from libraries.googleapiclient.oauth2client.client import OAuth2WebServerFlow
from libraries.googleapiclient.oauth2client.appengine import StorageByKeyName


from models import *


IS_DEBUG = True
if os.environ.get('SERVER_SOFTWARE','').startswith('Goog'):
    IS_DEBUG = False

import settings




FLOW = OAuth2WebServerFlow(
            client_id=settings.CLIENT_ID,
            client_secret=settings.CLIENT_SECRET,
            scope=settings.SCOPE,
            user_agent='%s/0.1' % settings.APP_NAME,
            response_type='code'
        )


def get_task_service():

    user = users.get_current_user()
    credentials = StorageByKeyName(Credentials, user.user_id(), 'credentials').get()
    http = httplib2.Http()
    http = credentials.authorize(http)
        
    service = build(serviceName='tasks', version='v1', http=http, developerKey=settings.API_KEY)
    
    return service


class ConnectHandler(webapp.RequestHandler):
    @login_required
    def get(self):
        user = users.get_current_user()
        credentials = StorageByKeyName(Credentials, user.user_id(), 'credentials').get()
        if credentials is None or credentials.invalid == True:
            callback_url = self.request.relative_url('/callback')
            authorize_url = FLOW.step1_get_authorize_url(callback_url)
            memcache.set(user.user_id(), pickle.dumps(FLOW))
            self.redirect(authorize_url)
        else:
            self.redirect('/')


class CallbackHandler(webapp.RequestHandler):

    @login_required
    def get(self):
        user = users.get_current_user()
        flow = pickle.loads(memcache.get(user.user_id()))
        credentials = flow.step2_exchange(self.request.params)
        StorageByKeyName(Credentials, user.user_id(), 'credentials').put(credentials)
        
        self.redirect('/')


class MainHandler(webapp.RequestHandler):


    def get(self):

        if not users.get_current_user():
            self.redirect('/connect')
        else:
            service = get_task_service()

            tasklists = service.tasklists().list().execute()
            lists = tasklists['items']
            
            self.response.out.write(template.render('templates/index.html',
                                                  {'lists': lists}))

class ViewListHandler(webapp.RequestHandler):

    def get(self, id):
        
        service = get_task_service()
        
        list = service.tasklists().get(tasklist=id).execute()
        task_lists = service.tasks().list(tasklist=id).execute()

        tasks = []
        if task_lists.has_key('items'):
            tasks = task_lists['items']

        self.response.out.write(template.render('templates/view_list.html',
                                              {'list' : list, 'tasks': tasks}))


class AddListHandler(webapp.RequestHandler):

    def get(self):

        self.response.out.write(template.render('templates/add_list.html',
                                              {}))

    def post(self):

        service = get_task_service()

        list_title = self.request.get('title') 
        
        task_list = {'title': list_title }

        result = service.tasklists().insert(body=task_list).execute() 

        self.redirect('/')


class AddTaskHandler(webapp.RequestHandler):

    def get(self, list_id):

        service = get_task_service()

        list = service.tasklists().get(tasklist=list_id).execute()

        self.response.out.write(template.render('templates/add_task.html',
                                              {'list' : list}))

    def post(self, list_id):

        service = get_task_service()

        task_title = self.request.get('title') 
        
        task = {'title': task_title }

        result = service.tasks().insert(tasklist=list_id, body=task).execute() 

        self.redirect('/list/%s' % list_id)

class ViewTaskHandler(webapp.RequestHandler):

    def get(self, list_id, task_id):
            
        service = get_task_service()

        list = service.tasklists().get(tasklist=list_id).execute()
        task = service.tasks().get(tasklist=list_id, task=task_id).execute()

        self.response.out.write(template.render('templates/view_task.html',
                                              {'list' : list, 'task': task}))

    def post(self, list_id, task_id):

        service = get_task_service()

        action = self.request.get('action')  

        list = service.tasklists().get(tasklist=list_id).execute()
        
        if action == 'completed':
            task = service.tasks().get(tasklist=list_id, task=task_id).execute()
            task['status'] = 'completed'
            result = service.tasks().update(tasklist=list_id, task=task['id'], body=task).execute()
        elif action == 'revert':
            task = service.tasks().get(tasklist=list_id, task=task_id).execute()
            task['status'] = 'needsAction'
            task['completed'] = None
            result = service.tasks().update(tasklist=list_id, task=task['id'], body=task).execute()
        elif action == 'delete':
            service.tasks().delete(tasklist=list_id, task=task_id).execute()
        self.redirect('/list/%s' % list_id)


class CompleteTaskHandler(webapp.RequestHandler):

    def get(self, list_id, task_id):

        service = get_task_service()

        #list = service.tasklists().get(tasklist=list_id).execute()
        task = service.tasks().get(tasklist=list_id, task=task_id).execute()
        task['status'] = 'completed'
        result = service.tasks().update(tasklist=list_id, task=task['id'], body=task).execute()
        
        self.redirect('/list/%s' % list_id)


def main():
    application = webapp.WSGIApplication([('/', MainHandler)
                                        , ('/connect', ConnectHandler)
                                        , ('/callback', CallbackHandler)
                                        , ('/list/add', AddListHandler)
                                        , ('/list/([^\/]*)/task/add', AddTaskHandler)
                                        , ('/list/([^\/]*)/task/([^\/]*)', ViewTaskHandler)
                                        , ('/list/([^\/]*)/task/([^\/]*)/complete', CompleteTaskHandler)
                                        , ('/list/([^\/]*)', ViewListHandler),],
                                         debug=IS_DEBUG)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
