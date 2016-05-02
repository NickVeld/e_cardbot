from configobj import ConfigObj

import core.workers_pkg.workers as lworkers
from core.apis_pkg import bot_api
from core.engine_pkg import bot_engine

data = dict()

cfg = ConfigObj("config.cfg")
tapi = bot_api.API()
tapi.get_from_config(cfg)

bs = bot_engine.BotCycle(tapi, lworkers.WorkersList.get_workers(lworkers.WorkersList, cfg["included_workers"], tapi))
bs.run()
