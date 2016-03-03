#!/usr/bin/env python

import pytest
import signal

import rafcon
from rafcon.statemachine import interface
import testing_utils

from rafcon.utils import log
logger = log.get_logger("start-no-gui")
logger.info("initialize RAFCON ... ")
from rafcon.utils.constants import RAFCON_TEMP_PATH_STORAGE

import rafcon.statemachine.singleton as sm_singletons
# needed for yaml parsing
from rafcon.statemachine.states.hierarchy_state import HierarchyState
from rafcon.statemachine.states.execution_state import ExecutionState
from rafcon.statemachine.states.preemptive_concurrency_state import PreemptiveConcurrencyState
from rafcon.statemachine.states.barrier_concurrency_state import BarrierConcurrencyState
from rafcon.statemachine.execution.statemachine_execution_engine import StatemachineExecutionEngine
from rafcon.statemachine.enums import StateExecutionState


request_counter = 0


def show_notice(query):
    return ""  # just take note of the missing library


def open_folder(query):
    global request_counter

    return_value = ""

    if request_counter == 0:
        return_value = None  # the first relocation has to be aborted
    else:
        return_value = "/home_local/brun_sb/develop/rafcon/source/test_scripts/test_libraries/library1_for_relocation_test_relocated"

    request_counter += 1
    return return_value


def test_library_relocation(caplog):

    signal.signal(signal.SIGINT, sm_singletons.signal_handler)
    testing_utils.test_multithrading_lock.acquire()

    interface.open_folder_func = open_folder

    interface.show_notice_func = show_notice

    rafcon.statemachine.singleton.state_machine_manager.delete_all_state_machines()

    # Initialize libraries
    sm_singletons.library_manager.initialize()

    # Set base path of global storage
    sm_singletons.global_storage.base_path = RAFCON_TEMP_PATH_STORAGE

    [state_machine, version, creation_time] = rafcon.statemachine.singleton.global_storage.load_statemachine_from_path(
        "/home_local/brun_sb/develop/rafcon/source/test_scripts/unit_test_state_machines/library_relocation_test")

    rafcon.statemachine.singleton.state_machine_manager.add_state_machine(state_machine)

    rafcon.statemachine.singleton.state_machine_execution_engine.start()
    rafcon.statemachine.singleton.state_machine_execution_engine.join()
    rafcon.statemachine.singleton.state_machine_execution_engine.stop()

    assert state_machine.root_state.output_data["output_0"] == 27

    testing_utils.assert_logger_warnings_and_errors(caplog, 0, 1)
    testing_utils.test_multithrading_lock.release()

    logger.info("State machine execution finished!")


if __name__ == '__main__':
    # test_library_relocation(None)
    pytest.main([__file__])