import argparse
import sys
import socket
import json
import logging


logging.basicConfig(level=logging.DEBUG)


class RoboticsConnection:
    def __init__(self, remote):
        """
        Connection to a robotd server

        Parameters:
        remote -- (host, port) tuple for server to connect to
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(remote)
        logging.info('Connecting to {addr[0]}:{addr[1]}'.format(addr=remote))

    def call(self, method, params):
        obj = {
            'method': 'call',
            'data': {
                'call': method,
                'args': params
            }
        }
        msg = json.dumps(obj)
        self.send(msg)

    def send(self, msg: str):
        """
        Sends some data to the remote robotd.

        Adds a carriage return for you.
        """
        data = msg.encode('utf-8') + b'\n'
        logging.debug('Sending {}'.format(data))
        self.sock.send(data)

    def robot_init(self):
        """
        Perform initialisation for the robot hardware.
        """
        self.call('init', {})


def parse_ip(ip):
    """
    Parse an IPv4 address:port (robotd does not intentionally support IPv6)

    Arguments:
    ip -- an IPv4 address:port

    Returns:
    (ip: str, port: int) tuple

    Raises an argparse.ArgumentTypeError if the provided ip:port is invalid
    """
    if not len(ip.split(':')) == 2:
        raise argparse.ArgumentTypeError('Address "{}" is not in '
                                         'ip:port format'.format(ip))
    addr, port = ip.split(':')
    if not addr.count('.') == 3:
        raise argparse.ArgumentTypeError('There are not four components in the'
                                         ' provided address "{}"'.format(addr))
    for comp in addr.split('.'):
        comp = int(comp)
        if not (comp <= 255 and comp >= 0):
            raise argparse.ArgumentTypeError('IP component '
                                             'out of range: {}'.format(comp))
    return addr, int(port)


def parse_args(args: list) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog='robotctl')
    parser.add_argument('--remote', '-r', default='127.0.0.1:47777',
                        help='Address of robotd server to connect to',
                        type=parse_ip)
    subs = parser.add_subparsers(dest='subparser')
    init_sub = subs.add_parser('init')
    return parser.parse_args(args)


def handle_args(args):
    """
    Takes the result from parse_args() and executes the appropriate methods
    """
    def default(*args, **kwargs):
        raise ValueError('Invalid method')
    method = subparser_handlers.get(args.subparser, 'invalid')
    conn = RoboticsConnection(args.remote)
    meth = getattr(conn, method, default)
    meth(args)


def main(args):
    parsed_args = parse_args(args)
    handle_args(parsed_args)


# handlers for subcommands
subparser_handlers = {
    'init': 'robot_init'
}


if __name__ == '__main__':
    main(sys.argv[1:])
