import socketserver
import json

from . import robot
from . import config


DECODE_ERROR = {
    'status': -1,
    'message': 'Exception occurred while loading request'
}

SUCCESS = {
    'status': 0,
    'message': 'success'
}


class JSONAPIServer(socketserver.StreamRequestHandler):
    """
    A server exposing a JSON based API over raw sockets.
    """
    def __init__(self):
        """
        Instantiate a JSONAPIServer.
        """

    def handle(self):
        while True:
            try:
                line = self.rfile.readline()
                # other end closed, we're done here!
                if line == b'':
                    break
                req = json.loads(line)
            except:
                self.wfile.write(json.dumps(DECODE_ERROR))

            if 'call' in req and 'args' in req:
                func = getattr(robot.robot, req['call'])
                if func:
                    func(**req['args'])
            if 'set' in req and 'value' in req:
                setattr(robot.robot, args['set'], args['value'])


server = socketserver.TCPServer(config.JSONAPI_BIND_ADDR, JSONAPIServer)
