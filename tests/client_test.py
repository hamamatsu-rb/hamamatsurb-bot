#-*- coding: utf-8 -*-

import os, sys

EXTRA_PATHS = [
  os.path.join(os.path.dirname(__file__), '..'),
  os.path.join(os.path.dirname(__file__), '..', 'app')
]
sys.path = EXTRA_PATHS + sys.path

import unittest, client, test_consumer, test_token, tweepy

class ClientTest(unittest.TestCase):
  def setUp(self):
    self.client = client.Client()
    auth = tweepy.OAuthHandler(test_consumer.KEY, test_consumer.SECRET)
    auth.set_access_token(test_token.KEY, test_token.SECRET)
    self.client.api = tweepy.API(auth)
    
  def test_get_current_user(self):
    user = self.client.get_current_user()
    assert user is not None
    assert user.screen_name is not None
        
  def test_get_last_update_id(self):
    assert self.client.get_last_update_id() is None
    
  def test_get_last_messages(self):
    screen_name = self._current_user_name()
    messages = self.client.get_last_messages()
    count = len(messages)
    assert 0 < count
    for message in messages:
      assert message.text.startswith(screen_name)
      
  def test_get_last_messages_with_ignore_sources(self):
    all_messages = self.client.get_last_messages()
    self.client.ignore_sources = ['Echofon']
    messages_not_echofon = self.client.get_last_messages()
    assert len(messages_not_echofon) < len(all_messages)
    
  def test_is_subscribe_message(self):
    screen_name = self._current_user_name()
    self.client.consumer_name = "Dummy"
    message = self._create_mock()
    assert not self.client.is_subscribe_message(message)
    
    message.text = "%s subscribe" % screen_name
    assert self.client.is_subscribe_message(message)
    
    message.text = "%s subscribe \n" % screen_name
    assert self.client.is_subscribe_message(message)
    
    message.text = "%s subscribe foo bar" % screen_name
    assert self.client.is_subscribe_message(message)
    
  def test_convert_message(self):
    screen_name = self._current_user_name()
    message = self._create_mock()
    message.text = "%s Hello!" % screen_name
    expected = 'Hello! #%s - @' % (screen_name, message.user.screen_name)
    assert self.client.convert_message(message) == expected
    message.text = "%s Hello! %s" % (screen_name, screen_name)
    assert self.client.convert_message(message) == expected
    
  def _current_user_name(self):
    user = self.client.get_current_user()
    return "@%s" % user.screen_name
    
  def _create_mock(self):
      class User:
        def _init__(self):
          self.screen_name = 'bob'
      class Mock:
        def __init__(self):
          self.user = User()
          self.text = ''
      return Mock()

if __name__ == '__main__':
  unittest.main()
