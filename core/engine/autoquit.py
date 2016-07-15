def autoquit_run(tapi):
    for user in tapi.db_shell.get_ready_for_autoquit():
        pers_id = int(user['pers_id'])
        for worker in tapi.workers_list:
            worker.quit(pers_id, pers_id, "Вы были неактивны долгое время.\n")
        tapi.db_shell.modify_last_activity(pers_id, True)
        tapi.db_shell.calculate_reminder_time(pers_id)