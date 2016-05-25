from configobj import ConfigObj

isExample = True
config = ConfigObj()
config.filename = "config_example.cfg"
config['APIs'] = {
    'bot_nick': "@coolbot",
    'telegram_chatlink': 'https://api.telegram.org/bot',
    'dictionary_link': 'https://dictionary.yandex.net/api/v1/dicservice.json/lookup?',
    'translator_link': 'https://translate.yandex.net/api/v1.5/tr.json/translate?',
    'telegram_api': "000000000:api_key",
    'dictionary_api': "dict.1.1.dict.key",
    'translator_api': "trnsl.1.1.tr.key"
}
config['mongo_settings'] = {
    'isEnabled': False,
    'name': "mongo",
    'port': "27017",
    'db_name': "e_card"
}
config['admins_ids'] = [
    "admin_id0",
    "admin_id1"
]
config['included_workers'] = [
    "Blacklist",
    "Stop",
    "Translator",
    "PhraseTranslator",
    "Info",
    "SimpleCard",
    "TranslationCard",
    "OptionCard",
    "HangCard"
]
config["cards_is_allowed_for_groups"] = True
config["card_cooldown_at_minutes"] = 1
config.initial_comment = ["Change values which you want, rename file to \"config.cfg\" and delete this string!"]
config.final_comment = ["Warning: Allowing cards for groups cause an undefined behavior "
                        "because of inline keyboards disallowed at groups."]
config.write()