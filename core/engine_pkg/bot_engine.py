from core.apis_pkg.msg_module import Msg


class BotCycle:
    tapi = None
    workers_list = None

    def __init__(self, tapi, workers_list):
        self.tapi = tapi
        self.workers_list = workers_list

    def run(self):
        offset = 0
        is_running = True
        tmsg = None
        print("Guess who's back!")

        try:
            for msg in self.tapi.get_msg(offset):
                if not is_running:
                    break
                tmsg = Msg(msg)
                if tmsg.text != "":
                    if tmsg.text.startswith("//"):
                        continue
                    print(tmsg.text)
                    tmsg.textmod()
                    try:
                        # is_running = self.workers_list.run_list(tmsg)
                        for worker in self.workers_list:
                            if worker.is_it_for_me(tmsg):
                                cmd = worker.run(tmsg)
                                if cmd == 2:
                                    is_running = False
                                break
                    except UnicodeEncodeError:
                        print(self.tapi.send("I don't like your language!", tmsg.chat_id))
        except Exception as ex:
            print(type(ex), ex.__str__())

        self.tapi.get(offset)
