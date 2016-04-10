class Msg():
    msg = None

    def __init__(self, msg):
        self.msg = msg

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
        if 'first_name' in self.msg['message']['from']:
            who = self.msg['message']['from']['first_name']
        else:
            who = "Anonymous"
        return who

    @property
    def surname(self):
        if 'last_name' in self.msg['message']['from']:
            who = self.msg['message']['from']['last_name']
        else:
            who = "Anonymous"
        return who

    @property
    def text(self):
        if 'text' in self.msg['message']:
            return self.msg['message']['text']
        else:
            return ""

    def text_change_to(self, new_v):
        self.msg['message']['text'] = new_v

    def textmod(self):
        self.msg['message']['text'] = self.msg['message']['text'].strip().replace("@E_CardBot", "").lower()
