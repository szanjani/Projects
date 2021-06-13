"""
This file tests the ActionManager class.
"""

import logging
import json
import threading
import action_manager


if __name__ == '__main__':

    # The below code tests validation of json strings. Various broken json strings
    # are fed to the addAction function and must be rejected.

    logging.basicConfig(format='%(asctime)s.%(msecs)03d: %(message)s', level=logging.DEBUG,
                        datefmt='%H:%M:%S')

    action_manager_1 = action_manager.ActionManager()

    JSON_STRING = '"action":"run", "time":5}'
    action_manager_1.addAction(JSON_STRING)

    JSON_STRING = '{action":"run", "time":5}'
    action_manager_1.addAction(JSON_STRING)

    JSON_STRING = '{"action:"run", "time":5}'
    action_manager_1.addAction(JSON_STRING)

    JSON_STRING = '{"action""run", "time":5}'
    action_manager_1.addAction(JSON_STRING)

    JSON_STRING = '{"action":run", "time":5}'
    action_manager_1.addAction(JSON_STRING)

    JSON_STRING = '{"action":"run, "time":5}'
    action_manager_1.addAction(JSON_STRING)

    JSON_STRING = '{"action":"run" "time":5}'
    action_manager_1.addAction(JSON_STRING)

    JSON_STRING = '{"action":"run", time":5}'
    action_manager_1.addAction(JSON_STRING)

    JSON_STRING = '{"action":"run", 1:5}'
    action_manager_1.addAction(JSON_STRING)

    JSON_STRING = '{"action":"run", "time"5}'
    action_manager_1.addAction(JSON_STRING)

    JSON_STRING = '{"action":"run", "time":}'
    action_manager_1.addAction(JSON_STRING)

    JSON_STRING = '{"key":"run", "time":1}'
    action_manager_1.addAction(JSON_STRING)

    JSON_STRING = '{"action":1, "time":1}'
    action_manager_1.addAction(JSON_STRING)

    JSON_STRING = '{"action":"swim", "time":1}'
    action_manager_1.addAction(JSON_STRING)

    JSON_STRING = '{"action":"jump", "value":1}'
    action_manager_1.addAction(JSON_STRING)

    JSON_STRING = '{"action":"jump", "time":"1"}'
    action_manager_1.addAction(JSON_STRING)

    JSON_STRING = '{"action":"jump", "time":-8}'
    action_manager_1.addAction(JSON_STRING)

    JSON_STRING = '{"action":"jump", "time":100}'
    action_manager_1.addAction(JSON_STRING)

    logging.debug('Failed objects: {}'.format(action_manager_1.getFailedObjects()))


    # The below code tests concurrent access of critical data by multiple threads using the
    # addAction and getStats functions.  With DEBUG logging level on, there should never be
    # consecutive "LOCKED" or "UNLOCKED" of the same type.  For example, after a "LOCKED RUNS"
    # there should NOT be another "LOCKED RUNS".

    NUM_THREADS = 10
    threads = [0] * NUM_THREADS

    time = 0
    for i in range(0, NUM_THREADS):
        if i % 2:
            action = 'jump'
        else:
            action = 'run'
        time += 1
        json_string = json.dumps({'action': action, 'time': time})
        threads[i] = threading.Thread(target=action_manager_1.addAction, args=(json_string,))

    for i in range(0, NUM_THREADS):
        threads[i].start()

    logging.debug('Statistics: {}'.format(action_manager_1.getStats()))

    for i in range(0, NUM_THREADS):
        threads[i].join()

    logging.debug('Threads have terminated.')
