
import pytest
import testing_utils
from rafcon.statemachine.global_variable_manager import GlobalVariableManager
from rafcon.utils import type_helpers
from pytest import raises


def test_type_check(caplog):
    # valid
    gvm = GlobalVariableManager()
    gvm.set_variable("a", 1, data_type=int)
    a = gvm.get_variable("a")
    assert a == 1

    gvm.set_variable("b", "test", data_type=str)
    b = gvm.get_variable("b")
    assert b == "test"

    gvm.set_variable("c", 12.0, data_type=float)
    c = gvm.get_variable("c")
    assert c == 12.0

    gvm.set_variable("d", 'True', data_type=bool)
    d = gvm.get_variable("d")
    assert d

    e_list = [1, 2, 3]
    gvm.set_variable("e", str(e_list), data_type=list)
    e = gvm.get_variable("e")
    assert e == str(e_list)

    # invalid
    with raises(AttributeError):
        gvm.set_variable("f", "test", data_type=int)
    testing_utils.assert_logger_warnings_and_errors(caplog)

    with raises(AttributeError):
        gvm.set_variable("g", "test", data_type=float)
    testing_utils.assert_logger_warnings_and_errors(caplog)

    # overwriting
    gvm.set_variable("a", 3, data_type=int)
    a = gvm.get_variable("a")
    assert a == 3

    # invalid overwriting
    with raises(AttributeError):
        gvm.set_variable("a", "string", data_type=int)
    a = gvm.get_variable("a")
    assert a == 3

    # backward compatibility
    gvm.set_variable("a", "test")
    a = gvm.get_variable("a")
    assert a == "test"

    gvm.set_variable("a", 123)
    a = gvm.get_variable("a")
    assert a == 123


if __name__ == '__main__':
    pytest.main([__file__])
    # test_type_check()