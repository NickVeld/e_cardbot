import API
from MSG import *
import json
import time
import random


def msg_tests():
    data = {}
    f = open("OutputExample.txt", 'r')
    dataStr = f.read()
    if dataStr != "":
        data = json.loads(dataStr)
    f.close()
    msg = data['result'][0]

    print(MSG.chat_id(msg))
    print(MSG.upd_id(msg))
    print(MSG.name(msg))
    print(MSG.surname(msg))
    print(MSG.pers_id(msg))
    print(MSG.text(msg))

# msg_tests()
random.seed(5849204)

data = {}
try:
    f = open("storage.yml", 'r')
    offset = int(f.readline())
    dataStr = f.read()
    if dataStr != "":
        data = json.loads(dataStr)
    f.close()
# except FileNotFoundError:
#     print("There're no storages.")
except Exception as ex:
    print(type(ex), ex.__str__())
    offset = 163111506

api = API.Api()

isRunning = True
print("Guess who's back!")
word_wait = 0
phrase_wait = 0

try:
    while isRunning:
        time.sleep(1)
        # try:
        newMsgs = api.get(offset)
        # except:
        #    print("Exception!")
        #    continue
        if newMsgs == "":
            continue

        if newMsgs['ok'] and (len(newMsgs['result']) != 0):
            for msg in newMsgs['result']:
                if 'text' in msg['message']:
                    txt = MSG.text(msg).strip()
                    if txt.startswith("//"):
                        continue
                    print(MSG.text(msg))
                    txt = txt.replace("@E_CardBot", "")
                    try:
                        if MSG.pers_id(msg) == 124147029:
                            print(api.send(MSG.name(msg) + ", вы в черном списке!", MSG.chat_id(msg)))
                        elif txt == "/StopPls":
                            offset = MSG.upd_id(msg)
                            print(MSG.upd_id(msg))
                            api.send("I'll be back, " + MSG.name(msg) + "!",
                                     MSG.chat_id(msg))
                            isRunning = False
                            break
                        elif txt.startswith("/tr") or word_wait:
                            if not word_wait:
                                if len(txt) < 4:
                                    api.send("Введите слово.", MSG.chat_id(msg))
                                    word_wait = MSG.id(msg)
                                    continue
                                else:
                                    txt = txt[3:].lstrip()
                                    word_wait = MSG.id(msg)
                            # res = ""
                            res = api.translate(txt, "ru-en", "ru")
                            if res == "":
                                res = api.translate(txt, "en-ru", "ru")
                            if res == "":
                                print(api.send("Нет перевода!", MSG.chat_id(msg), word_wait))
                            else:
                                print(api.send(res, MSG.chat_id(msg), word_wait))
                            word_wait = 0
                        elif txt.startswith("/help"):
                            api.send("/tr слово - переводит слово с английского на русский или с русского на английский.\n/ph** текст - перевод на язык с кодом ** текста до первой точки, если есть, иначе полностью.\nСписок кодов языков: https://tech.yandex.ru/translate/doc/dg/concepts/langs-docpage/\nПеревод слов: Реализовано с помощью сервиса «Яндекс.Словарь», https://tech.yandex.ru/dictionary/\nПеревод текста: Переведено «Яндекс.Переводчиком», http://translate.yandex.ru/", MSG.chat_id(msg))
                        elif txt.startswith("/ph") or phrase_wait:
                            if not phrase_wait:
                                if len(txt) < 6:
                                    api.send("Введите фразу.", MSG.chat_id(msg))
                                    phrase_wait = txt[3:5] + str(MSG.id(msg))
                                    continue
                                else:
                                    phrase_wait = txt[3:5] + str(MSG.id(msg))
                                    txt = txt[5:].lstrip()
                            brd = txt.find('.')
                            if brd != -1:
                                txt = txt[ : brd+1]
                            # res = ""
                            res = api.translateph(txt, phrase_wait[0:2], "ru")
                            phrase_wait = int(phrase_wait[2:])
                            if res == "":
                                print(api.send("Нет перевода!", MSG.chat_id(msg), phrase_wait))
                            else:
                                print(api.send(res, MSG.chat_id(msg), phrase_wait))
                            phrase_wait = 0


                    except UnicodeEncodeError:
                        print(api.send("I don't like your language!",
                                       MSG.chat_id(msg)))
            offset = MSG.upd_id(newMsgs['result'][len(newMsgs['result']) - 1])
            print(offset)
except Exception as ex:
    print(type(ex), ex.__str__())

try:
    f = open("storage.yml", 'w')
    f.write(str(offset) + '\n')
    # json.dump(data, f, sort_keys=True, indent=4)
except Exception as ex:
    print(type(ex), ex.__str__())
