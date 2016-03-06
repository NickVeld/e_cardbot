# -*- coding: utf-8 -*-

import requests
import json
from pymongo import MongoClient

__author__ = 'NickVeld'


class api:
    db = MongoClient('mongo', 27017).e_card
    admin_ids = set()
    api_key = ""
    dict_key = ""
    tr_key = ""

    def __init__(self, data):
        self.api_key = data["api_key"]
        self.dict_key = data["dict_key"]
        self.tr_key = data["tr_key"]
        self.admin_ids = data["admin_ids"]

    def get(self, toffset=0):
        method = 'getUpdates'
        params = {
            'offset': toffset + 1
        }
        try:
            req = requests.request(
                'POST',
                'https://api.telegram.org/bot{api_key}/{method}'.format(
                    api_key=self.api_key,
                    method=method
                ),
                params=params,
                timeout=30
            )

            return json.loads(req.text)
        except requests.exceptions.Timeout:
            print("Timeout in get()!")
        except Exception as ex:
            print("Error in get()!")
            print(type(ex), ex.__str__())

        return ""

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
                'https://api.telegram.org/bot{api_key}/{method}'.format(
                    api_key=self.api_key,
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

    def translate(self, request, lang, userl="en"):
        req = requests.get(
            "https://dictionary.yandex.net/api/v1/dicservice.json/lookup?key={dict_key}&lang={lang}&text={request})".format(
                dict_key = self.dict_key,
                lang = lang,
                request = request
                # userl = userl, &ui={userl}
                # flag = 12 &flags={flag}
            )
        ).json()

        res = ""
        if len(req['def']) > 0:
            nstr = 1 #number of string
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
                tr_key = self.tr_key,
                lang = lang,
                request = request
                # userl = userl, &ui={userl}
                # flag = 12 &flags={flag}
            )
        ).json()

        if req['code'] == 200:
            if len(req['text']) != 0:
                return req['text'][0]
            else:
                return ""
        else:
            return "Ошибочка вышла.\nСоветы:\n1) Проверьте ввод.\n2) Прочтите /help\n3) Надейтесь, что это не проблема с сервисом перевода."

    # def is_it_for_me(self, msg):
    #     raise NotImplementedError("It's necessary to redefine the abstract method \"is_it_for_me\"!")
    #
    # def run(self, msg):
    #     raise NotImplementedError("It's necessary to redefine the abstract method \"run\"!")