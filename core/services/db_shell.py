import datetime
import random
from bson.code import Code
from pymongo import MongoClient

__author__ = 'NickVeld'


class DBShell:
    def __init__(self):
        self.db = None
        self.INACT_M = 5
        self.COOLDOWN_M = 1
        # self.NUM_DECKS = 5
        self.TEST_WORDS = False


    def get_from_config(self, cfg):
        self.db = (MongoClient(cfg['mongo_settings']['name'], int(cfg['mongo_settings']['port']))
                   [cfg['mongo_settings']['db_name']] if cfg['mongo_settings']['isEnabled'] == 'True' else None)
        self.INACT_M = int(cfg["user_inactivity_time_at_minutes"])
        self.COOLDOWN_M = int(cfg["card_delay_at_minutes"])
        # self.NUM_DECKS = int(cfg["number_of_decks"]) - 1
        self.TEST_WORDS = cfg.get('test_words', 'False') == 'True'


    def get_random_doc(self, collection, request=None):
        return collection.find().skip(random.randint(0, collection.count() - 1)).limit(1)[0] \
            if request == None else \
            collection.find(request).skip(random.randint(0, collection.count() - 1)).limit(1)[0]
        # return collection.find_one() if request==None else collection.find_one(request)

    def get_test_word(self, pers_id):
        return self.db['common'].find_one(
            {"$or": [
                {str(pers_id):
                     {"$exists": False}
                 },
                {str(pers_id):
                     {"$lt": datetime.datetime.utcnow() - datetime.timedelta(minutes=self.COOLDOWN_M)}
                 }
            ]})

    def sum_weight(self, decks, rule):
        sum = 0
        for i, deck in enumerate(decks):
            sum += deck * rule(i)
        return sum

    def get_doc_for_card(self, tmsg, collection, additional_condition=(lambda x: True)):
        post = None
        sorted_cards = list(collection.find().where(Code("function() {"
            "var d = new Date(); "
            "d.setMinutes(d.getMinutes()-" + str(self.COOLDOWN_M) + "*Math.pow(2, this.deck)); "
            "return (d.getTime() - this.lastRevised.getTime() > 0);"
            "}")
            ).sort([('deck', 1)]))
        if len(sorted_cards) > 0:
            max_deck = sorted_cards[len(sorted_cards) - 1]['deck']
            min_deck = sorted_cards[0]['deck']
            curr_decks = [0 for i in range(max_deck + 1 - min_deck)]
            for card in sorted_cards:
                curr_decks[card['deck']-min_deck] = curr_decks[card['deck']-min_deck] + 1
            rule = lambda x: 2**(len(curr_decks) - 1 - x)
            rand_num = random.randint(1, self.sum_weight(curr_decks, rule))
            for i, el in enumerate(sorted_cards):
                rand_num -= rule(el['deck'] - min_deck)
                if rand_num <= 0:
                    post = el
                    break
            if post == None:
                print('Beda')
                post = sorted_cards[len(sorted_cards)-1]
        if post == None or not additional_condition(post["lang"]):
            if self.TEST_WORDS:
                post = self.get_test_word(tmsg.pers_id)
                return [post, None if post == None else [post["_id"], False]]
        else:
            return [post, [post["_id"], True]]

    def update_doc_for_card(self, is_not_test_word, pers_id, doc_id, correctness):
        if (is_not_test_word):
            if (correctness):
                # delc = self.db[str(pers_id)]['known_words'].delete_one(
                #     {'$and':{{"_id": doc_id }, {'deck': {'$gt': self.NUM_DECKS}}}}).deleted_count
                # if (delc):
                #     return True
                info = { "$inc": { "deck": 1 }, "$set": {} }
            else:
                info = { "$set": { "deck": 0 } }
            info["$set"]["lastRevised"] = datetime.datetime.utcnow()

            self.db[str(pers_id)]['known_words'].update_one(
                {"_id": doc_id}, info)
        else:
            self.db['common'].update_one(
                {"_id": doc_id},
                {
                    "$set": {
                        str(pers_id): datetime.datetime.utcnow()
                    }
                })
        # return False

    def insert_doc_for_card(self, tmsg, collection, tr_request, lang, tr_response):
        collection.insert_one({"word": tr_request, "trl": tr_response})
        self.db[str(tmsg.pers_id)]['known_words'].insert_one(
            {
                "word": tr_request,
                "lang": lang,
                "lastRevised": datetime.datetime.utcnow(),
                "deck": 1
            }
        )

    def initialize_user(self, pers_id):
        if self.db[str(pers_id)]['activity'].count() == 0:
            self.db['users'].insert_one({'pers_id': str(pers_id), 'last': datetime.datetime.min})
            for i in range(7):
                doc = {str(p) : 0 for p in range(24)}
                doc['weekday'] = str(i)
                doc['reminder_time'] = -1
                self.db[str(pers_id)]['activity'].insert_one(doc)


    def modify_activity(self, pers_id, amount):
        h = datetime.datetime.utcnow().hour
        for i in range(0, 3):
            p = int(h) - i + (24 if int(h) < i else 0)
            self.db[str(pers_id)]['activity'].update_many(
                {'weekday': str(datetime.datetime.utcnow().weekday())}, {'$inc':{str(p): amount}})

    def modify_last_activity(self, pers_id, after_quit):
        if after_quit:
            info = {'$set':{'last': datetime.datetime.min}}
        else:
            info = {'$set': {'last': datetime.datetime.utcnow()}}
        self.db['users'].update_many({'pers_id': str(pers_id)}, info)

    def calculate_reminder_time_for(self, pers_id, weekday):
        today_stat = self.db[str(pers_id)]['activity'].find_one({'weekday': str(weekday)})
        index_of_max = '0'
        for i in range(24):
            if today_stat[str(i)] >= today_stat[index_of_max]:
                index_of_max = str(i)
        self.db[str(pers_id)]['activity'].update_one({'_id': today_stat['_id']}
                                    , {'$set':{'reminder_time': -1 if today_stat[index_of_max] == 0 else index_of_max}})

    def calculate_reminder_time(self, pers_id):
        today = datetime.datetime.utcnow().weekday()
        self.calculate_reminder_time_for(pers_id, 6 if today == 0 else today - 1)
        self.calculate_reminder_time_for(pers_id, today)

    def get_ready_for_autoquit(self):
        return self.db['users'].find(
            {'last':
                 {'$ne': datetime.datetime.min
                     , '$lte': datetime.datetime.utcnow() - datetime.timedelta(minutes=(self.INACT_M-1))}
             })
