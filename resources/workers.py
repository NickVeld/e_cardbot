from resources.bot_api import api
from resources.msg_module import msgc

class blacklist(api):
    def is_it_for_me(self, msg):
        return msgc.pers_id(msg) == 124147029

    def run(self, msg):
        return 0

class stop(api):
    def is_it_for_me(self, msg):
        return msgc.text(msg)== "/StopPls"

    def run(self, msg):
        self.send("I'll be back, " + msgc.name(msg) + "!", msgc.chat_id(msg))
        return 2

class tr(api):
    waitlist = set()

    def is_it_for_me(self, msg):
        return msgc.text(msg).startswith("/tr") or ((msgc.pers_id(msg), msgc.chat_id(msg)) in self.waitlist)


    def run(self, msg):
        is_chain = (msgc.pers_id(msg), msgc.chat_id(msg)) in self.waitlist
        txt = ""
        if not (is_chain):
            if len(msgc.text(msg)) < 4:
                self.send("Введите слово.", msgc.chat_id(msg))
                self.waitlist.add((msgc.pers_id(msg), msgc.chat_id(msg)))
                return 1
            else:
                txt = msgc.text(msg)[3:].lstrip()
        else:
            txt = msgc.text(msg).lstrip()
        # res = ""
        res = self.translate(txt, "ru-en", "ru")
        if res == "":
            res = self.translate(txt, "en-ru", "ru")
        if res == "":
            print(self.send("Нет перевода!", msgc.chat_id(msg), msgc.id(msg)))
        else:
            print(self.send(res, msgc.chat_id(msg), msgc.id(msg)))
        if is_chain:
            self.waitlist.remove((msgc.pers_id(msg), msgc.chat_id(msg)))
        return 0

class help(api):
    def is_it_for_me(self, msg):
        return msgc.text(msg).startswith("/help")

    def run(self, msg):
        self.send("/tr слово - переводит слово с английского на русский или с русского на английский.\n/ph** текст - перевод на язык с кодом ** текста до первой точки, если есть, иначе полностью.\nСписок кодов языков: https://tech.yandex.ru/translate/doc/dg/concepts/langs-docpage/\nПеревод слов: Реализовано с помощью сервиса «Яндекс.Словарь», https://tech.yandex.ru/dictionary/\nПеревод текста: Переведено «Яндекс.Переводчиком», http://translate.yandex.ru/", msgc.chat_id(msg))

class ph(api):
    waitlist = dict()
    def is_it_for_me(self, msg):
        return msgc.text(msg).startswith("/ph") or ((msgc.pers_id(msg), msgc.chat_id(msg)) in self.waitlist)

    def run(self, msg):
        is_chain = self.waitlist.get((msgc.pers_id(msg), msgc.chat_id(msg)), False)
        txt = ""
        if not (is_chain):
            if len(msgc.text(msg)) < 6:
                self.send("Введите фразу.", msgc.chat_id(msg))
                self.waitlist[(msgc.pers_id(msg), msgc.chat_id(msg))] = msgc.text(msg)[3:5]
                return 1
            else:
                txt = msgc.text(msg)[5:].lstrip()
        else:
            txt = msgc.text(msg).lstrip()
        if txt.startswith("/"):
            txt = txt[1:]
        brd = txt.find('.')
        if brd != -1:
            txt = txt[ : brd+1]
        # res = ""
        if is_chain:
            res = self.translateph(txt, self.waitlist[(msgc.pers_id(msg), msgc.chat_id(msg))], "ru")
        else:
            res = self.translateph(txt, msgc.text(msg)[3:5], "ru")
        if res == "":
            print(self.send("Нет перевода!", msgc.chat_id(msg), msgc.id(msg)))
        else:
            print(self.send(res, msgc.chat_id(msg), msgc.id(msg)))
        if is_chain:
            self.waitlist.pop((msgc.pers_id(msg), msgc.chat_id(msg)))
        return 0