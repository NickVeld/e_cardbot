import sys

from configobj import ConfigObj

import core.workers_pkg.workers as lworkers
from core.apis_pkg import bot_api
from core.engine_pkg import bot_engine

data = dict()

cfg = ConfigObj("config.cfg")
data["api_key"] = cfg['APIs']['telegram_api']
data["dict_key"] = cfg['APIs']['dictionary_api']
data["tr_key"] = cfg['APIs']['translator_api']
data["db_is_enabled"] = cfg['mongo_settings']['isEnabled'] == 'True'
data["mongo_name"] = cfg['mongo_settings']['name']
data["mongo_port"] = int(cfg['mongo_settings']['port'])
data["db_name"] = cfg['mongo_settings']['db_name']
data["admin_ids"] = cfg['admins_ids']
data["cards_groups"] = cfg["cards_is_allowed_for_groups"]
data["cooldown_m"] = cfg["card_cooldown_at_minutes"]

tapi = bot_api.API(data)

workers = []
available = lworkers.WorkersList.workers
for worker in available:
    exist = False
    for str in cfg['included_workers']:
        if str == worker[0]:
            exist = True
            break
    if not exist:
        available.remove(worker)

for str in cfg['included_workers']:
    try:
        workers.append(getattr(sys.modules[lworkers.__name__], str)(tapi))
        print(str)
    except:
        print("There isn't " + str)
bs = bot_engine.BotCycle(tapi, workers)
bs.run()
