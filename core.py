import time

from resources import bot_api
from resources.workers import *

offset = 163113241

cfg = open("config.cfg", 'r')
data = dict()
data["api_key"] = cfg.readline().strip()
data["dict_key"] = cfg.readline().strip()
data["tr_key"] = cfg.readline().strip()
data["admin_ids"] = {}
cfg.close()
tapi = bot_api.api(data)
workers = (blacklist(data), stop(data), tr(data), ph(data), help(data))

isRunning = True
print("Guess who's back!")
word_wait = 0
phrase_wait = 0

try:
    while isRunning:
        time.sleep(1)
        # try:
        newMsgs = tapi.get(offset)
        # except:
        #    print("Exception!")
        #    continue
        if newMsgs == "":
            continue

        if newMsgs['ok'] and (len(newMsgs['result']) != 0):
            for msg in newMsgs['result']:
                if(not isRunning):
                    break
                offset = msgc.upd_id(newMsgs['result'][len(newMsgs['result']) - 1])
                print(offset)
                if 'text' in msg['message']:
                    if msgc.text(msg).startswith("//"):
                        continue
                    msgc.textmod(msg)
                    print(msgc.text(msg))
                    try:
                        for worker in workers:
                            if(worker.is_it_for_me(msg)):
                                cmd = worker.run(msg)
                                if(cmd == 2):
                                    isRunning = False
                                break

                    except UnicodeEncodeError:
                        print(tapi.send("I don't like your language!",
                                        msgc.chat_id(msg)))
except Exception as ex:
    print(type(ex), ex.__str__())

tapi.get(offset)