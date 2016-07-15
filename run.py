from configobj import ConfigObj

from core.workers.workers import WorkersList
from core.apis.bot_api import API
from core.engine.bot_engine import BotCycle

data = dict()

cfg = ConfigObj("config.cfg")

tapi = API()
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
workers_list = WorkersList.get_workers(WorkersList, cfg["included_workers"], tapi)
tapi.workers_list = workers_list
bs = BotCycle(tapi, workers_list)
bs.run()

try:
    f = open("storage.yml", 'w')
    f.write(str(bs.tapi.offset) + '\n')
    f.close()
except Exception as ex:
    print(type(ex), ex.__str__())