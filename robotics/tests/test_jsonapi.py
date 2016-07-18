import threading
import socket
import json
from unittest import mock

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


def test_call():
    """
    Test the 'call' method in an incoming jsonapi data structure
    """
    testdata = {
        'call': 'test_func',
        'args': {'test': 42}
    }

    jsonapi.TEST_QUEUE = True
    robot.robot.test_func = mock.MagicMock()

    start_server_thread()
    sock = connect_server()

    sock.send((json.dumps(testdata) + '\n').encode())
    assert jsonapi.test_queue.get() == 'Request Done'
    robot.robot.test_func.assert_called_with(test=42)

    sock.close()
    jsonapi.server.shutdown()


def test_baddata():
    """
    Sends the jsonapi some malformed JSON to make sure it errors out properly.
    """
    jsonapi.TEST_QUEUE = True
    start_server_thread()
    sock = connect_server()

    sock.send(b'NOTJSON\n')
    assert jsonapi.test_queue.get() == 'Request Done'
    # ensure it returns an error code
    assert json.loads(sock.recv(1024).decode())['status'] == -1

    sock.close()
    jsonapi.server.shutdown()
