import datetime
import random
from bson.code import Code
from pymongo import MongoClient

__author__ = 'NickVeld'


class DBShell:
    def __init__(self):
        self.db = None
        self.COOLDOWN_M = 1
        # self.NUM_DECKS = 5
        self.TEST_WORDS = False


    def get_from_config(self, cfg):
        self.db = (MongoClient(cfg['mongo_settings']['name'], int(cfg['mongo_settings']['port']))
                   [cfg['mongo_settings']['db_name']] if cfg['mongo_settings']['isEnabled'] == 'True' else None)
        self.COOLDOWN_M = int(cfg["card_cooldown_at_minutes"])
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

    def get_doc_for_card(self, tmsg, collection, additional_condition=(lambda x: True)):
        cursor = collection.find({}).where(Code("function() {"
            "var d = new Date(); "
            "d.setMinutes(d.getMinutes()-" + str(self.COOLDOWN_M) + "*Math.pow(2, this.deck)); "
            "return d.getTime() - this.lastRevised.getTime() > 0;"
            "}")
            ).skip(random.randint(0, collection.count() - 1)).limit(1)[0]
        if cursor.count() > 0:
            post = cursor[0]
        else:
            post = None
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