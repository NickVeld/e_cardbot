import sys
import datetime
from multiprocessing import Process
from core.engine.autoquit import autoquit_run
from core.engine.reminder import reminder_run


class WorkersList(type):
    workers = []

    def __new__(mcs, name, bases, attrs, **kwargs):
        worker_class = super(WorkersList, mcs).__new__(mcs, name, bases, attrs)
        if '__not_bot__' not in attrs:
            WorkersList.workers.append((name, worker_class))
        return worker_class

    def get_workers(cls, list, tapi):
        workers = []
        # available = cls.workers
        for worker in cls.workers:
            exist = False
            for str in list:
                if str == worker[0]:
                    exist = True
                    break
            if not exist:
                cls.workers.remove(worker)

        for str in list:
            try:
                workers.append(getattr(sys.modules[__name__], str)(tapi))
                print(str)
            except:
                print("There isn't " + str)
        return workers


class BaseWorker(object, metaclass=WorkersList):
    __not_bot__ = True

    HELP = ""

    def __init__(self, teleapi):
        self.tAPI = teleapi


class Autoquit(BaseWorker):
    old_time = datetime.datetime.utcnow()

    def is_it_for_me(self):
        return self.tAPI.DB_IS_ENABLED \
               and datetime.datetime.utcnow() - datetime.timedelta(minutes=self.tAPI.db_shell.INACT_M) >= self.old_time

    def run(self):
        print('inactive')
        self.old_time = datetime.datetime.utcnow()
        # autoquit = Process(target=autoquit_run, args=(self.tAPI,))
        # autoquit.start()
        autoquit_run(self.tAPI)
        # reminder_run(self.tAPI)
        return 1