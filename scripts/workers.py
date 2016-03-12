from scripts.bot_api import API


class WorkersList(type):
    workers = []

    def __new__(mcs, name, bases, attrs, **kwargs):
        res = super(WorkersList, mcs).__new__(mcs, name, bases, attrs)
        if '__not_bot__' not in attrs:
            WorkersList.workers.append(res)
        return res

    @staticmethod
    def run_list(tmsg):
        for worker in WorkersList.workers:
            if worker.is_it_for_me(tmsg):
                cmd = worker.run(tmsg)
                if cmd == 2:
                    return False
                break
        return True


class Blacklist(API):
    # __metaclass__ = WorkersList

    def is_it_for_me(self, tmsg):
        if(self.DB_IS_ENABLED):
            collection = self.db.blacklist
            return collection.find_one({"pers_id": str(tmsg.pers_id)}) is not None
        return False

    def run(self, tmsg):
        return 0


class Stop(API):
    # __metaclass__ = WorkersList

    def is_it_for_me(self, tmsg):
        return tmsg.text == "/StopPls"

    def run(self, tmsg):
        self.send("I'll be back, " + tmsg.name + "!", tmsg.chat_id)
        return 2


class Translator(API):
    # __metaclass__ = WorkersList
    waitlist = set()

    def is_it_for_me(self, tmsg):
        return tmsg.text.startswith("/tr") or ((tmsg.pers_id, tmsg.chat_id) in self.waitlist)

    def run(self, tmsg):
        is_chain = (tmsg.pers_id, tmsg.chat_id) in self.waitlist
        txt = ""
        tmsg.textmod()
        if not is_chain:
            if len(tmsg.text) < 4:
                self.send("Введите слово.", tmsg.chat_id)
                self.waitlist.add((tmsg.pers_id, tmsg.chat_id))
                return 1
            else:
                txt = tmsg.text[3:].lstrip()
        else:
            txt = tmsg.text.lstrip()
        # res = ""
        post = None
        if (self.DB_IS_ENABLED):
            collection = self.db.tr
            post = collection.find_one({"word": txt})
        if post is None:
            res = self.translate(txt, "ru-en", "ru")
            if res == "":
                res = self.translate(txt, "en-ru", "ru")
            if res == "":
                print(self.send("Нет перевода!", tmsg.chat_id, tmsg.id))
            else:
                print(self.send(res, tmsg.chat_id, tmsg.id))
                if (self.DB_IS_ENABLED):
                    collection.insert_one({"word": txt, "trl": res})
        else:
            print(self.send("l " + post["trl"], tmsg.chat_id, tmsg.id))

        if is_chain:
            self.waitlist.remove((tmsg.pers_id, tmsg.chat_id))
        return 0


class Info(API):
    # __metaclass__ = WorkersList
    def is_it_for_me(self, tmsg):
        return tmsg.text.startswith("/help")

    def run(self, tmsg):
        self.send("/tr слово - переводит слово с английского на русский или с русского на английский.\n"
                  "/ph** текст - перевод на язык с кодом ** текста до первой точки, если есть, иначе полностью.\n"
                  "Список кодов языков: https://tech.yandex.ru/translate/doc/dg/concepts/langs-docpage/\n"
                  "Перевод слов: Реализовано с помощью сервиса «Яндекс.Словарь», https://tech.yandex.ru/dictionary/\n"
                  "Перевод текста: Переведено «Яндекс.Переводчиком», http://translate.yandex.ru/", tmsg.chat_id)


class PhraseTranslator(API):
    # __metaclass__ = WorkersList
    waitlist = dict()

    def is_it_for_me(self, tmsg):
        return tmsg.text.startswith("/ph") or ((tmsg.pers_id, tmsg.chat_id) in self.waitlist)

    def run(self, tmsg):
        is_chain = self.waitlist.get((tmsg.pers_id, tmsg.chat_id), False)
        txt = ""
        if not is_chain:
            if len(tmsg.text) < 6:
                self.send("Введите фразу.", tmsg.chat_id)
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
            res = self.translateph(txt, self.waitlist[(tmsg.pers_id, tmsg.chat_id)], "ru")
        else:
            res = self.translateph(txt, tmsg.text[3:5], "ru")
        if res == "":
            print(self.send("Нет перевода!", tmsg.chat_id, tmsg.id))
        else:
            print(self.send(res, tmsg.chat_id, tmsg.id))
        if is_chain:
            self.waitlist.pop((tmsg.pers_id, tmsg.chat_id))
        return 0
