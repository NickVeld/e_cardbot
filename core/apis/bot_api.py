# -*- coding: utf-8 -*-

import requests
import json
from core.services.db_shell import DBShell
from core.workers.service_workers import WorkersList as ServiceWorkersList

__author__ = 'NickVeld'


class API:
    def __init__(self):
        self.telegram = Tg_api()
        self.translator = Translator()
        self.db_shell = DBShell()
        self.offset = 0

        self.admin_ids = list()
        self.BOT_NICK = ""
        self.DB_IS_ENABLED = False
        self.NO_CARDS_GROUPS = True

        self.workers_list = None

    # def __init__(self, data):
    #     self.telegram = Tg_api(data["api_key"])
    #     self.translator = Translator(data["dict_key"], data["tr_key"])
    #
    #     self.admin_ids = data["admin_ids"]
    #     self.DB_IS_ENABLED = data["db_is_enabled"]
    #     self.NO_CARDS_GROUPS = not data["cards_groups"]
    #     self.db = MongoClient(data["mongo_name"], data["mongo_port"])["e_card"] if self.DB_IS_ENABLED else None

    def get_from_config(self, cfg):
        self.DB_IS_ENABLED = cfg['mongo_settings']['isEnabled'] == 'True'
        print("DB is " + ("en" if self.DB_IS_ENABLED else "dis") + "abled")
        self.admin_ids = list(cfg['admins_ids'])
        self.NO_CARDS_GROUPS = cfg["cards_is_allowed_for_groups"] == 'False'

        self.BOT_NICK = cfg['APIs']['bot_nick']

        self.telegram.get_from_config(cfg['APIs'])
        self.translator.get_from_config(cfg['APIs'])
        self.db_shell.get_from_config(cfg)

        self.service_workers_list = ServiceWorkersList.get_workers(ServiceWorkersList
                                                                   , cfg["included_service_workers"], self)

    def get(self, toffset=0):
        return self.telegram.get(toffset)

    def get_msg(self):
        while True:
            for worker in self.service_workers_list:
                if worker.is_it_for_me():
                    cmd = worker.run()
                    if cmd != 1:
                        break
            new_msgs = self.get(self.offset)
            if new_msgs is None:
                continue

            for msg in new_msgs['result']:
                self.offset = msg['update_id']
                yield msg

    def send(self, message, chat_id, reply_to_message_id=0, keyboard=None):
        self.telegram.send(message, chat_id, reply_to_message_id)
        return message

    def send_with_id(self, message, chat_id, reply_to_message_id=0, keyboard=None):
        return self.telegram.send(message, chat_id, reply_to_message_id)

    def send_inline_keyboard(self, message, chat_id, inline_keyboard, reply_to_message_id=0):
        self.telegram.send_inline_keyboard(message, chat_id, inline_keyboard, reply_to_message_id)
        return message

    def send_inline_keyboard_with_id(self, message, chat_id, inline_keyboard, reply_to_message_id=0):
        return self.telegram.send_inline_keyboard(message, chat_id, inline_keyboard, reply_to_message_id)

    def edit(self, message, chat_id, inline_keyboard, message_id):
        return self.telegram.edit(message, chat_id, inline_keyboard, message_id)

    def get_inline_text_keyboard(self, source):
        return self.telegram.get_inline_text_keyboard(source)

    def translate(self, request, lang, userl="en"):
        return self.translator.translate(request, lang, userl)

    def translateph(self, request, lang, userl="en"):
        return self.translator.translateph(request, lang, userl)

    @property
    def db(self):
        return self.db_shell.db

    @property
    def COOLDOWN_M(self):
        return self.db_shell.COOLDOWN_M

    def get_random_doc(self, collection, request=None):
        return self.db_shell.get_random_doc(collection, request)

    def get_test_word(self, pers_id):
        return self.db_shell.get_test_word(pers_id)

    def get_doc_for_card(self, tmsg, collection, additional_condition=(lambda x: True)):
        return self.db_shell.get_doc_for_card(tmsg, collection, additional_condition)

    def update_doc_for_card(self, is_not_test_word, pers_id, doc_id, correctness):
        self.db_shell.update_doc_for_card(is_not_test_word, pers_id, doc_id, correctness)

    def insert_doc_for_card(self, tmsg, collection, tr_request, lang, tr_response):
        self.db_shell.insert_doc_for_card(tmsg, collection, tr_request, lang, tr_response)


class Tg_api:

    def __init__(self):
        pass

    # def __init__(self, api_key):
    #     self.API_KEY = api_key

    def get_from_config(self, cfg):
        self.CHAT_LINK = cfg['telegram_chatlink']
        self.API_KEY = cfg['telegram_api']

    def get(self, toffset=0, timeout=29):
        method = 'getUpdates'
        params = {
            'offset': toffset + 1,
            'timeout': timeout
        }
        try:
            req = requests.request(
                'POST',
                '{link}{api_key}/{method}'.format(
                    link=self.CHAT_LINK,
                    api_key=self.API_KEY,
                    method=method
                ),
                params=params,
                timeout=timeout+1
            )
            if req.text is "":
                return None

            new_msgs = json.loads(req.text)
            if new_msgs['ok'] and (len(new_msgs['result']) != 0):
                return new_msgs
        except requests.exceptions.Timeout:
            print("Timeout in get()!")
        except Exception as ex:
            print("Error in get()!")
            print(type(ex), ex.__str__())
        return None

    def send(self, message, chat_id, reply_to_message_id=0):
        method = 'sendMessage'
        params = {
            'chat_id': chat_id,
            'disable_web_page_preview': True,
            'text': message
        }
        if reply_to_message_id:
            params['reply_to_message_id'] = reply_to_message_id
        try:
            req = requests.request(
                'POST',
                '{link}{api_key}/{method}'.format(
                    link = self.CHAT_LINK,
                    api_key=self.API_KEY,
                    method=method
                ),
                params=params,
                timeout=30
            )
            sended = json.loads(req.text)
            if sended['ok']:
                return sended['result']['message_id']
        except requests.exceptions.Timeout:
            print("Timeout in send()!")
        except Exception as ex:
            print("Error in send()!")
            print(type(ex), ex.__str__())
        return 0

    def get_reply_keyboard(self, source):
        return [["/{}".format(c) for c in s_in.split('\t')] for s_in in source.split('\n')]

    def send_reply_keyboard(self, message, chat_id, keyboard, reply_to_message_id=0):
        method = 'sendMessage'
        params = {
            'chat_id': chat_id,
            'disable_web_page_preview': True,
            'text': message
        }
        if reply_to_message_id:
            params['reply_to_message_id'] = reply_to_message_id
        if keyboard != None:
            params["reply_markup"] = json.dumps({
                "keyboard": keyboard,
                "resize_keyboard": True,
                "one_time_keyboard": True,
                "selective": True
            })
        try:
            req = requests.request(
                'POST',
                '{link}{api_key}/{method}'.format(
                    link=self.CHAT_LINK,
                    api_key=self.API_KEY,
                    method=method
                ),
                params=params,
                timeout=30
            )
            sended = json.loads(req.text)
            if sended['ok']:
                return sended['result']['message_id']
        except requests.exceptions.Timeout:
            print("Timeout in send_reply_keyboard(...)!")
        except Exception as ex:
            print("Error in send_reply_keyboard(...)!")
            print(type(ex), ex.__str__())
        return 0

    def get_inline_text_keyboard(self, source):
        return list([[{'text': c,
                       'callback_data': "/{}".format(c)} for c in s_in.split('\t')] for s_in in source.split('\n')])

    def send_inline_keyboard(self, message, chat_id, inline_keyboard, reply_to_message_id=0):
        method = 'sendMessage'
        params = {
            'chat_id': chat_id,
            'disable_web_page_preview': True,
            'text': message
        }
        if reply_to_message_id:
            params['reply_to_message_id'] = reply_to_message_id
        if inline_keyboard != None:
            params["reply_markup"] = json.dumps({
                "inline_keyboard": inline_keyboard
            })
        try:
            req = requests.request(
                'POST',
                '{link}{api_key}/{method}'.format(
                    link=self.CHAT_LINK,
                    api_key=self.API_KEY,
                    method=method
                ),
                params=params,
                timeout=30
            )
            sended = json.loads(req.text)
            if sended['ok']:
                return sended['result']['message_id']
        except requests.exceptions.Timeout:
            print("Timeout in send_inline_keyboard(...)!")
        except Exception as ex:
            print("Error in send_inline_keyboard(...)!")
            print(type(ex), ex.__str__())
        return 0

    def edit(self, message, chat_id, inline_keyboard, message_id):
        method = 'editMessageText'
        params = {
            'chat_id': chat_id,
            'message_id': message_id,
            'disable_web_page_preview': True,
            'text': message
        }
        if inline_keyboard != None:
            params["reply_markup"] = json.dumps({
                "inline_keyboard": inline_keyboard
            })
        try:
            req = requests.request(
                'POST',
                '{link}{api_key}/{method}'.format(
                    link=self.CHAT_LINK,
                    api_key=self.API_KEY,
                    method=method
                ),
                params=params,
                timeout=30
            )
        except requests.exceptions.Timeout:
            print("Timeout in edit(...)!")
        except Exception as ex:
            print("Error in edit(...)!")
            print(type(ex), ex.__str__())
        return message

class Translator:
    def __init__(self):
        self.DICT_KEY = ""
        self.TR_KEY = ""
        self.DICT_LINK = ""
        self.TR_LINK = ""
        self.SPLR_LINK = ""

    # def __init__(self, dict_key, tr_key):
    #     self.DICT_KEY = dict_key
    #     self.TR_KEY = tr_key

    def get_from_config(self, cfg):
        self.DICT_KEY = cfg['dictionary_api']
        self.TR_KEY = cfg['translator_api']
        self.DICT_LINK = cfg['dictionary_link']
        self.TR_LINK = cfg['translator_link']
        self.SPLR_LINK = cfg['speller_link']

    def translate(self, request, lang, userl="en"):
        if len(request) > 100:
            request = request[:100]
        req = requests.get(
            "{link}&text={request}&lang={lang})".format(
                link=self.SPLR_LINK,
                lang=lang,
                request=request
            )
        ).json()

        with_mistakes = False
        for mistake in req:
            if mistake['code'] == 1 and len(mistake['s']) > 0:
                with_mistakes = True
                request = request.replace(mistake['word'], mistake['s'][0], 1)
        req = requests.get(
            "{link}key={dict_key}&lang={lang}&text={request})".format(
                link=self.DICT_LINK,
                dict_key=self.DICT_KEY,
                lang=lang,
                request=request
                # userl=userl, &ui={userl}
                # flag=12 &flags={flag}
            )
        ).json()

        res = ""
        if len(req['def']) > 0:
            nstr = 1  # number of string
            for wdef in req['def']:
                if 'tr' in wdef:
                    if len(wdef['tr']) > 0:
                        res += str(nstr) + '. '
                        nstr += 1
                        for tr in wdef['tr']:
                            res += tr['text'] + ", "
                        res = res[:-2]
                        res += '\n'
            res = res[:-1]
        if with_mistakes:
            res = "*_%" + request + "\n\n" + res
        return res

    def translateph(self, request, lang, userl="en"):
        req = requests.get(
            "{link}key={tr_key}&text={request}&lang={lang}".format(
                link=self.TR_LINK,
                tr_key=self.TR_KEY,
                lang=lang,
                request=request
                # userl=userl, &ui={userl}
                # flag=12 &flags={flag}
            )
        ).json()

        if req['code'] == 200:
            if len(req['text']) != 0:
                return req['text'][0]
            else:
                return ""
        else:
            return "Ошибочка вышла.\nСоветы:\n1) Проверьте ввод.\n2) Прочтите /help\n" \
                   "3) Надейтесь, что это не проблема с сервисом перевода."