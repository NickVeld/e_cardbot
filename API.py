# -*- coding: utf-8 -*-

import requests
import json

__author__ = 'NickVeld'


class Api:
    admin_id = 61407283
    api_key = '195086242:AAEvbzKAHV69PS3X4vptJNNij_OT3bT8BeY'
    dict_key = "dict.1.1.20160213T102818Z.7142bb91598d6fff.b1c74ef028f0e5db99da1f0d3e1db9561ea61c95"
    tr_key = "trnsl.1.1.20160215T190325Z.369ef43e4e71a747.935abff36df1f9617df0995d9267a7d42b06a1f4"

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
