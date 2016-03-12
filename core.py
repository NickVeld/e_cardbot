from scripts import bot_api
import scripts.workers as lworkers
from scripts import bot_engine

cfg = open("config.cfg", 'r')
data = dict()
data["api_key"] = cfg.readline().strip()
data["dict_key"] = cfg.readline().strip()
data["tr_key"] = cfg.readline().strip()
db_is_enabled = cfg.readline().strip()[0] == 'E'
data["admin_ids"] = cfg.readline().strip().split(',')
cfg.close()
tapi = bot_api.API(data)
workers = (lworkers.Blacklist(data, db_is_enabled), lworkers.Stop(data), lworkers.Translator(data, db_is_enabled),
           lworkers.PhraseTranslator(data), lworkers.Info(data))
bs = bot_engine.BotCycle(tapi, workers)
bs.run()
