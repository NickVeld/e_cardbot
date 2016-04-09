# -*- coding: utf-8 -*-

import datetime


class WorkersList(type):
    workers = []

    def __new__(mcs, name, bases, attrs, **kwargs):
        worker_class = super(WorkersList, mcs).__new__(mcs, name, bases, attrs)
        if '__not_bot__' not in attrs:
            WorkersList.workers.append((name, worker_class))
        return worker_class

    # @staticmethod
    # def run_list(tmsg):
    #     for worker in WorkersList.workers:
    #         if worker.is_it_for_me(tmsg):
    #             cmd = worker.run(tmsg)
    #             if cmd == 2:
    #                 return False
    #             break
    #     return True


class BaseWorker(object, metaclass=WorkersList):
    __not_bot__ = True

    HELP = ""
    tAPI = None
    
    def __init__(self, teleapi):
        self.tAPI = teleapi


class Blacklist(BaseWorker):
    HELP = "There is a blacklist for rude users!\n\n"

    def is_it_for_me(self, tmsg):
        if self.tAPI.DB_IS_ENABLED:
            collection = self.tAPI.db.blacklist
            return collection.find_one({"pers_id": str(tmsg.pers_id)}) is not None
        return False

    def run(self, tmsg):
        return 0


class Stop(BaseWorker):

    def is_it_for_me(self, tmsg):
        return tmsg.text == "/StopPls"

    def run(self, tmsg):
        self.tAPI.send("I'll be back, " + tmsg.name + "!", tmsg.chat_id)
        return 2


class Translator(BaseWorker):
    HELP = ("/tr слово - переводит слово с английского на русский или с русского на английский.\n"
            "Реализовано с помощью сервиса «Яндекс.Словарь», https://tech.yandex.ru/dictionary/\n\n")

    waitlist = set()

    def is_it_for_me(self, tmsg):
        return tmsg.text.startswith("/tr") or ((tmsg.pers_id, tmsg.chat_id) in self.waitlist)

    def run(self, tmsg):
        is_chain = (tmsg.pers_id, tmsg.chat_id) in self.waitlist
        txt = ""
        tmsg.textmod()
        if not is_chain:
            if len(tmsg.text) < 4:
                self.tAPI.send("Введите слово.", tmsg.chat_id)
                self.waitlist.add((tmsg.pers_id, tmsg.chat_id))
                return 1
            else:
                txt = tmsg.text[3:].lstrip()
        else:
            txt = tmsg.text.lstrip()
        # res = ""
        post = None
        if (self.tAPI.DB_IS_ENABLED):
            collection = self.tAPI.db.tr
            post = collection.find_one({"word": txt})
        if post is None:
            res = self.tAPI.translate(txt, "ru-en", "ru")
            if res == "":
                res = self.tAPI.translate(txt, "en-ru", "ru")
            if res == "":
                print(self.tAPI.send("Нет перевода!", tmsg.chat_id, tmsg.id))
            else:
                print(self.tAPI.send(res, tmsg.chat_id, tmsg.id))
                if (self.tAPI.DB_IS_ENABLED):
                    collection.insert_one({"word": txt, "trl": res})
                    self.tAPI.db[str(tmsg.pers_id)].insert_one({"word": txt})
        else:
            print(self.tAPI.send("l " + post["trl"], tmsg.chat_id, tmsg.id))

        if is_chain:
            self.waitlist.remove((tmsg.pers_id, tmsg.chat_id))
        return 0


class Info(BaseWorker):

    def is_it_for_me(self, tmsg):
        return tmsg.text.startswith("/help")

    def run(self, tmsg):
        HELP = ""
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

    HELP = "\"/simplecards\" turn on mode of revising known words.\n\n"

    waitlist = dict()

    def is_it_for_me(self, tmsg):
        if (tmsg.pers_id, tmsg.chat_id) in self.waitlist:
            return True
        if tmsg.text.startswith("/simple_cards"):
            if not self.tAPI.DB_IS_ENABLED:
                print(self.tAPI.send("I can't start card mode!", tmsg.chat_id, tmsg.id))
            elif self.tAPI.db[str(tmsg.pers_id)]['known_words'].count() == 0:
                print(self.tAPI.send("You didn't translate any words!", tmsg.chat_id, tmsg.id))
            else:
                print("True")
                return True
        return False

    def run(self, tmsg):
        collection = self.tAPI.db[str(tmsg.pers_id)]['known_words']
        if (tmsg.pers_id, tmsg.chat_id) in self.waitlist:
            if tmsg.text == "No":
                post = collection.find_one({"_id": self.waitlist[(tmsg.pers_id, tmsg.chat_id)]})
                post = self.tAPI.db.tr.find_one({"word": post.word})
                print(self.tAPI.send(post["trl"], tmsg.chat_id, tmsg.id))
                tmsg.text = "Yes"
            if tmsg.text == "Yes":
                collection.update_one(
                    {"_id": self.waitlist[(tmsg.pers_id, tmsg.chat_id)]},
                    {
                        "date": datetime.datetime.utcnow()
                    }
                )
        post = None
        if tmsg.text != "Stop":
            post = collection.find_one(
            {"lastRevised" :
                 {"$lt": datetime.datetime.utcnow() - datetime.datetime(0, 0, 0, 0, 5, 0, 0)}
            })
        if post == None:
            self.waitlist.pop((tmsg.pers_id, tmsg.chat_id))
        else:
            print(self.tAPI.send("Do you remember the word " + post.word + " ?", tmsg.chat_id, tmsg.id))
            self.waitlist[(tmsg.pers_id, tmsg.chat_id)] = post._id
        return 0
