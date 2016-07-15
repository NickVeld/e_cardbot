def autoquit_run(tapi):
    for user in tapi.db_shell.get_ready_for_autoquit():
        for worker in tapi.workers_list:
            print(type(worker).__name__ + ' finded')
            worker.quit(user['pers_id'], user['pers_id'], "Вы были неактивны долгое время.")
            print(type(worker).__name__ + ' checked')
        tapi.db_shell.modify_last_activity(user, True)