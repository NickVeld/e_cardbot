# -*- coding: utf-8 -*-

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
    
    def __init__(self, teleapi):
        self.tAPI = teleapi
        self.MENU_KEYBOARD = [
            [{'text': "Перевести слово", 'callback_data': Translator.COMMAND}
                , {'text': "Удалить карточку", 'callback_data': CardDeleter.COMMAND}],
            [{'text': "Перевести фразу на русский", 'callback_data': PhraseTranslator.COMMAND+'ru'}
                , {'text': "Перевести фразу на английский", 'callback_data': PhraseTranslator.COMMAND+'en'}],
            [{'text': "Карточки знаю/не знаю", 'callback_data': SimpleCard.COMMAND}
                , {'text': "Карточки на знание перевода", 'callback_data': TranslationCard.COMMAND}],
            [{'text': "Карточки с 4 опциями ответа", 'callback_data': OptionCard.COMMAND}
                , {'text': "Виселица", 'callback_data': HangCard.COMMAND}],
            [{'text': "Помощь/дополнительная информация", 'callback_data': Info.COMMAND}]
        ]



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

    def quit(self, pers_id, chat_id, additional_info = '', msg_id=None):
        pass


class Stop(BaseWorker):
    COMMAND = "/StopPls"

    def is_it_for_me(self, tmsg):
        return (tmsg.text == self.COMMAND) and (str(tmsg.pers_id) == self.tAPI.admin_ids[0])

    def run(self, tmsg):
        print(self.tAPI.send("I'll be back, " + tmsg.name + "!", tmsg.chat_id))
        return 2

    def quit(self, pers_id, chat_id, additional_info = '', msg_id = 0):
        pass


class Humanity(BaseWorker):
    HELP = "Поддерживается понимание некоторых человеческих фраз, список команд можно посмотреть," \
           "введя слово \"команды\"\n\n"

    def __init__(self, teleapi):
        super(Humanity, self).__init__(teleapi)
        self.waitlist = set()
        import re
        self.re = re

    def is_it_for_me(self, tmsg):
        return not (tmsg.is_inline)

    def run(self, tmsg):
        tmsg.text_change_to(tmsg.text.lower())
        if self.re.match(r"^(((\/| )*)команды)", tmsg.text):
            self.tAPI.send("Список фраз:\n\"переведи слово\", после этого пишите свое слово\n"
                           "\"переведи фразу на английский\", после этого пишите свою фразу"
                           "\"переведи фразу на русский\", после этого пишите свою фразу"
                           "\"давай карточки\", выбирается случайный режим", tmsg.chat_id, tmsg.id)
            return 0
        tmsg.text_replace(r"^(((\/| )*)переведи(.*)слово)", Translator.COMMAND, self.re.sub)
        tmsg.text_replace(r"^(((\/| )*)переведи(.*)на английский)", PhraseTranslator.COMMAND + "en", self.re.sub)
        tmsg.text_replace(r"^(((\/| )*)переведи(.*)на русский)", PhraseTranslator.COMMAND + "ru", self.re.sub)
        tmsg.text_replace(r"^(((\/| )*)удали(.*)карточку)", CardDeleter.COMMAND, self.re.sub)
        choice = random.randint(0, 4)
        if choice == 1:
            choice = TranslationCard.COMMAND
        elif choice == 2:
            choice = OptionCard.COMMAND
        elif choice == 3:
            choice = HangCard.COMMAND
        else:
            choice = SimpleCard.COMMAND
        tmsg.text_replace(r"^(((\/| )*)давай(.*)карточки)", choice, self.re.sub)
        return 1

    def quit(self, pers_id, chat_id, additional_info = '', msg_id = 0):
        pass


class Translator(BaseWorker):
    COMMAND = "/tr"
    HELP = COMMAND + " слово - бот переводит слово с английского на русский или с русского на английский и"\
            "добавляет карточку с этим словом в Ваш набор.\n"\
            "Реализовано с помощью сервиса «Яндекс.Словарь», https://tech.yandex.ru/dictionary/\n" \
            "Проверка правописания: Яндекс.Спеллер, http://api.yandex.ru/speller/\n\n"

    waitlist = set()

    def is_it_for_me(self, tmsg):
        return tmsg.text.startswith(self.COMMAND) or (not tmsg.is_inline and (((tmsg.pers_id, tmsg.chat_id) in self.waitlist or
                                               ((tmsg.pers_id == tmsg.chat_id) and not tmsg.text.startswith("/")))))

    def run(self, tmsg):
        if (tmsg.pers_id == tmsg.chat_id):
            self.tAPI.db_shell.modify_last_activity(tmsg.pers_id, False)
        is_chain = (tmsg.pers_id, tmsg.chat_id) in self.waitlist
        txt = ""
        if not (is_chain or
                ((tmsg.pers_id == tmsg.chat_id) and not tmsg.text.startswith("/"))):
            if len(tmsg.text) < 4:
                self.tAPI.send("Введите слово.", tmsg.chat_id)
                self.waitlist.add((tmsg.pers_id, tmsg.chat_id))
                return 1
            else:
                txt = tmsg.text[3:].lstrip().lower()
        else:
            txt = tmsg.text.lstrip().lower()
        if txt.startswith('/'):
            txt = txt[1:]
        txt = txt[:50]
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
                print(self.tAPI.send_inline_keyboard("Нет перевода!", tmsg.chat_id, self.MENU_KEYBOARD, tmsg.id))
            elif lang == "":
                lang = "en"
            if lang != "":
                with_mistake = res.startswith("*_%")
                if with_mistake:
                    res = res[3:]

                print(self.tAPI.send_inline_keyboard(("Возможно, Вы имели ввиду: "
                                      if with_mistake else "") + res, tmsg.chat_id, self.MENU_KEYBOARD, tmsg.id))
                if self.tAPI.DB_IS_ENABLED:
                    self.tAPI.insert_doc_for_card(tmsg, collection, txt, lang, res)
        else:
            print(self.tAPI.send_inline_keyboard("l " + post["trl"], tmsg.chat_id, self.MENU_KEYBOARD, tmsg.id))

        self.tAPI.db_shell.modify_activity(tmsg.pers_id, 1)

        self.quit(tmsg.pers_id, tmsg.chat_id)
        return 0

    def quit(self, pers_id, chat_id, additional_info = '', msg_id = 0):
        if (pers_id, chat_id) in self.waitlist:
            self.waitlist.remove((pers_id, chat_id))
            if additional_info != '':
                self.tAPI.send_inline_keyboard(additional_info, chat_id, self.MENU_KEYBOARD, msg_id)


class CardDeleter(BaseWorker):
    COMMAND = "/rm"
    HELP = COMMAND + " слово - бот удаляет карточку с данным словом из Вашего набора.\n\n"

    waitlist = set()

    def is_it_for_me(self, tmsg):
        if ((tmsg.pers_id, tmsg.chat_id) in self.waitlist) and tmsg.is_inline:
            return True
        if tmsg.text.startswith(self.COMMAND):
            if not self.tAPI.DB_IS_ENABLED:
                print(self.tAPI.send("Этот режим сейчас недоступен!", tmsg.chat_id, tmsg.id))
            elif self.tAPI.NO_CARDS_GROUPS and (tmsg.chat_id != tmsg.pers_id):
                print(self.tAPI.send("Использование режима в групповом чате отключено!", tmsg.chat_id, tmsg.id))
            elif self.tAPI.db[str(tmsg.pers_id)]['known_words'].count() == 0 and not self.tAPI.db_shell.TEST_WORDS:
                print(self.tAPI.send("Вы не переводили слов, поэтому не могу запустить этот режим.", tmsg.chat_id,
                                     tmsg.id))
            else:
                return True
        return False

    def run(self, tmsg):
        if (tmsg.pers_id == tmsg.chat_id):
            self.tAPI.db_shell.modify_last_activity(tmsg.pers_id, False)
        is_chain = (tmsg.pers_id, tmsg.chat_id) in self.waitlist
        txt = ""
        if not (is_chain or
                    ((tmsg.pers_id == tmsg.chat_id) and not tmsg.text.startswith("/"))):
            if len(tmsg.text) < 4:
                self.tAPI.send("Введите слово.", tmsg.chat_id)
                self.waitlist.add((tmsg.pers_id, tmsg.chat_id))
                return 1
            else:
                txt = tmsg.text[3:].lstrip().lower()
        else:
            txt = tmsg.text.lstrip().lower()
        if txt.startswith('/'):
            txt = txt[1:]
        txt = txt[:50]
        collection = self.tAPI.db[str(tmsg.pers_id)]["known_words"]
        del_c = collection.delete_one({"word": txt}).deleted_count
        print(self.tAPI.send_inline_keyboard("Карточка успешно удалена" if del_c else "Такой карточки нет."
                                             , tmsg.chat_id, self.MENU_KEYBOARD, tmsg.id))

        self.quit(tmsg.pers_id, tmsg.chat_id)
        return 0

    def quit(self, pers_id, chat_id, additional_info = '', msg_id = 0):
        if (pers_id, chat_id) in self.waitlist:
            self.waitlist.remove((pers_id, chat_id))
            if additional_info != '':
                self.tAPI.send_inline_keyboard(additional_info, chat_id, self.MENU_KEYBOARD, msg_id)


class Info(BaseWorker):
    COMMAND = "/help"

    def is_it_for_me(self, tmsg):
        return tmsg.text.startswith(self.COMMAND) or tmsg.text.startswith("/start")

    def run(self, tmsg):
        if tmsg.text.startswith("/start"):
            self.tAPI.db_shell.initialize_user(tmsg.pers_id)
        if (tmsg.pers_id == tmsg.chat_id):
            self.tAPI.db_shell.modify_last_activity(tmsg.pers_id, False)
        HELP = ""
            # "Включен режим презентации, Вы можете получить слова из банка." if self.tAPI.db_shell.TEST_WORDS else ""
            # "Storage is " + ("on" if self.tAPI.DB_IS_ENABLED else "off") + "!\n\n"
        for worker in WorkersList.workers:
            HELP += worker[1].HELP
        HELP = HELP[:-2]
        self.tAPI.send_inline_keyboard(HELP, tmsg.chat_id, self.MENU_KEYBOARD)
        return 0

    def quit(self, pers_id, chat_id, additional_info = '', msg_id = 0):
        pass


class PhraseTranslator(BaseWorker):
    COMMAND = "/ph"
    HELP =  COMMAND + "** текст - перевод на язык с кодом ** текста до первой точки, если есть, иначе полностью.\n"\
            "Список кодов языков: https://tech.yandex.ru/translate/doc/dg/concepts/api-overview-docpage/#languages\n"\
            "Переведено «Яндекс.Переводчиком», http://translate.yandex.ru/\n\n"

    waitlist = dict()

    def is_it_for_me(self, tmsg):
        return tmsg.text.startswith(self.COMMAND) or ((tmsg.pers_id, tmsg.chat_id) in self.waitlist)

    def run(self, tmsg):
        if (tmsg.pers_id == tmsg.chat_id):
            self.tAPI.db_shell.modify_last_activity(tmsg.pers_id, False)
        is_chain = self.waitlist.get((tmsg.pers_id, tmsg.chat_id), False)
        txt = ""
        if not is_chain:
            if len(tmsg.text) < 6:
                self.tAPI.send("Введите фразу.", tmsg.chat_id)
                self.waitlist[(tmsg.pers_id, tmsg.chat_id)] = tmsg.text[3:5]
                return 1
            else:
                txt = tmsg.text[5:5005 if len(tmsg.text) > 5005 else len(tmsg.text)].lstrip()
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
            print(self.tAPI.send("Нет перевода!", tmsg.chat_id, self.MENU_KEYBOARD, tmsg.id))
        else:
            print(self.tAPI.send(res, tmsg.chat_id, self.MENU_KEYBOARD, tmsg.id))
        self.quit(tmsg.pers_id, tmsg.chat_id)
        return 0

    def quit(self, pers_id, chat_id, additional_info='', msg_id=None):
        if (pers_id, chat_id) in self.waitlist:
            self.waitlist.pop((pers_id, chat_id))
            if additional_info != '':
                self.tAPI.send_inline_keyboard(additional_info, chat_id, self.MENU_KEYBOARD)


class SimpleCard(BaseWorker):
    COMMAND = "/cards_simple"
    HELP = "Команда \"" + COMMAND + "\" включает режим карточек"\
            ", которые проверяют, помните ли вы некогда переведенные слова.\n\n"

    waitlist = dict()

    def is_it_for_me(self, tmsg):
        if ((tmsg.pers_id, tmsg.chat_id) in self.waitlist) and tmsg.is_inline:
            return True
        if tmsg.text.startswith(self.COMMAND):
            if not self.tAPI.DB_IS_ENABLED:
                print(self.tAPI.send("Этот режим сейчас недоступен!", tmsg.chat_id, tmsg.id))
            elif self.tAPI.NO_CARDS_GROUPS and (tmsg.chat_id != tmsg.pers_id):
                print(self.tAPI.send("Использование режима в групповом чате отключено!", tmsg.chat_id, tmsg.id))
            elif self.tAPI.db[str(tmsg.pers_id)]['known_words'].count() == 0 and not self.tAPI.db_shell.TEST_WORDS:
                print(self.tAPI.send("Вы не переводили слов, поэтому не могу запустить этот режим.", tmsg.chat_id, tmsg.id))
            else:
                self.tAPI.db_shell.modify_activity(tmsg.pers_id, 1)
                return True
        return False

    def run(self, tmsg):
        if (tmsg.pers_id == tmsg.chat_id):
            self.tAPI.db_shell.modify_last_activity(tmsg.pers_id, False)
        collection = self.tAPI.db[str(tmsg.pers_id)]['known_words']
        try:
            history = self.waitlist[(tmsg.pers_id, tmsg.chat_id)][2]
        except:
            history = ""
        if (tmsg.pers_id, tmsg.chat_id) in self.waitlist:
            self.waitlist[(tmsg.pers_id, tmsg.chat_id)][3] = tmsg.id
            if tmsg.text == "/Stop":
                self.quit(tmsg.pers_id, tmsg.chat_id, msg_id=tmsg.id)
                return 0
            elif tmsg.text == "/No":
                post = (collection if self.waitlist[(tmsg.pers_id, tmsg.chat_id)][1]
                                else self.tAPI.db['common']).find_one(
                    {"_id": self.waitlist[(tmsg.pers_id, tmsg.chat_id)][0]}
                )
                post = self.tAPI.db.tr.find_one({"word": post['word']})
                history = history + post["word"] + ':\n' + post["trl"] + '\n\n'
                # self.tAPI.send(post["trl"], tmsg.chat_id, tmsg.id)
                self.tAPI.update_doc_for_card(self.waitlist[(tmsg.pers_id, tmsg.chat_id)][1]
                                              , tmsg.pers_id, self.waitlist[(tmsg.pers_id, tmsg.chat_id)][0], False)
            elif tmsg.text == "/Yes":
                self.tAPI.update_doc_for_card(self.waitlist[(tmsg.pers_id, tmsg.chat_id)][1]
                                              , tmsg.pers_id, self.waitlist[(tmsg.pers_id, tmsg.chat_id)][0], True)
            else:
                self.tAPI.send("Неожиданный ответ! Попробуйте еще раз.",
                               tmsg.chat_id, tmsg.id)
                return 0
        res = self.tAPI.get_doc_for_card(tmsg, collection)
        post = res[0]
        if post == None:
            self.quit(tmsg.pers_id, tmsg.chat_id, "Мне не о чем вас спросить сейчас, попробуйте включить этот режим через несколько("\
                   + str(self.tAPI.COOLDOWN_M) +") минут.\n", tmsg.id)
        else:
            self.waitlist[(tmsg.pers_id, tmsg.chat_id)] = res[1]
            self.waitlist[(tmsg.pers_id, tmsg.chat_id)].append(history)
            if tmsg.is_inline:
                print(self.tAPI.edit(history + "Помните ли вы слово \"" + post['word'] + "\"?",
                                 tmsg.chat_id, self.tAPI.get_inline_text_keyboard("Yes\nNo\nStop"), tmsg.id))
                self.waitlist[(tmsg.pers_id, tmsg.chat_id)].append(tmsg.id)
            else:
                self.waitlist[(tmsg.pers_id, tmsg.chat_id)].append(
                    self.tAPI.send_inline_keyboard_with_id("Помните ли вы слово \"" + post['word'] + "\"?",
                                 tmsg.chat_id, self.tAPI.get_inline_text_keyboard("Yes\nNo\nStop"), tmsg.id))
        return 0

    def quit(self, pers_id, chat_id, additional_info = '', msg_id = 0):
        if (pers_id, chat_id) in self.waitlist:
            draft = additional_info + "Я вышел из режима \"simple cards\"."
            if msg_id == 0:
                msg_id = self.waitlist[(pers_id, chat_id)][3]
            self.waitlist.pop((pers_id, chat_id))
            self.tAPI.edit(draft, chat_id, self.MENU_KEYBOARD, msg_id)


class TranslationCard(BaseWorker):
    COMMAND = "/cards_ytr"
    HELP = "Команда \"" + COMMAND + "\" включает режим карточек"\
            ", которые проверяют, помните ли вы написание некогда переведенных слов по их переводу.\n\n"

    waitlist = dict()

    def is_it_for_me(self, tmsg):
        if (tmsg.pers_id, tmsg.chat_id) in self.waitlist:
            return True
        if tmsg.text.startswith(self.COMMAND):
            if not self.tAPI.DB_IS_ENABLED:
                print(self.tAPI.send("Этот режим сейчас недоступен!", tmsg.chat_id, tmsg.id))
            elif self.tAPI.NO_CARDS_GROUPS and tmsg.chat_id != tmsg.pers_id:
                print(self.tAPI.send("Использование режима в групповом чате отключено!", tmsg.chat_id, tmsg.id))
            elif self.tAPI.db[str(tmsg.pers_id)]['known_words'].count() == 0 and not self.tAPI.db_shell.TEST_WORDS:
                print(self.tAPI.send("Вы не переводили слов, поэтому не могу запустить этот режим.", tmsg.chat_id, tmsg.id))
            else:
                self.tAPI.send("/Stop - остановить режим. \n /Next - следующее слово.", tmsg.chat_id, tmsg.id)
                self.tAPI.db_shell.modify_activity(tmsg.pers_id, 10)
                return True
        return False

    def run(self, tmsg):
        if (tmsg.pers_id == tmsg.chat_id):
            self.tAPI.db_shell.modify_last_activity(tmsg.pers_id, False)
        collection = self.tAPI.db[str(tmsg.pers_id)]['known_words']
        if (tmsg.pers_id, tmsg.chat_id) in self.waitlist:
            self.waitlist[(tmsg.pers_id, tmsg.chat_id)][2] = tmsg.id
            if tmsg.text == "/Stop":
                self.quit(tmsg.pers_id, tmsg.chat_id, msg_id=tmsg.id)
                return 0
            else:
                if tmsg.text != "/Next":
                    post = (collection if self.waitlist[(tmsg.pers_id, tmsg.chat_id)][1]
                            else self.tAPI.db['common']).find_one(
                        {"_id": self.waitlist[(tmsg.pers_id, tmsg.chat_id)][0]}
                    )
                    flag = tmsg.text[2:].lower() == post['word']
                else:
                    flag = True
                if flag:
                    self.tAPI.update_doc_for_card(self.waitlist[(tmsg.pers_id, tmsg.chat_id)][1]
                                                  , tmsg.pers_id, self.waitlist[(tmsg.pers_id, tmsg.chat_id)][0], True)
                else:
                    self.tAPI.send("Попробуйте еще раз.", tmsg.chat_id, tmsg.id)
                    return 0
        res = self.tAPI.get_doc_for_card(tmsg, collection)
        post = res[0]
        if post == None:
            self.quit(tmsg.pers_id, tmsg.chat_id, "Мне не о чем вас спросить сейчас, попробуйте включить этот режим через несколько("
                           + str(self.tAPI.COOLDOWN_M) + ") минут.\n", tmsg.id)
        else:
            self.waitlist[(tmsg.pers_id, tmsg.chat_id)] = res[1]
            self.waitlist[(tmsg.pers_id, tmsg.chat_id)].append(
                self.tAPI.send_with_id("Напишите /* и без пробела слово, которому соответствует этот перевод:\n\"" +
                                 self.tAPI.db.tr.find_one({"word": post['word']})["trl"] + "\"",
                                 tmsg.chat_id, tmsg.id))
        return 0

    def quit(self, pers_id, chat_id, additional_info = '', msg_id = 0):
        if (pers_id, chat_id) in self.waitlist:
            if msg_id == 0:
                msg_id = self.waitlist[(pers_id, chat_id)][2]
            self.waitlist.pop((pers_id, chat_id))
            self.tAPI.send_inline_keyboard(additional_info + "Я вышел из режима \"translation cards\"."
                                           , chat_id, self.MENU_KEYBOARD, msg_id)


class OptionCard(BaseWorker):
    COMMAND = "/cards_4option"
    HELP = "Команда \"" + COMMAND + "\" включает режим карточек"\
           ", которые проверяют, помните ли вы некогда переведенные слова.\n\n"

    waitlist = dict()

    def is_it_for_me(self, tmsg):
        if ((tmsg.pers_id, tmsg.chat_id) in self.waitlist) and tmsg.is_inline:
            return True
        if tmsg.text.startswith(self.COMMAND):
            if not self.tAPI.DB_IS_ENABLED:
                print(self.tAPI.send("Этот режим сейчас недоступен!", tmsg.chat_id, tmsg.id))
            elif self.tAPI.NO_CARDS_GROUPS and tmsg.chat_id != tmsg.pers_id:
                print(self.tAPI.send("Использование режима в групповом чате отключено!", tmsg.chat_id, tmsg.id))
            elif not self.tAPI.db_shell.TEST_WORDS\
                    and self.tAPI.db[str(tmsg.pers_id)]['known_words'].find({'lang': 'ru'}).count() < 4 \
                    and self.tAPI.db[str(tmsg.pers_id)]['known_words'].find({'lang': 'en'}).count() < 4:
                print(self.tAPI.send("Вы не перевели еще 4 слов на одном из языков"
                                     ", поэтому не могу запустить этот режим.", tmsg.chat_id, tmsg.id))
            else:
                self.tAPI.db_shell.modify_activity(tmsg.pers_id, 10)
                return True
        return False

    def run(self, tmsg):
        if (tmsg.pers_id == tmsg.chat_id):
            self.tAPI.db_shell.modify_last_activity(tmsg.pers_id, False)
        collection = self.tAPI.db[str(tmsg.pers_id)]['known_words']
        if (tmsg.pers_id, tmsg.chat_id) in self.waitlist:
            self.waitlist[(tmsg.pers_id, tmsg.chat_id)][3] = tmsg.id
            if tmsg.text == "/Stop it":
                self.quit(tmsg.pers_id, tmsg.chat_id, msg_id=tmsg.id)
                return 0
            else:
                if tmsg.text != "/Next word":
                    post = (collection if self.waitlist[(tmsg.pers_id, tmsg.chat_id)][1]
                            else self.tAPI.db['common']).find_one(
                        {"_id": self.waitlist[(tmsg.pers_id, tmsg.chat_id)][0]}
                    )
                    flag = tmsg.text[2:].lower() == post['word']
                else:
                    flag = True
                if flag:
                    self.tAPI.update_doc_for_card(self.waitlist[(tmsg.pers_id, tmsg.chat_id)][1]
                                                  , tmsg.pers_id, self.waitlist[(tmsg.pers_id, tmsg.chat_id)][0], True)
                else:
                    print(tmsg.msg)
                    self.tAPI.edit("Попробуйте еще раз.\n" + tmsg.text_of_inline_root, tmsg.chat_id,
                                   self.waitlist[(tmsg.pers_id, tmsg.chat_id)][2], tmsg.id)
                    return 0
        res = self.tAPI.get_doc_for_card(tmsg, collection, (lambda x:len(list(
            self.tAPI.db[str(tmsg.pers_id)]['known_words'].find(
            {'lang': x}
        ))) > 3))
        post = res[0]
        if post == None:
            self.quit(tmsg.pers_id, tmsg.chat_id, "Мне не о чем вас спросить сейчас, попробуйте включить этот режим через несколько("
                           + str(self.tAPI.COOLDOWN_M) + ") минут.\n"
                                                         "Я вышел из режима \"4option cards\".",
                           tmsg.id)
        else:
            self.waitlist[(tmsg.pers_id, tmsg.chat_id)] = res[1]
            current_keyboard = self.tAPI.get_inline_text_keyboard("Next word\tStop it")
            chosen = (collection if self.waitlist[(tmsg.pers_id, tmsg.chat_id)][1]
                            else self.tAPI.db['common']).find({'lang': post['lang']})
            for doc in chosen:
                if doc['word'] != post['word']:  # and doc['lang'] == post['lang']:
                    current_keyboard.insert(random.randint(0, len(current_keyboard)-1)
                                            , [{'text': doc['word'], 'callback_data': "/*" + doc['word']}])
                    if len(current_keyboard) == 4:
                        break
            if len(current_keyboard) < 4:
                if (tmsg.pers_id, tmsg.chat_id) in self.waitlist:
                    self.waitlist.pop((tmsg.pers_id, tmsg.chat_id))
                print(self.tAPI.edit("Вы не перевели еще 4 слов на"
                                     + (" английском " if post['lang'] == "en" else " русском ")
                                     + "языке, поэтому выхожу из режима.", tmsg.chat_id, None, tmsg.id))
                return 0
            current_keyboard.insert(random.randint(0, len(current_keyboard)-1)
                                    , [{'text': post['word'], 'callback_data': "/*" + post['word']}])
            draft = "Выберите из предложенных слов слово, которому соответствует этот перевод:\n\""\
                    + self.tAPI.db.tr.find_one({"word": post['word']})["trl"] + "\""
            self.waitlist[(tmsg.pers_id, tmsg.chat_id)].append(current_keyboard)
            if tmsg.is_inline:
                self.waitlist[(tmsg.pers_id, tmsg.chat_id)].append(tmsg.id)
                print(self.tAPI.edit(draft, tmsg.chat_id, current_keyboard, tmsg.id))
            else:
                self.waitlist[(tmsg.pers_id, tmsg.chat_id)].append(
                    self.tAPI.send_inline_keyboard_with_id(draft, tmsg.chat_id, current_keyboard, tmsg.id))
        return 0

    def quit(self, pers_id, chat_id, additional_info = '', msg_id = 0):
        if (pers_id, chat_id) in self.waitlist:
            if msg_id == 0:
                msg_id = self.waitlist[(pers_id, chat_id)][5]
            self.waitlist.pop((pers_id, chat_id))
            self.tAPI.edit(additional_info + "Я вышел из режима \"4option cards\".", chat_id, self.MENU_KEYBOARD, msg_id)


class HangCard(BaseWorker):
    COMMAND = "/cards_hang"
    HELP = "Команда \"" + COMMAND + "\" включает игровой режим карточек, Вам нужно угадать некогда переведенное слово.\n\n"

    waitlist = dict()

    def is_it_for_me(self, tmsg):
        if ((tmsg.pers_id, tmsg.chat_id) in self.waitlist) and tmsg.is_inline:
            return True
        if tmsg.text.startswith(self.COMMAND):
            if not self.tAPI.DB_IS_ENABLED:
                print(self.tAPI.send("Этот режим сейчас недоступен!", tmsg.chat_id, tmsg.id))
            elif self.tAPI.NO_CARDS_GROUPS and tmsg.chat_id != tmsg.pers_id:
                print(self.tAPI.send("Использование режима в групповом чате отключено!", tmsg.chat_id, tmsg.id))
            elif self.tAPI.db[str(tmsg.pers_id)]['known_words'].count() == 0 and not self.tAPI.db_shell.TEST_WORDS:
                print(self.tAPI.send("Вы не переводили слов, поэтому не могу запустить этот режим.", tmsg.chat_id, tmsg.id))
            else:
                self.tAPI.send("Stop - остановить режим. \n Next - следующее слово.", tmsg.chat_id, tmsg.id)
                self.tAPI.db_shell.modify_activity(tmsg.pers_id, 5)
                return True
        return False

    def run(self, tmsg):
        if (tmsg.pers_id == tmsg.chat_id):
            self.tAPI.db_shell.modify_last_activity(tmsg.pers_id, False)
        collection = self.tAPI.db[str(tmsg.pers_id)]['known_words']
        if (tmsg.pers_id, tmsg.chat_id) in self.waitlist:
            self.waitlist[(tmsg.pers_id, tmsg.chat_id)][5] = tmsg.id
            if tmsg.text == "/Stop":
                self.quit(tmsg.pers_id, tmsg.chat_id, msg_id=tmsg.id)
                return 0
            else:
                if tmsg.text == "/Next":
                    self.tAPI.edit("Дальше, так дальше.", tmsg.chat_id, None, tmsg.id)
                else:
                    if self.existance_del(self.get_inline_request(tmsg), self.waitlist[(tmsg.pers_id, tmsg.chat_id)][3]):
                        index = self.waitlist[(tmsg.pers_id, tmsg.chat_id)][0].find(tmsg.text[1:].lower())
                        if index == -1:
                            self.waitlist[(tmsg.pers_id, tmsg.chat_id)][2] -= 1
                            self.tAPI.edit("Нет такой буквы. \n\n" + self.tAPI.db.tr.find_one({"word":
                                                        self.waitlist[(tmsg.pers_id, tmsg.chat_id)][4]}
                                                                  )["trl"] + '\n'
                                       + self.state_to_string(self.waitlist[(tmsg.pers_id, tmsg.chat_id)])
                                                    , tmsg.chat_id, self.waitlist[(tmsg.pers_id, tmsg.chat_id)][3]
                                                    , tmsg.id)
                            if self.waitlist[(tmsg.pers_id, tmsg.chat_id)][2] == 0:
                                self.tAPI.edit("Вы проиграли. :(\nОтвет: "\
                                               + self.waitlist[(tmsg.pers_id, tmsg.chat_id)][4]
                                               , tmsg.chat_id, None, tmsg.id)
                                # self.tAPI.send("Stop - остановить режим. \n Next - следующее слово.", tmsg.chat_id)
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
                            self.tAPI.edit("Есть такая буква. \n\n" + self.tAPI.db.tr.find_one({"word":
                                                        self.waitlist[(tmsg.pers_id, tmsg.chat_id)][4]}
                                                                  )["trl"] + '\n'
                                       + self.state_to_string(self.waitlist[(tmsg.pers_id, tmsg.chat_id)]),
                                           tmsg.chat_id, self.waitlist[(tmsg.pers_id, tmsg.chat_id)][3], tmsg.id)
                            if len(self.waitlist[(tmsg.pers_id, tmsg.chat_id)][0]) \
                                == self.waitlist[(tmsg.pers_id, tmsg.chat_id)][0].count("-"):
                                self.tAPI.edit("Вы выиграли!", tmsg.chat_id, None, tmsg.id)
                                # self.tAPI.send("Stop - остановить режим. \n Next - следующее слово.", tmsg.chat_id)
                            else:
                                return 0
                    else:
                        self.tAPI.edit("Некорректный ответ. Попробуйте еще раз. \n\n"
                                       + self.tAPI.db.tr.find_one({"word":
                                                        self.waitlist[(tmsg.pers_id, tmsg.chat_id)][4]}
                                                                  )["trl"] + '\n'
                                       + self.state_to_string(self.waitlist[(tmsg.pers_id, tmsg.chat_id)]),
                                   tmsg.chat_id, self.waitlist[(tmsg.pers_id, tmsg.chat_id)][3], tmsg.id)
                        return 0
        post = self.tAPI.get_random_doc(collection if collection.count() > 0 else self.tAPI.db['common'])
        if post == None:
            self.quit(tmsg.pers_id, tmsg.chat_id, "Мне не о чем вас спросить.", tmsg.id)
        else:
            state = [post['word'], "- " * len(post['word']), 6, self.default_keyboard(post['lang']), post['word']]
            state.append(self.tAPI.send_inline_keyboard_with_id(self.tAPI.db.tr.find_one({"word": post['word']})["trl"]
                                            + '\n' + self.state_to_string(state), tmsg.chat_id, state[3]))
            self.waitlist[(tmsg.pers_id, tmsg.chat_id)] = state
        return 0

    def quit(self, pers_id, chat_id, additional_info='', msg_id=0):
        if (pers_id, chat_id) in self.waitlist:
            if msg_id == 0:
                msg_id = self.waitlist[(pers_id, chat_id)][5]
            self.waitlist.pop((pers_id, chat_id))
            self.tAPI.edit(additional_info + "Я вышел из режима \"hang cards\".", chat_id, self.MENU_KEYBOARD, msg_id)

    def state_to_string(self, state):
        return state[1] + "\nВаше количество жизней: " + str(state[2]) + "."

    def get_reply_request(self, tmsg):
        return tmsg.text

    def get_inline_request(self, tmsg):
        return {'text': tmsg.text[1:], 'callback_data': tmsg.text}

    def existance_del(self, request, keyboard):
        for i in range(0, len(keyboard)-1):
            if request in keyboard[i]:
                keyboard[i].pop(keyboard[i].index(request))
                return True
        return False

    def default_keyboard(self, lang):
        if lang == "en":
            return self.tAPI.get_inline_text_keyboard(
                """a\tb\tc\td\te\tf\tg\th\ti\nj\tk\tl\tm\tn\to\tp\tq\tr\ns\tt\tu\tv\tw\tx\ty\tz\nNext\tStop""")
        elif lang == "ru":
            return self.tAPI.get_inline_text_keyboard(
                """а\tб\tв\tг\tд\tе\tж\tз\tи\tй\nк\tл\tм\tн\tо\tп\tр\tс\tт\tу\tф\nх\tц\tч\tш\tщ\tъ\tы\tь\tю\tя\nNext\tStop""")
            # return [["/а", "/б", "/в", "/г", "/д", "/е", "/ё", "/ж", "/з", "/и", "/й"],
            #         ["/к", "/л", "/м", "/н", "/о", "/п", "/р", "/с", "/т", "/у", "/ф"],
            #         ["/х", "/ц", "/ч", "/ш", "/щ", "/ъ", "/ы", "/ь", "/э", "/ю", "/я"], ["/Next", "/Stop"]]
        else:
            return self.tAPI.get_inline_text_keyboard("No keyboard for this language!\nNext\tStop")
