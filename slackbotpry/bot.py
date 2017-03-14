from slackclient import SlackClient
from multiprocessing.pool import Pool
from time import sleep
from . import eventpool

class Bot:
    def __init__(self, api_token, default_channel='random'):
        self.api = SlackClient(token=api_token)
        self.cur_channel = default_channel
        # 今後デフォルトで設定するかもしれないところ API じゃできないっぽい
        self.owner = ''
        self.user_dm = ''
        self.handlers = []
        self.pool = eventpool.EventPool()
    def add_eventhandler(self, handler):
        self.handlers.append(handler)
    def mainloop(self):
        if self.api.rtm_connect():
            while True:
                events = self.api.rtm_read()
                for event in events:
                    self.on_event(event)
                self.pool.check_queue()
                sleep(1)
    def on_event(self, event):
        if 'bot_id' in event:
            return
        for handler in self.handlers:
            if handler.filter(event):
                record = eventpool.EventPoolRecord(handler, self, event)
                self.pool.register(record)
    def post_message(self, message, channel=None, dest_user=None):
        """Post a Message
        Description:
            This method posts a message to channel (if channel is None, self.cur_channel).
        Arguments:
            message (str): message to post
        """
        if dest_user is None:
            text = message
        else:
            text = '@{0} {1}'.format(dest_user, message)
        if channel is None:
            channel = self.cur_channel
        result = self.api.api_call('chat.postMessage', text=text, link_names=True, channel=channel, as_user=True)
        return result
