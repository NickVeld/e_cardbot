from core.services.msg_module import Msg


class BotCycle:

    def __init__(self, tapi, workers_list):
        self.tapi = tapi
        self.workers_list = workers_list

    def run(self):
        is_running = True
        tmsg = None
        print("Guess who's back!")

        try:
            for msg in self.tapi.get_msg():
                tmsg = Msg(msg, self.tapi.BOT_NICK)
                if (tmsg.msg == None) or tmsg.text.startswith("//"):
                    continue
                if tmsg.text != "":
                    print(tmsg.text)
                    tmsg.textmod()
                    try:
                        # is_running = self.workers_list.run_list(tmsg)
                        for worker in self.workers_list:
                            if worker.is_it_for_me(tmsg):
                                cmd = worker.run(tmsg)
                                if cmd == 2:
                                    is_running = False
                                if cmd != 1:
                                    break
                    except UnicodeEncodeError:
                        print(self.tapi.send("Мне не нравится Ваш язык!", tmsg.chat_id))
                if not is_running:
                    break
        except Exception as ex:
            print(type(ex), ex.__str__())

        # self.tapi.get(offset, timeout=1)
