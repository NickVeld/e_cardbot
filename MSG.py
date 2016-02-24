class MSG:
    def id(tmsg):
        return tmsg['message']['message_id']
    id = staticmethod(id)

    def upd_id(tmsg):
        return tmsg['update_id']
    upd_id = staticmethod(upd_id)

    def chat_id(tmsg):
        return tmsg['message']['chat']['id']
    chat_id = staticmethod(chat_id)

    def pers_id(tmsg):
        return tmsg['message']['from']['id']
    pers_id = staticmethod(pers_id)

    def name(tmsg):
        if 'first_name' in tmsg['message']['from']:
            who = tmsg['message']['from']['first_name']
        else:
            who = "Anonymous"
        return who
    name = staticmethod(name)

    def surname(tmsg):
        if 'last_name' in tmsg['message']['from']:
            who = tmsg['message']['from']['last_name']
        else:
            who = "Anonymous"
        return who
    surname = staticmethod(surname)

    def text(tmsg):
        if 'text' in tmsg['message']:
            return tmsg['message']['text']
        else:
            return ""
    text = staticmethod(text)
