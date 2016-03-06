import time

from resources import bot_api
from resources.workers import *

offset = 163113241

tapi = bot_api.api()
workers = (blacklist(), stop(), tr(), ph(), help())

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