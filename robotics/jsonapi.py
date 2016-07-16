import socketserver
import json
import signal
import sys
import queue
import socket

from . import robot
from . import config


# part of test system, allows test to reliably tell when its request has
# been processed
TEST_QUEUE = False
test_queue = queue.Queue()


DECODE_ERROR = {
    'status': -1,
    'message': 'Exception occurred while loading request'
}

SUCCESS = {
    'status': 0,
    'message': 'success'
}


class TestableServer(socketserver.TCPServer):

    def __init__(self, *args, **kwargs):
        socketserver.TCPServer.__init__(self, *args, **kwargs)

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        socketserver.TCPServer.server_bind(self)

    def server_activate(self):
        socketserver.TCPServer.server_activate(self)
        if TEST_QUEUE:
            test_queue.put('Server Running')


class JSONAPIServer(socketserver.StreamRequestHandler):
    """
    A server exposing a JSON based API over raw sockets.
    """

    def handle(self):
        while True:
            try:
                # NOTE NOTE NOTE: if handle() is stuck, YOU FORGOT A NEWLINE!
                line = self.rfile.readline()
                # other end closed, we're done here!
                if line == b'':
                    break
                req = json.loads(line.decode())
            except Exception as e:
                self.wfile.write(json.dumps(DECODE_ERROR).encode())
                if TEST_QUEUE:
                    test_queue.put('Request Done')
                continue

            if 'call' in req and 'args' in req:
                func = getattr(robot.robot, req['call'])
                if func:
                    func(**req['args'])
            if 'set' in req and 'value' in req:
                setattr(robot.robot, req['set'], req['value'])
            if TEST_QUEUE:
                test_queue.put('Request Done')


def termination_handler():
    # SIGTERM signal handler
    server.shutdown()
    sys.exit(0)

signal.signal(signal.SIGTERM, termination_handler)


def run():
    global server
    server = TestableServer(config.JSONAPI_BIND_ADDR, JSONAPIServer)
    server.serve_forever()
