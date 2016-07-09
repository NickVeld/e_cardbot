import sys
import datetime

from ..workers.workers import WorkersList

def now_is_belong_to(period):
    tt = datetime.datetime.utcnow().hour - period
    return (tt >= 0 and tt < 4) or (tt < -20)


def get_inline_text_keyboard():
    keyboard = []
    for worker in WorkersList.workers:
        if worker.endswith('Card'):
            keyboard.append([{'text': worker.replace("Card", " card")
                                 , 'callback_data': getattr(sys.modules[__name__], str).COMMAND}])
    return keyboard

def reminder_run(tapi, worker):
    for user in tapi.db.collection_names:
        if now_is_belong_to(tapi.db[user]['activity'][datetime.datetime.utcnow().weekday]['reminder_time']):
            tapi.send_inline_keyboard("Как насчет того, чтобы поучить карточки?", int(user), get_inline_text_keyboard())
