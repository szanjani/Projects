"""
This file contains the ActionManager class.
"""

import copy
import logging
import threading
import json
import jsonschema
import constants


class ActionManager:
    """
    This class maintains lists of actions (jump and run) along with an average time for each
    action.
    """

    def __init__(self):
        # private lock object used as a mutex for safe concurrent access of jump data.
        self.__lock_jumps = threading.Lock()

        # private lock object used as a mutex for safe concurrent access of run data.
        self.__lock_runs = threading.Lock()

        # private lock object used as a mutex for safe concurrent access of failed objects data.
        self.__lock_failed_objects = threading.Lock()

        # private list that holds all jumps and should be wrapped in self.__lock_jumps when
        # accessed.
        self.__jumps = list()

        # private list that holds all runs and should be wrapped in self.__lock_runs when accessed.
        self.__runs = list()

        # private list that holds all failed objects and should be wrapped in
        #  self.__lock_failed_objects when accessed.
        self.__failed_objects = list()

        # private dictionary that holds all jump averages and should be wrapped in
        #  self.__lock_jumps when accessed.
        self.__jump_average = {constants.ActionManager.KEY_ACTION : constants.ActionManager.
                                                                    VALUE_JUMP,
                               constants.ActionManager.KEY_AVERAGE : 0}

        # private dictionary that holds all run averages and should be wrapped in
        #  self.__lock_runs when accessed.
        self.__run_average = {constants.ActionManager.KEY_ACTION : constants.ActionManager.
                                                                   VALUE_RUN,
                              constants.ActionManager.KEY_AVERAGE : 0}

    def addAction(self, action:str):
        """
        This function accepts a json serialized string of the form {"action":"jump", "time":100},
        validates it as a correct json string, then appends it to either the jump or run list in
        a thread safe manner along with updating the average time data.  In case of a failure
        the object is appended to the failed list.

        Args:
            action (str): Valid actions in the json are "jump" and "run"
        """

        result, json_object = self.__validate_JSON(action)
        if result:
            logging.debug('Valid JSON string')


            if json_object[constants.ActionManager.KEY_ACTION] == constants.ActionManager.\
                                                                  VALUE_JUMP:
                with self.__lock_jumps:
                    logging.debug('LOCKED JUMPS')
                    self.__jumps.append(json_object)
                    jump_total_time = 0
                    for jump in self.__jumps:
                        jump_total_time += jump[constants.ActionManager.KEY_TIME]
                    self.__jump_average[constants.ActionManager.KEY_AVERAGE] = (jump_total_time /
                                                                               (len(self.__jumps)))
                    logging.debug('UNLOCKED JUMPS')

            elif json_object[constants.ActionManager.KEY_ACTION] == constants.ActionManager.\
                                                                    VALUE_RUN:
                with self.__lock_runs:
                    logging.debug('LOCKED RUNS')
                    self.__runs.append(json_object)
                    run_total_time = 0
                    for run in self.__runs:
                        run_total_time += run[constants.ActionManager.KEY_TIME]
                    self.__run_average[constants.ActionManager.KEY_AVERAGE] = (run_total_time /
                                                                               (len(self.__runs)))
                    logging.debug('UNLOCKED RUNS')
        else:
            logging.error('Failed to add {}'.format(action))

            with self.__lock_failed_objects:
                logging.debug('LOCKED FAILED OBJECTS')
                self.__failed_objects.append(action)
                logging.debug('UNLOCKED FAILED OBJECTS')

    def __validate_JSON(self, json_string:str):
        """
        This private function accepts a json serialized string and validates that the first key is
        "action", the first value is either "jump" or "run", the second key is "time", and
        the second value is an integer greater than 0.

        Args:
            json_string (str): json to be validated.

        Returns:
            result (bool), json_object: True, json_object if valid and False, None otherwise.
        """

        try:
            json_object = json.loads(json_string)
        except ValueError as error:
            logging.debug('Invalid JSON string: {}'.format(error))
            return False, None

        schema = {
            "type": "object",
            "properties": {
                constants.ActionManager.KEY_ACTION: {"enum": [constants.ActionManager.VALUE_JUMP,
                                                              constants.ActionManager.VALUE_RUN]},
                constants.ActionManager.KEY_TIME: {"type": "number", "minimum": 0}
            },
            "required": [constants.ActionManager.KEY_ACTION, constants.ActionManager.KEY_TIME]
        }

        try:
            jsonschema.validate(json_object, schema)
        except jsonschema.exceptions.ValidationError as error:
            error = str(error).split('\n')
            logging.debug('Invalid JSON schema: {}'.format(error[0]))
            return False, None

        return True, json_object

    def getStats(self):
        """
        This function returns a serialized json array of the average time for each action in the
        following form: [ {"action":"jump", "avg":150}, {"action":"run", "avg":75} ]

        Args:
            none

        Returns:
            string: serialized json array of the average time for each action.
        """

        statistics = []

        with self.__lock_jumps:
            logging.debug('LOCKED JUMPS')
            logging.debug('Jumps: {}'.format(self.__jumps))
            logging.debug('Jumps Average: {}'.format(self.__jump_average))
            statistics.append(copy.deepcopy(self.__jump_average))
            logging.debug('UNLOCKED JUMPS')

        with self.__lock_runs:
            logging.debug('LOCKED RUNS')
            logging.debug('Runs: {}'.format(self.__runs))
            logging.debug('Runs Average: {}'.format(self.__run_average))
            statistics.append(copy.deepcopy(self.__run_average))
            logging.debug('UNLOCKED RUNS')

        return json.dumps(statistics)

    def getFailedObjects(self):
        """
        This function returns a list of objects that failed to be added to a
        list.

        Args:
            none

        Returns:
            list: contains objects that failed to be added to a list.
        """

        failed_objects = None

        with self.__lock_failed_objects:
            logging.debug('LOCKED FAILED OBJECTS')
            failed_objects = copy.deepcopy(self.__failed_objects)
            logging.debug('UNLOCKED FAILED OBJECTS')

        return failed_objects
