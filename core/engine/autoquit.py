from core.workers.workers import WorkersList

def autoquit_run(tapi):
    for user in tapi.db_shell.get_ready_for_autoquit():
        for worker in WorkersList.workers:
            worker.quit(['user.pers_id'], user['pers_id'], "Вы были неактивны долгое время.")
            tapi.db_shell.modify_last_activity(user, True)