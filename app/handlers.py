#-*- coding: utf-8 -*-

from google.appengine.ext import webapp
from google.appengine.api import taskqueue, memcache

import tweepy, consumer, token, logging, re

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
      auth = tweepy.OAuthHandler(consumer.KEY, consumer.SECRET)
      auth.set_access_token(token.KEY, token.SECRET)
      self.api = tweepy.API(auth)
      self.execute()
      self.response.out.write("Success!")
    except Exception, e:
      logging.error(e)
      self.response.out.write("Error!")
  
  def execute(self):
    """
    Execute status update or subscribe user by mentions that tweeted after last update.
    """
    status_id = None
    try:
      mentions = self.api.mentions()
      last_update_id = self.last_update_id()
      mentions.reverse()
      for status in mentions:
        if not (last_update_id and status.id <= last_update_id):
          if status.text.strip() == u'@hamamatsurb subscribe':
            status_id = self.subscribe_user(status)
          else:
            status_id = self.update_status(status)
      if status_id:
        memcache.set('last_update_id', status_id)
    except Exception, e:
      if status_id:
        memcache.set('last_update_id', status_id)
      logging.error(e)
      
  def last_update_id(self):
    """
    Return last status id that this bot posted.
    """
    last_update_id = memcache.get('last_update_id')
    if last_update_id is not None:
      return last_update_id
    try:
      statuses = self.api.user_timeline()
      p = re.compile(r'hamamatsu', re.IGNORECASE)
      for status in  statuses:
        if p.match(status.source):
          return status.id
      return None
    except Exception, e:
      raise e
    
  def update_status(self, status):
    """
    Update status with a hashtag and user screen name.
    """
    if status.source.startswith('GitHub'):
      return None
    text = status.text.replace('@hamamatsurb ', '')
    tag = '#hamamatsurb' if not re.search(r'#hamamatsurb', text) else ''
    text = "%s %s - @%s" % (text, tag, status.user.screen_name)
    if re.match('@', text):
      text = ".%s" % text
    if 140 < len(text):
      text = "%s..." % text[0:140-3]
    try:
      self.api.update_status(text)
      return status.id
    except Exception, e:
      raise e

  def subscribe_user(self, status):
    """
    Follow user and add user to list.
    """
    screen_name = status.user.screen_name
    try:
      if not self.api.exists_friendship('hamamatsurb', screen_name):
        self.api.create_friendship(screen_name)
        self.api.add_list_member('hamamatsu-rb', status.user.id)
        text = u".@%s さんがHamamatsu.rbに参加しました！" % screen_name
        self.api.update_status(text)
        logging.info(text)
        return status.id
    except Exception, e:
      raise e
