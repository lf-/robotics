import threading
import time
import socket
import json
from unittest import mock

from .. import jsonapi
from .. import robot
from .. import config


def test_call():
    testdata = {
        'call': 'test_func',
        'args': {'test': 42}
    }

    jsonapi.TEST_QUEUE = True
    robot.robot.test_func = mock.MagicMock()
    # get jsonapi running in another thread
    thr = threading.Thread(target=jsonapi.run)
    thr.start()
    assert jsonapi.test_queue.get() == 'Server Running'
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(config.JSONAPI_BIND_ADDR)
    sock.send((json.dumps(testdata) + '\n').encode())
    assert jsonapi.test_queue.get() == 'Request Done'
    robot.robot.test_func.assert_called_with(test=42)
    sock.close()
    jsonapi.server.shutdown()


def test_baddata():
    jsonapi.TEST_QUEUE = True
    # get jsonapi running in another thread
    thr = threading.Thread(target=jsonapi.run)
    thr.start()
    assert jsonapi.test_queue.get() == 'Server Running'
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(config.JSONAPI_BIND_ADDR)
    sock.send(b'NOTJSON\n')
    assert jsonapi.test_queue.get() == 'Request Done'
    # ensure it returns an error code
    assert json.loads(sock.recv(1024).decode())['status'] == -1
    sock.close()
    jsonapi.server.shutdown()
