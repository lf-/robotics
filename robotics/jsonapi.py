import socketserver
import json
import queue
import socket
import atexit

from . import robot
from . import config


# part of test system, allows test to reliably tell when its request has
# been processed
TEST_QUEUE = False
test_queue = queue.Queue()


SUCCESS = {
    'status': 0,
    'exception': None,
    'message': 'success'
}


def require(required, data):
    """
    Require that all of required are in data

    Parameters:
    required -- iterable of things required to be contained in data
    data -- an object supporting the contains operator
    """
    if not all(x in data for x in required):
        raise ValueError('Not all of required {} in '
                         'provided object'.format(required))


class TestableServer(socketserver.TCPServer):
    """
    A modified TCPServer that does the thing, but better!

    * Complies with the test queue scheme for synchronisation

    * Actually binds to the socket when the OS keeps it open for no
      bloody reason

    * Shutdown shuts down and cleans up, because that makes more sense than
      default behaviour!
    """

    def __init__(self, *args, **kwargs):
        socketserver.TCPServer.__init__(self, *args, **kwargs)

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        socketserver.TCPServer.server_bind(self)

    def server_activate(self):
        socketserver.TCPServer.server_activate(self)
        if TEST_QUEUE:
            test_queue.put('Server Running')

    def shutdown(self):
        socketserver.TCPServer.shutdown(self)
        socketserver.TCPServer.server_close(self)


def api_set(data):
    """
    API function to set a value on the Robot singleton

    Parameters:
    data -- dict, see below

    Dict contents:
    name -- name of the attribute to set
    value -- what to set it to
    """
    require(('name', 'value'), data)
    var = data['name']
    val = data['value']
    setattr(robot.robot, var, val)


def api_call(data):
    """
    API function to call a method on the Robot singleton

    Parameters:
    data -- dict, see below

    Dict contents:
    call -- name of the method to call
    args -- dict containing the keyword arguments for the method, see
            language note below

    Language note:
    Python allows positional arguments to be referred to by their names like
    keyword arguments. api_call(data=x) is valid, even though data is a
    positional argument
    """
    require(('call', 'args'), data)
    call = data['call']
    args = data['args']
    func = getattr(robot.robot, call)
    if func:
        func(**args)


def api_state(data):
    """
    API function to update the robot's state

    Parameters:
    data -- dict, see below

    Dict contents:
    state -- dict with the new state
    """
    require(('state',), data)
    robot.robot.update_state(data['state'])


def process_request(req: dict):
    """
    Processes a request, handing it off to the correct handler function

    Parameters:
    req -- request to process

    Dict contents:
    method -- method to use of (call, set)
    data -- data to hand off to that method
    """
    require(('method', 'data'), req)

    def method_missing(*args):
        raise ValueError('No such API method')

    method = METHODS.get(req['method'], method_missing)
    method(req['data'])


def get_error(exc: Exception) -> dict:
    """
    Gets the proper object to return to the sender from an exception
    """
    template = {
        'status': -1,
        'exception': exc.__class__.__name__,
        'message': exc.args
    }
    return template


class JSONAPIServer(socketserver.StreamRequestHandler):
    """
    A server exposing a JSON based API over a TCP socket
    """
    def respond(self, obj):
        """
        Respond to a request with a dict-like object
        """
        obj['state'] = robot.robot.state
        self.wfile.write((json.dumps(obj) + '\n').encode())

    def handle(self):
        while True:
            try:
                # NOTE NOTE NOTE: if handle() is stuck, YOU FORGOT A NEWLINE!
                line = self.rfile.readline()
                # other end closed, we're done here!
                if line == b'':
                    break
                req = json.loads(line.decode())
                process_request(req)
                # lack of exception implies success
                self.respond(SUCCESS)
            except Exception as e:
                self.respond(get_error(e))
            if TEST_QUEUE:
                test_queue.put('Request Done')


@atexit.register
def on_exit():
    """
    Shutdown on program end
    """
    server.shutdown()


def run():
    global server
    server = TestableServer(config.JSONAPI_BIND_ADDR, JSONAPIServer)
    server.serve_forever()


METHODS = {
    'set': api_set,
    'call': api_call,
    'state': api_state
}
