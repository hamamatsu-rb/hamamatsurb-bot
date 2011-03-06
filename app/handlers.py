from google.appengine.ext import webapp
from google.appengine.api import taskqueue, memcache

import tweepy, consumer, token, logging, re

class CronHandler(webapp.RequestHandler):
  def get(self):
    """
    GET /cron
    Execute added tweets every a minute.
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
      self.status_update()
      self.response.out.write("Success!")
    except Exception, e:
      logging.error(e.message)
      self.response.out.write("Error!")
  
  def status_update(self):
    """
    Execute status update by mentions that tweeted after last update.
    """
    status_id = None
    try:
      mentions = self.api.mentions()
      last_update_id = self.last_update_id()
      mentions.reverse()
      for status in mentions:
        if not (last_update_id and status.id <= last_update_id):
          status_id = self.update_status(status)
      if status_id:
        memcache.set('last_update_id', status_id)
    except Exception, e:
      if status_id:
        memcache.set('last_update_id', status_id)
      logging.error(e.message)
      
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
    text = status.text.replace('@hamamatsurb ', '')
    tag = '#hamamatsurb' if not re.search(r'#hamamatsurb', text) else ''
    text = "%s %s - @%s" % (text, tag, status.user.screen_name)
    if re.match('@', text):
      text = ".%s" % text
    try:
      self.api.update_status(text)
      return status.id
    except Exception, e:
      raise e
