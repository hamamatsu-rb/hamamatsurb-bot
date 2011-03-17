#-*- coding: utf-8 -*-

from google.appengine.ext import webapp
from google.appengine.api import taskqueue, memcache

import client, logging

class CronHandler(webapp.RequestHandler):
  def get(self):
    """
    GET /cron
    Executes every a minute.
    """
    taskqueue.add(url='/update')
    self.response.out.write("Call update worker.")
    
class UpdateHandler(webapp.RequestHandler):
  def post(self):
    """
    POST /update
    """
    try:
      self.client = client.Client()
      self.execute()
      self.response.out.write("Success!")
    except Exception, e:
      self.response.out.write("Error!")
  
  def execute(self):
    """
    Execute status update or subscribe user by mentions that tweeted after last update.
    """
    status = None
    try:
      # mentions = self.api.mentions()
      last_update_id = self.last_update_id()
      messages = self.client.get_last_messages(last_update_id)
      for message in messages:
        if self.client.is_subscribe_message(message):
          status = self.client.subscribe_user(message.user)
        else:
          text = self.client.convert_message(message)
          status = self.client.update_status(text)
        memcache.set('last_update_id', status.id)
    except Exception, e:
      if status:
        memcache.set('last_update_id', status.id)
      logging.error("UpdateHandler#execute: %s" % e)
      raise e
      
  def last_update_id(self):
    """
    Return last status id that this bot posted.
    """
    last_update_id = memcache.get('last_update_id')
    if last_update_id is not None:
      return last_update_id
    try:
      return self.client.get_last_update_id('hamamatsurb-bot')
    except Exception, e:
      logging.error("UpdateHandler#last_update_id: %s" % e)
      raise e
