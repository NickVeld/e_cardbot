from core_dir import bot_api
import core_dir.workers as lworkers
from core_dir import bot_engine
from configobj import ConfigObj


data = dict()
# cfg = open("config.cfg", 'r')
# data["api_key"] = cfg.readline().strip()
# data["dict_key"] = cfg.readline().strip()
# data["tr_key"] = cfg.readline().strip()
# data["db_is_enabled"] = cfg.readline().strip()[0] == 'E'
# data["mongo_name"] = cfg.readline().strip()
# data["mongo_port"] = int(cfg.readline().strip())
# data["db_name"] = cfg.readline().strip()
# data["admin_ids"] = cfg.readline().strip().split(',')
# cfg.close()

cfg = ConfigObj("config.cfg")
data["api_key"] = cfg['APIs']['telegram_api']
data["dict_key"] = cfg['APIs']['dictionary_api']
data["tr_key"] = cfg['APIs']['translator_api']
data["db_is_enabled"] = cfg['mongo_settings']['isEnabled'] == 'True'
data["mongo_name"] = cfg['mongo_settings']['name']
data["mongo_port"] = int(cfg['mongo_settings']['port'])
data["db_name"] = cfg['mongo_settings']['db_name']
data["admin_ids"] = cfg['admins_ids']

tapi = bot_api.API(data)
workers = (lworkers.Blacklist(data), lworkers.Stop(data), lworkers.Translator(data),
           lworkers.PhraseTranslator(data), lworkers.Info(data), lworkers.SimpleCard(data))
bs = bot_engine.BotCycle(tapi, workers)
bs.run()
