# -*- coding: utf-8 -*-

import datetime
import random
import sys

class WorkersList(type):
    workers = []

    def __new__(mcs, name, bases, attrs, **kwargs):
        worker_class = super(WorkersList, mcs).__new__(mcs, name, bases, attrs)
        if '__not_bot__' not in attrs:
            WorkersList.workers.append((name, worker_class))
        return worker_class

    def get_workers(cls, list, tapi):
        workers = []
        # available = cls.workers
        for worker in cls.workers:
            exist = False
            for str in list:
                if str == worker[0]:
                    exist = True
                    break
            if not exist:
                cls.workers.remove(worker)

        for str in list:
            try:
                workers.append(getattr(sys.modules[__name__], str)(tapi))
                print(str)
            except:
                print("There isn't " + str)
        return workers


class BaseWorker(object, metaclass=WorkersList):
    __not_bot__ = True

    HELP = ""
    tAPI = None
    
    def __init__(self, teleapi):
        self.tAPI = teleapi


class Blacklist(BaseWorker):
    # HELP = "There is a blacklist for rude users!\n\n"

    def is_it_for_me(self, tmsg):

        if self.tAPI.DB_IS_ENABLED:
            collection = self.tAPI.db.blacklist
            return ((tmsg.text.startswith("/addbl")) or (tmsg.text.startswith("/delbl")) or
                    (collection.find_one({"pers_id": str(tmsg.pers_id)}) is not None))
        return False

    def run(self, tmsg):
        # TODO adding and deleting from blacklist.
        return 0


class Stop(BaseWorker):

    def is_it_for_me(self, tmsg):
        return tmsg.text == "/StopPls"

    def run(self, tmsg):
        print(self.tAPI.send("I'll be back, " + tmsg.name + "!", tmsg.chat_id))
        return 2


class Translator(BaseWorker):
    HELP = ("/tr слово - переводит слово с английского на русский или с русского на английский.\n"
            "Реализовано с помощью сервиса «Яндекс.Словарь», https://tech.yandex.ru/dictionary/\n\n")

    waitlist = set()

    def is_it_for_me(self, tmsg):
        return tmsg.text.startswith("/tr") or ((tmsg.pers_id, tmsg.chat_id) in self.waitlist or
                                               ((tmsg.pers_id == tmsg.chat_id) and not tmsg.text.startswith("/")))

    def run(self, tmsg):
        is_chain = (tmsg.pers_id, tmsg.chat_id) in self.waitlist
        txt = ""
        tmsg.text_change_to(tmsg.text.lower())
        if not (is_chain or
                ((tmsg.pers_id == tmsg.chat_id) and not tmsg.text.startswith("/"))):
            if len(tmsg.text) < 4:
                self.tAPI.send("Введите слово.", tmsg.chat_id)
                self.waitlist.add((tmsg.pers_id, tmsg.chat_id))
                return 1
            else:
                txt = tmsg.text[3:].lstrip()
        else:
            txt = tmsg.text.lstrip()
        if txt.startswith('/'):
            txt = txt[1:]
        # res = ""
        post = None
        if self.tAPI.DB_IS_ENABLED:
            collection = self.tAPI.db.tr
            post = collection.find_one({"word": txt})
        if post is None:
            lang = ""
            res = self.tAPI.translate(txt, "ru-en", "ru")
            if res == "":
                res = self.tAPI.translate(txt, "en-ru", "ru")
            else:
                lang = "ru"
            if res == "":
                print(self.tAPI.send("Нет перевода!", tmsg.chat_id, tmsg.id))
            elif lang == "":
                lang = "en"
            if lang != "":
                print(self.tAPI.send(res, tmsg.chat_id, tmsg.id))
                if self.tAPI.DB_IS_ENABLED:
                    collection.insert_one({"word": txt, "trl": res})
                    self.tAPI.db[str(tmsg.pers_id)]['known_words'].insert_one(
                        {
                            "word": txt,
                            "lang": lang,
                            "lastRevised": datetime.datetime.utcnow()
                        }
                    )
        else:
            print(self.tAPI.send("l " + post["trl"], tmsg.chat_id, tmsg.id))

        if is_chain:
            self.waitlist.remove((tmsg.pers_id, tmsg.chat_id))
        return 0


class Info(BaseWorker):

    def is_it_for_me(self, tmsg):
        return tmsg.text.startswith("/help") or tmsg.text.startswith("/start")

    def run(self, tmsg):
        HELP = "" # "Storage is " + ("on" if self.tAPI.DB_IS_ENABLED else "off") + "!\n\n"
        for worker in WorkersList.workers:
            HELP += worker[1].HELP
        HELP = HELP[:-2]
        self.tAPI.send(HELP, tmsg.chat_id)


class PhraseTranslator(BaseWorker):

    HELP = ("/ph** текст - перевод на язык с кодом ** текста до первой точки, если есть, иначе полностью.\n"
            "Список кодов языков: https://tech.yandex.ru/translate/doc/dg/concepts/langs-docpage/\n"
            "Переведено «Яндекс.Переводчиком», http://translate.yandex.ru/\n\n")

    waitlist = dict()

    def is_it_for_me(self, tmsg):
        return tmsg.text.startswith("/ph") or ((tmsg.pers_id, tmsg.chat_id) in self.waitlist)

    def run(self, tmsg):
        is_chain = self.waitlist.get((tmsg.pers_id, tmsg.chat_id), False)
        txt = ""
        if not is_chain:
            if len(tmsg.text) < 6:
                self.tAPI.send("Введите фразу.", tmsg.chat_id)
                self.waitlist[(tmsg.pers_id, tmsg.chat_id)] = tmsg.text[3:5]
                return 1
            else:
                txt = tmsg.text[5:].lstrip()
        else:
            txt = tmsg.text.lstrip()
        if txt.startswith("/"):
            txt = txt[1:]
        brd = txt.find('.')
        if brd != -1:
            txt = txt[: brd+1]
        # res = ""
        if is_chain:
            res = self.tAPI.translateph(txt, self.waitlist[(tmsg.pers_id, tmsg.chat_id)], "ru")
        else:
            res = self.tAPI.translateph(txt, tmsg.text[3:5], "ru")
        if res == "":
            print(self.tAPI.send("Нет перевода!", tmsg.chat_id, tmsg.id))
        else:
            print(self.tAPI.send(res, tmsg.chat_id, tmsg.id))
        if is_chain:
            self.waitlist.pop((tmsg.pers_id, tmsg.chat_id))
        return 0


class SimpleCard(BaseWorker):

    HELP = "Команда \"/cards_simple\" включает режим карточек, которые проверяет, помните ли вы некогда переведенные слова.\n\n"

    waitlist = dict()

    def is_it_for_me(self, tmsg):
        if (tmsg.pers_id, tmsg.chat_id) in self.waitlist:
            return True
        if tmsg.text.startswith("/cards_simple"):
            if not self.tAPI.DB_IS_ENABLED:
                print(self.tAPI.send("Этот режим сейчас недоступен!", tmsg.chat_id, tmsg.id))
            elif self.tAPI.NO_CARDS_GROUPS and tmsg.chat_id != tmsg.pers_id:
                print(self.tAPI.send("Использование режима в групповом чате отключено!", tmsg.chat_id, tmsg.id))
            elif self.tAPI.db[str(tmsg.pers_id)]['known_words'].count() == 0:
                print(self.tAPI.send("Вы не переводили слов, поэтому не могу запустить этот режим.", tmsg.chat_id, tmsg.id))
            else:
                return True
        return False

    def run(self, tmsg):
        collection = self.tAPI.db[str(tmsg.pers_id)]['known_words']
        if (tmsg.pers_id, tmsg.chat_id) in self.waitlist:
            if tmsg.text == "/Stop":
                self.tAPI.send("Я вышел из режима \"simple cards\".",
                            tmsg.chat_id, tmsg.id)
                if (tmsg.pers_id, tmsg.chat_id) in self.waitlist:
                    self.waitlist.pop((tmsg.pers_id, tmsg.chat_id))
                return 0
            elif tmsg.text == "/No":
                post = collection.find_one({"_id": self.waitlist[(tmsg.pers_id, tmsg.chat_id)]})
                post = self.tAPI.db.tr.find_one({"word": post['word']})
                self.tAPI.send(post["trl"], tmsg.chat_id, tmsg.id)
                collection.update_one(
                    {"_id": self.waitlist[(tmsg.pers_id, tmsg.chat_id)]},
                    {
                        "$set": {
                            "lastRevised": datetime.datetime.utcnow()
                        }
                    }
                )
            elif tmsg.text == "/Yes":
                collection.update_one(
                    {"_id": self.waitlist[(tmsg.pers_id, tmsg.chat_id)]},
                    {
                        "$set": {
                            "lastRevised": datetime.datetime.utcnow()
                        }
                    }
                )
            else:
                self.tAPI.send("Неожиданный ответ! Попробуйте еще раз.",
                               tmsg.chat_id, tmsg.id)
                return 0
        post = collection.find_one(
        {"lastRevised" :
             {"$lt": datetime.datetime.utcnow() - datetime.timedelta(minutes=self.tAPI.COOLDOWN_M)}
        })
        if post == None:
            if (tmsg.pers_id, tmsg.chat_id) in self.waitlist:
                self.waitlist.pop((tmsg.pers_id, tmsg.chat_id))
            self.tAPI.send("Мне не о чем вас спросить сейчас, попробуйте включить этот режим через несколько("
                           + str(self.tAPI.COOLDOWN_M) +") минут.\n"
                           "Я вышел из режима \"simple cards\".",
                            tmsg.chat_id, tmsg.id)
        else:
            print(self.tAPI.telegram.send_reply_keyboard("Помните ли вы слово \"" + post['word'] + "\"?",
                                 tmsg.chat_id, [["/Yes"], ["/No"], ["/Stop"]], tmsg.id))
            self.waitlist[(tmsg.pers_id, tmsg.chat_id)] = post["_id"]
        return 0


class TranslationCard(BaseWorker):

    HELP = "Команда \"/cards_ytr\" включает режим карточек, которые проверяет, помните ли вы написание некогда переведенных слов по их переводу.\n\n"

    waitlist = dict()

    def is_it_for_me(self, tmsg):
        if (tmsg.pers_id, tmsg.chat_id) in self.waitlist:
            return True
        if tmsg.text.startswith("/cards_ytr"):
            if not self.tAPI.DB_IS_ENABLED:
                print(self.tAPI.send("Этот режим сейчас недоступен!", tmsg.chat_id, tmsg.id))
            # elif self.tAPI.NO_CARDS_GROUPS and tmsg.chat_id != tmsg.pers_id:
            #     print(self.tAPI.send("Использование режима в групповом чате отключено!", tmsg.chat_id, tmsg.id))
            elif self.tAPI.db[str(tmsg.pers_id)]['known_words'].count() == 0:
                print(self.tAPI.send("Вы не переводили слов, поэтому не могу запустить этот режим.", tmsg.chat_id, tmsg.id))
            else:
                self.tAPI.send("/Stop - остановить режим. \n /Next - следующее слово.", tmsg.chat_id, tmsg.id)
                return True
        return False

    def run(self, tmsg):
        collection = self.tAPI.db[str(tmsg.pers_id)]['known_words']
        if (tmsg.pers_id, tmsg.chat_id) in self.waitlist:
            if tmsg.text == "/Stop":
                self.tAPI.send("Я вышел из режима \"translation cards\".",
                               tmsg.chat_id, tmsg.id)
                if (tmsg.pers_id, tmsg.chat_id) in self.waitlist:
                    self.waitlist.pop((tmsg.pers_id, tmsg.chat_id))
                return 0
            else:
                if tmsg.text != "/Next":
                    tmsg.text_change_to(tmsg.text[2:].lower())
                    post = collection.find_one({"_id": self.waitlist[(tmsg.pers_id, tmsg.chat_id)]})
                    flag = tmsg.text == post['word']
                else:
                    flag = True
                if flag:
                    collection.update_one(
                        {"_id": self.waitlist[(tmsg.pers_id, tmsg.chat_id)]},
                        {
                            "$set": {
                                "lastRevised": datetime.datetime.utcnow()
                            }
                        }
                    )
                else:
                    self.tAPI.send("Попробуйте еще раз.", tmsg.chat_id, tmsg.id)
                    return 0
        post = collection.find_one(
            {"lastRevised":
                 {"$lt": datetime.datetime.utcnow() - datetime.timedelta(minutes=self.tAPI.COOLDOWN_M)}
            })
        if post == None:
            if (tmsg.pers_id, tmsg.chat_id) in self.waitlist:
                self.waitlist.pop((tmsg.pers_id, tmsg.chat_id))
            self.tAPI.send("Мне не о чем вас спросить сейчас, попробуйте включить этот режим через несколько("
                           + str(self.tAPI.COOLDOWN_M) + ") минут.\n"
                                                    "Я вышел из режима \"translation cards\".",
                           tmsg.chat_id, tmsg.id)
        else:
            print(self.tAPI.send("Напишите /* и без пробела слово, которому соответствует этот перевод:\n\"" +
                                 self.tAPI.db.tr.find_one({"word": post['word']})["trl"] + "\"",
                                 tmsg.chat_id, tmsg.id))
            self.waitlist[(tmsg.pers_id, tmsg.chat_id)] = post["_id"]
        return 0


class OptionCard(BaseWorker):

    HELP = "Команда \"/cards_4option\" включает режим карточек, которые проверяет, помните ли вы некогда переведенные слова.\n\n"

    waitlist = dict()

    def is_it_for_me(self, tmsg):
        if (tmsg.pers_id, tmsg.chat_id) in self.waitlist:
            return True
        if tmsg.text.startswith("/cards_4option"):
            if not self.tAPI.DB_IS_ENABLED:
                print(self.tAPI.send("Этот режим сейчас недоступен!", tmsg.chat_id, tmsg.id))
            elif self.tAPI.NO_CARDS_GROUPS and tmsg.chat_id != tmsg.pers_id:
                print(self.tAPI.send("Использование режима в групповом чате отключено!", tmsg.chat_id, tmsg.id))
            elif self.tAPI.db[str(tmsg.pers_id)]['known_words'].count() < 4:
                print(self.tAPI.send("Вы не перевели еще 4 слов, поэтому не могу запустить этот режим.", tmsg.chat_id,
                                     tmsg.id))
            else:
                return True
        return False

    def run(self, tmsg):
        collection = self.tAPI.db[str(tmsg.pers_id)]['known_words']
        if (tmsg.pers_id, tmsg.chat_id) in self.waitlist:
            if tmsg.text == "/Stop":
                self.tAPI.send("Я вышел из режима \"4option cards\".",
                               tmsg.chat_id, tmsg.id)
                if (tmsg.pers_id, tmsg.chat_id) in self.waitlist:
                    self.waitlist.pop((tmsg.pers_id, tmsg.chat_id))
                return 0
            else:
                if tmsg.text != "/Next":
                    tmsg.text_change_to(tmsg.text[2:])
                    post = collection.find_one({"_id": self.waitlist[(tmsg.pers_id, tmsg.chat_id)][0]})
                    flag = tmsg.text == post['word']
                else:
                    flag = True
                if flag:
                    collection.update_one(
                        {"_id": self.waitlist[(tmsg.pers_id, tmsg.chat_id)][0]},
                        {
                            "$set": {
                                "lastRevised": datetime.datetime.utcnow()
                            }
                        }
                    )
                else:
                    self.tAPI.telegram.send_reply_keyboard("Попробуйте еще раз.", tmsg.chat_id,
                                   self.waitlist[(tmsg.pers_id, tmsg.chat_id)][1], tmsg.id)
                    return 0
        post = collection.find_one(
            {"lastRevised":
                 {"$lt": datetime.datetime.utcnow() - datetime.timedelta(minutes=self.tAPI.COOLDOWN_M)}
            })
        if post == None:
            if (tmsg.pers_id, tmsg.chat_id) in self.waitlist:
                self.waitlist.pop((tmsg.pers_id, tmsg.chat_id))
            self.tAPI.send("Мне не о чем вас спросить сейчас, попробуйте включить этот режим через несколько("
                           + str(self.tAPI.COOLDOWN_M) + ") минут.\n"
                                                         "Я вышел из режима \"4option cards\".",
                           tmsg.chat_id, tmsg.id)
        else:
            current_keyboard = []
            chosen = collection.find()
            for doc in chosen:
                if doc['word'] != post['word'] and doc['lang'] == post['lang']:
                    current_keyboard.insert(random.randint(0, len(current_keyboard)), ["/*" + doc['word']])
                    if len(current_keyboard) == 3:
                        break
            if len(current_keyboard) < 3:
                print(self.tAPI.send("Вы не перевели еще 4 слов на одном языке, поэтому не могу запустить этот режим.",
                                     tmsg.chat_id, tmsg.id))
                return 0
            current_keyboard.insert(random.randint(0, len(current_keyboard)), ["/>" + post['word']])
            print(self.tAPI.telegram.send_reply_keyboard(
                "Выберите из предложенных слов слово, которому соответствует этот перевод:\n\"" +
                self.tAPI.db.tr.find_one({"word": post['word']})["trl"] + "\"",
                tmsg.chat_id, current_keyboard, tmsg.id))
            self.waitlist[(tmsg.pers_id, tmsg.chat_id)] = [post["_id"], current_keyboard]
        return 0


class HangCard(BaseWorker):

    HELP = "Команда \"/cards_hang\" включает игровой режим карточек, Вам нужно угадать некогда переведенное слово.\n\n"

    waitlist = dict()

    def is_it_for_me(self, tmsg):
        if (tmsg.pers_id, tmsg.chat_id) in self.waitlist:
            return True
        if tmsg.text.startswith("/cards_hang"):
            if not self.tAPI.DB_IS_ENABLED:
                print(self.tAPI.send("Этот режим сейчас недоступен!", tmsg.chat_id, tmsg.id))
            elif self.tAPI.NO_CARDS_GROUPS and tmsg.chat_id != tmsg.pers_id:
                print(self.tAPI.send("Использование режима в групповом чате отключено!", tmsg.chat_id, tmsg.id))
            elif self.tAPI.db[str(tmsg.pers_id)]['known_words'].count() == 0:
                print(self.tAPI.send("Вы не переводили слов, поэтому не могу запустить этот режим.", tmsg.chat_id, tmsg.id))
            else:
                self.tAPI.send("/Stop - остановить режим. \n /Next - следующее слово.", tmsg.chat_id, tmsg.id)
                return True
        return False

    def run(self, tmsg):
        collection = self.tAPI.db[str(tmsg.pers_id)]['known_words']
        if (tmsg.pers_id, tmsg.chat_id) in self.waitlist:
            if tmsg.text == "/Stop":
                self.tAPI.send("Я вышел из режима \"hang cards\".",
                               tmsg.chat_id, tmsg.id)
                if (tmsg.pers_id, tmsg.chat_id) in self.waitlist:
                    self.waitlist.pop((tmsg.pers_id, tmsg.chat_id))
                return 0
            else:
                if tmsg.text != "/Next":
                    if self.existance_del(tmsg.text, self.waitlist[(tmsg.pers_id, tmsg.chat_id)][3]):
                        index = self.waitlist[(tmsg.pers_id, tmsg.chat_id)][0].find(tmsg.text[1:].lower())
                        if index == -1:
                            self.waitlist[(tmsg.pers_id, tmsg.chat_id)][2] -= 1
                            self.tAPI.telegram.send_reply_keyboard("Нет такой буквы. \n\n" +
                                           self.state_to_string(self.waitlist[(tmsg.pers_id, tmsg.chat_id)]),
                                           tmsg.chat_id, self.waitlist[(tmsg.pers_id, tmsg.chat_id)][3], tmsg.id)
                            if self.waitlist[(tmsg.pers_id, tmsg.chat_id)][2] == 0:
                                self.tAPI.send("Вы проиграли. :(\nОтвет: " + self.waitlist[(tmsg.pers_id, tmsg.chat_id)][4],
                                               tmsg.chat_id, tmsg.id)
                                self.tAPI.send("/Stop - остановить режим. \n /Next - следующее слово."
                                               , tmsg.chat_id, tmsg.id)
                            else:
                                return 0
                        else:
                            while index != -1:
                                self.waitlist[(tmsg.pers_id, tmsg.chat_id)][1] = \
                                    self.waitlist[(tmsg.pers_id, tmsg.chat_id)][1][:2*index] \
                                    + tmsg.text[1:].lower() \
                                    + self.waitlist[(tmsg.pers_id, tmsg.chat_id)][1][2*index+1:]
                                self.waitlist[(tmsg.pers_id, tmsg.chat_id)][0] = \
                                    self.waitlist[(tmsg.pers_id, tmsg.chat_id)][0][:index] \
                                    + "-" \
                                    + self.waitlist[(tmsg.pers_id, tmsg.chat_id)][0][index + 1:]
                                index = self.waitlist[(tmsg.pers_id, tmsg.chat_id)][0].find(tmsg.text[1:].lower())
                            self.tAPI.telegram.send_reply_keyboard("Есть такая буква. \n\n" +
                                           self.state_to_string(self.waitlist[(tmsg.pers_id, tmsg.chat_id)]),
                                           tmsg.chat_id, self.waitlist[(tmsg.pers_id, tmsg.chat_id)][3], tmsg.id)
                            if len(self.waitlist[(tmsg.pers_id, tmsg.chat_id)][0]) \
                                == self.waitlist[(tmsg.pers_id, tmsg.chat_id)][0].count("-"):
                                self.tAPI.send("Вы выиграли!", tmsg.chat_id, tmsg.id)
                                self.tAPI.send("/Stop - остановить режим. \n /Next - следующее слово.", tmsg.chat_id, tmsg.id)
                            else:
                                return 0
                    else:
                        self.tAPI.telegram.send_reply_keyboard("Некорректный ответ. Попробуйте еще раз. \n\n" +
                                   self.state_to_string(self.waitlist[(tmsg.pers_id, tmsg.chat_id)]),
                                   tmsg.chat_id, self.waitlist[(tmsg.pers_id, tmsg.chat_id)][3], tmsg.id)
                        return 0
        post = self.tAPI.get_random_doc(collection)
        if post == None:
            if (tmsg.pers_id, tmsg.chat_id) in self.waitlist:
                self.waitlist.pop((tmsg.pers_id, tmsg.chat_id))
            self.tAPI.send("Мне не о чем вас спросить.", tmsg.chat_id, tmsg.id)
        else:
            state = [post['word'], "- " * len(post['word']), 6, self.default_keyboard(post['lang']), post['word']]
            print(self.tAPI.telegram.send_reply_keyboard(self.state_to_string(state), tmsg.chat_id, state[3], tmsg.id))
            self.waitlist[(tmsg.pers_id, tmsg.chat_id)] = state
        return 0

    def state_to_string(self, state):
        return state[1] + "\nВаше количество жизней: " + str(state[2]) + "."

    def existance_del(self, request, keyboard):
        for i in range(0, len(keyboard)-1):
            if request in keyboard[i]:
                keyboard[i].pop(keyboard[i].index(request))
                return True
        return False

    def default_keyboard(self, lang):
        if lang == "en":
            return self.tAPI.telegram.get_reply_keyboard(
                """a\tb\tc\td\te\tf\tg\th\ti\nj\tk\tl\tm\tn\to\tp\tq\tr\ns\tt\tu\tv\tw\tx\ty\tz\nNext\tStop""")
        elif lang == "ru":
            return self.tAPI.telegram.get_reply_keyboard(
                """а\tб\tв\tг\tд\tе\tж\tз\tи\tй\nк\tл\tм\tн\tо\tп\tр\tс\tт\tу\tф\nх\tц\tч\tш\tщ\tъ\tы\tь\tю\tя\nNext\tStop""")
            # return [["/а", "/б", "/в", "/г", "/д", "/е", "/ё", "/ж", "/з", "/и", "/й"],
            #         ["/к", "/л", "/м", "/н", "/о", "/п", "/р", "/с", "/т", "/у", "/ф"],
            #         ["/х", "/ц", "/ч", "/ш", "/щ", "/ъ", "/ы", "/ь", "/э", "/ю", "/я"], ["/Next", "/Stop"]]
        else:
            return [["No keyboard for this language!"], ["/Next", "/Stop"]]