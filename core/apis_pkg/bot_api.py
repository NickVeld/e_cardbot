# -*- coding: utf-8 -*-

import random
import requests
import json
from pymongo import MongoClient

__author__ = 'NickVeld'


class API:
    db = None
    telegram = None
    translator = None
    offset = 0

    admin_ids = set()
    BOT_NICK = ""
    DB_IS_ENABLED = False
    NO_CARDS_GROUPS = True
    COOLDOWN_M = 1

    def __init__(self):
        self.telegram = Tg_api()
        self.translator = Translator()

    # def __init__(self, data):
    #     self.telegram = Tg_api(data["api_key"])
    #     self.translator = Translator(data["dict_key"], data["tr_key"])
    #
    #     self.admin_ids = data["admin_ids"]
    #     self.DB_IS_ENABLED = data["db_is_enabled"]
    #     self.NO_CARDS_GROUPS = not data["cards_groups"]
    #     self.COOLDOWN_M = int(data["cooldown_m"])
    #     self.db = MongoClient(data["mongo_name"], data["mongo_port"])["e_card"] if self.DB_IS_ENABLED else None

    def get_from_config(self, cfg):
        self.DB_IS_ENABLED = cfg['mongo_settings']['isEnabled'] == 'True'
        self.admin_ids = cfg['admins_ids']
        self.NO_CARDS_GROUPS = cfg["cards_is_allowed_for_groups"] == 'False'
        self.COOLDOWN_M = int(cfg["card_cooldown_at_minutes"])

        self.db = (MongoClient(cfg['mongo_settings']['name'], int(cfg['mongo_settings']['port']))
                   [cfg['mongo_settings']['db_name']] if self.DB_IS_ENABLED else None)

        self.BOT_NICK = cfg['APIs']['bot_nick']

        self.telegram.get_from_config(cfg['APIs'])
        self.translator.get_from_config(cfg['APIs'])

    def get(self, toffset=0):
        return self.telegram.get(toffset)

    def get_msg(self):
        while True:
            new_msgs = self.get(self.offset)
            if new_msgs is None:
                continue

            for msg in new_msgs['result']:
                self.offset = msg['update_id']
                print(self.offset)
                yield msg

    def send(self, message, chat_id, reply_to_message_id=0, keyboard=None):
        return self.telegram.send(message, chat_id, reply_to_message_id, keyboard)

    def translate(self, request, lang, userl="en"):
        return self.translator.translate(request, lang, userl)

    def translateph(self, request, lang, userl="en"):
        return self.translator.translateph(request, lang, userl)

    def get_random_doc(self, collection, request=None):
        return collection.find().skip(random.randint(0, collection.count()-1)).limit(1)[0] \
            if request == None else \
            collection.find(request).skip(random.randint(0, collection.count()-1)).limit(1)[0]
        #return collection.find_one() if request==None else collection.find_one(request)

class Tg_api:
    API_KEY = ""

    def __init__(self):
        pass

    # def __init__(self, api_key):
    #     self.API_KEY = api_key

    def get_from_config(self, cfg):
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
                'https://api.telegram.org/bot{api_key}/{method}'.format(
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
                return json.loads(req.text)
        except requests.exceptions.Timeout:
            print("Timeout in get()!")
        except Exception as ex:
            print("Error in get()!")
            print(type(ex), ex.__str__())
        return None

    def send(self, message, chat_id, reply_to_message_id=0, keyboard=None):
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
                'https://api.telegram.org/bot{api_key}/{method}'.format(
                    api_key=self.API_KEY,
                    method=method
                ),
                params=params,
                timeout=30
            )
        except requests.exceptions.Timeout:
            print("Timeout in send()!")
        except Exception as ex:
            print("Error in send()!")
            print(type(ex), ex.__str__())
        return message

class Translator:
    DICT_KEY = ""
    TR_KEY = ""

    def __init__(self):
        pass

    # def __init__(self, dict_key, tr_key):
    #     self.DICT_KEY = dict_key
    #     self.TR_KEY = tr_key

    def get_from_config(self, cfg):
        self.DICT_KEY = cfg['dictionary_api']
        self.TR_KEY = cfg['translator_api']

    def translate(self, request, lang, userl="en"):
        req = requests.get(
            "https://dictionary.yandex.net/api/v1/dicservice.json/lookup?key={dict_key}&lang={lang}&text={request})".format(
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
        return res

    def translateph(self, request, lang, userl="en"):
        req = requests.get(
            "https://translate.yandex.net/api/v1.5/tr.json/translate?key={tr_key}&text={request}&lang={lang}".format(
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