class Msg():
    def __init__(self, msg, bot_nick):
        self.BOT_NICK = bot_nick
        if "callback_query" in msg:
            self.msg = msg['callback_query']['message']
            self.from_data = msg['callback_query']['from']
            self.inline_data = msg['callback_query']['data']
        elif "message" in msg:
            self.msg = msg['message']
            self.from_data = msg['message']['from']
            self.inline_data = None

    @property
    def id(self):
        return self.msg['message_id']

    @property
    def chat_id(self):
        return self.msg['chat']['id']

    @property
    def pers_id(self):
        return self.from_data['id']

    @property
    def name(self):
        return self.from_data.get('first_name', 'Anonymous')

    @property
    def surname(self):
        return self.from_data.get('last_name', 'Anonymous')

    @property
    def text(self):
        if self.inline_data == None:
            return self.msg.get('text', '')
        else:
            return self.inline_data

    @property
    def text_of_inline_root(self):
        return self.msg.get('text', '')

    @property
    def is_inline(self):
        return self.inline_data != None

    def text_change_to(self, new_v):
        if self.inline_data == None:
            self.msg['text'] = new_v
        else:
            self.inline_data = new_v

    def textmod(self):
        if self.inline_data == None:
            self.msg['text'] = self.msg['text'].strip().replace(self.BOT_NICK, "")
