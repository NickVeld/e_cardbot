import datetime

from ..workers.workers import WorkersList

def now_is_belong_to(period):
    tt = datetime.datetime.utcnow().hour - period
    return (tt >= 0 and tt < 4) or (tt < -20)


def get_inline_text_keyboard():
    keyboard = []
    for worker, worker_class in WorkersList.workers:
        if worker.endswith('Card') and not worker == 'HangCard':
            keyboard.append([{'text': worker.replace("Card", " card"), 'callback_data': worker_class.COMMAND}])
    return keyboard

def reminder_run(tapi):
    for user_activity in tapi.db.collection_names():
        if user_activity.endswith('activity'):
            if now_is_belong_to(int(tapi.db[user_activity].find_one(
                    {'weekday': str(datetime.datetime.utcnow().weekday())})['reminder_time'])):
                tapi.send_inline_keyboard("Как насчет того, чтобы поучить карточки?"
                                          , int(user_activity.replace('.activity', '', 1)), get_inline_text_keyboard())
