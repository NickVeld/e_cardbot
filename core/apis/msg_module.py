class Msg():
    msg = None
    BOT_NAME = ""

    def __init__(self, msg, bot_nick):
        self.msg = msg
        self.BOT_NICK = bot_nick

    @property
    def id(self):
        return self.msg['message']['message_id']

    @property
    def upd_id(self):
        return self.msg['update_id']

    @property
    def chat_id(self):
        return self.msg['message']['chat']['id']

    @property
    def pers_id(self):
        return self.msg['message']['from']['id']

    @property
    def name(self):
        return self.msg['message']['from'].get('first_name', 'Anonymous')

    @property
    def surname(self):
        return self.msg['message']['from'].get('last_name', 'Anonymous')

    @property
    def text(self):
        return self.msg['message'].get('text', '')

    def text_change_to(self, new_v):
        self.msg['message']['text'] = new_v

    def textmod(self):
        self.msg['message']['text'] = self.msg['message']['text'].strip().replace(self.BOT_NICK, "")
