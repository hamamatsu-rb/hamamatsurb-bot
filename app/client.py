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
  
  def get_last_update_id(self, consumer_name):
    """
    指定したクライアントが投稿した最後のツイートのIDを取得する
    """
    statuses = self.api.user_timeline()
    for status in statuses:
      if status.source == consumer_name:
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
    text = message.text.replace(pattern, '').strip()
    return "%s #%s - @%s" % (text, self.get_current_user().screen_name, message.user.screen_name)
    
  def update_status(self, text):
    """
    Twitterにテキストを投稿する。
    """
    return self.api.update_status(text)
    
  def subscribe_user(self, user, list_name=None):
    """
    ユーザーをフォローしていなければフォローし、リストが指定されていたらリストに追加する。
    """
    if not self.api.exists_friendship(self.get_current_user().screen_name, user.screen_name):
      self.api.create_friendship(user.screen_name)
      if list_name:
        self.api.add_list_member(list_name, user.id)
      text = u".@%s さんが%sに参加しました！" % (user.screen_name, self.get_current_user().name)
      return  self.update_status(text)
    else:
      return None