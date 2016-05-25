from configobj import ConfigObj

import core.workers.workers as lworkers
from core.apis import bot_api
from core.engine import bot_engine

data = dict()

cfg = ConfigObj("config.cfg")
tapi = bot_api.API()
tapi.get_from_config(cfg)

try:
    f = open("storage.yml", 'r')
    offset = int(f.readline())
    f.close()
except FileNotFoundError:
    print("There're no storages.")
    offset = 163111506
except ValueError:
    offset = 163111506
except Exception as ex:
    print(type(ex), ex.__str__())
    offset = 163111506

tapi.offset = offset
bs = bot_engine.BotCycle(tapi, lworkers.WorkersList.get_workers(lworkers.WorkersList, cfg["included_workers"], tapi))
bs.run()

try:
    f = open("storage.yml", 'w')
    f.write(str(bs.tapi.offset) + '\n')
    f.close()
except Exception as ex:
    print(type(ex), ex.__str__())