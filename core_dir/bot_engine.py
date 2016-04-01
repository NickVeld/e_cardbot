from core_dir.msg_module import Msg


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
            while is_running:
                # try:
                new_msgs = self.tapi.get(offset)
                # except:
                #    print("Exception!")
                #    continue
                if new_msgs is None:
                    continue

                for msg in new_msgs['result']:
                    if not is_running:
                        break
                    tmsg = Msg(msg)
                    offset = tmsg.upd_id
                    print(offset)
                    if 'text' in msg['message']:
                        if tmsg.text.startswith("//"):
                            continue
                        print(tmsg.text)
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
