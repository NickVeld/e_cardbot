def autoquit_run(tapi):
    for user in tapi.db_shell.get_ready_for_autoquit():
        for worker in tapi.workers_list:
            worker.quit(user['pers_id'], user['pers_id'], "Вы были неактивны долгое время.")
        tapi.db_shell.modify_last_activity(user, True)