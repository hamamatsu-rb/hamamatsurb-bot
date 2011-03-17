#-*- coding: utf-8 -*-

import tweepy, consumer, token, logging, re

class Client(object):
  """
  Twitterクライアント
  """
  def __init__(self):
    auth = tweepy.OAuthHandler(consumer.KEY, consumer.SECRET)
    auth.set_access_token(token.KEY, token.SECRET)
    self.api = tweepy.API(auth)
    self.current_user = None
    self.ignore_sources = consumer.IGNORE_SOURCES
    
  def get_current_user(self):
    """
    このクライアントBotが使うTwitterアカウントを取得する
    """
    if self.current_user:
      return self.current_user
    self.current_user = self.api.me()
    return self.current_user
  
  def get_last_update_id(self):
    """
    このクライアントが投稿した最後のツイートのIDを取得する
    """
    statuses = self.api.user_timeline()
    regex = re.compile(r'hamamatsu', re.IGNORECASE)
    for status in  statuses:
      if regex.match(status.source):
        return status.id
    return None

  def get_last_messages(self, last_update_id=None):
    """
    このアカウント向けの最新のメンションの中から転送すべきメッセージのリストを古い順で取得する。
      * last_update_idが指定された場合は、それより新しいものだけを取得
      * 先頭が @screen_name で始まらないものは無視
      * 投稿主が ignore_sources に含まれる場合は無視
    """
    messages = []
    screen_name = "@%s" % self.get_current_user().screen_name
    mentions = self.api.mentions()
    mentions.reverse()
    for mention in mentions:
      if mention.text.startswith(screen_name):
        if not (last_update_id and status.id <= last_update_id):
          if self.ignore_sources.count(mention.source) == 0:
            messages.append(mention)
    return messages
    
  def is_subscribe_message(self, message):
    """
    メッセージがメンバー登録用か否かを確認する。
    """
    pattern = "@%s subscribe" % self.get_current_user().screen_name
    return message.text.strip().startswith(pattern)
  
  def convert_message(self, message):
    """
    受け取ったメッセージをBotが投稿するテキストに変換する。
    """
    pattern = "@%s" % self.get_current_user().screen_name
    return message.text.replace(pattern, '').strip()
    
  def update_status(self, text):
    """
    Twitterにテキストを投稿する。
    """
    pass