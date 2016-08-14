import threading
import socket
import json
from unittest import mock
import pytest

from .. import jsonapi
from .. import robot
from .. import config


def start_server_thread():
    """
    Start the jsonapi server in another thread
    """
    jsonapi.TEST_QUEUE = True
    thr = threading.Thread(target=jsonapi.run)
    thr.start()
    assert jsonapi.test_queue.get() == 'Server Running'


def connect_server() -> socket.socket:
    """
    Connect to the jsonapi server

    Returns:
    A socket.socket connected to the server
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(config.JSONAPI_BIND_ADDR)
    return sock


def test_require():
    test = {
        'a': 'b',
        'c': 'd'
    }
    jsonapi.require(('a'), test)
    with pytest.raises(ValueError):
        jsonapi.require(('z',), test)


def test_process():
    testdata = {
        'method': 'test_method',
        'data': 1234
    }

    # test absent method
    with pytest.raises(ValueError):
        jsonapi.process_request(testdata)

    test_mock = mock.MagicMock()
    jsonapi.METHODS.update({'test_method': test_mock})
    jsonapi.process_request(testdata)
    test_mock.assert_called_with(1234)


def test_call():
    """
    Test the 'call' method in an incoming jsonapi data structure
    """
    testdata = {
        'call': 'test_func',
        'args': {'test': 42}
    }

    robot.robot.test_func = mock.MagicMock()

    jsonapi.api_call(testdata)


def test_set():
    """
    Test the 'set' implementation
    """
    testdata = {
        'name': 'test_val',
        'value': 255
    }

    jsonapi.api_set(testdata)
    assert robot.robot.test_val == 255


def test_handle():
    """
    Test the request handler
    """
    jsonapi.TEST_QUEUE = True
    start_server_thread()
    sock = connect_server()

    # test malformed data
    sock.send(b'NOTJSON\n')
    assert jsonapi.test_queue.get() == 'Request Done'
    # ensure it returns an error code
    assert json.loads(sock.recv(1024).decode())['status'] == -1

    # test correct data
    testdata = {
        'a': 'b'
    }
    with mock.patch.object(jsonapi, 'process_request') as m:
        sock.send(json.dumps(testdata).encode() + b'\n')
        assert jsonapi.test_queue.get() == 'Request Done'
        m.assert_called_with(testdata)
        sock.recv(1024)

    sock.close()
    jsonapi.server.shutdown()


def test_on_exit():
    """
    Test that the onexit method properly shuts down the server.
    """
    old_shutdown = jsonapi.server.shutdown
    jsonapi.server.shutdown = mock.MagicMock()
    jsonapi.on_exit()
    assert jsonapi.server.shutdown.called
    jsonapi.server.shutdown = old_shutdown
