import argparse
import pytest
from unittest import mock

from .. import cli


def test_parse_args():
    assert cli.parse_args(['--remote', '123.4.5.6:234']).remote == ('123.4.5.6', 234)
    assert cli.parse_args(['init']).subparser == 'init'


def test_parse_ip():
    with pytest.raises(argparse.ArgumentTypeError):
        cli.parse_ip('123.4.5.6')
    with pytest.raises(argparse.ArgumentTypeError):
        cli.parse_ip('123.4.5.6.7:4444')
    with pytest.raises(argparse.ArgumentTypeError):
        cli.parse_ip('123.456.5.7:4444')
    assert cli.parse_ip('123.4.5.6:4444') == ('123.4.5.6', 4444)


@mock.patch.dict(cli.subparser_handlers, {'test': 'test'})
@mock.patch('socket.socket')
def test_handle_args(_):
    args = argparse.Namespace(remote=('127.0.0.1', 47777), subparser='test')
    cli.RoboticsConnection.test = mock.MagicMock()
    cli.handle_args(args)
    cli.RoboticsConnection.test.assert_called_with(args)

    failargs = argparse.Namespace(remote=('127.0.0.1', 47777), subparser='nonexistant')
    with pytest.raises(ValueError):
        cli.handle_args(failargs)


@mock.patch('socket.socket')
def test_connect(sock_mock):
    remote_addr = ('1.2.3.4', 5678)
    conn = cli.RoboticsConnection(remote_addr)
    conn.sock.connect.assert_called_with(remote_addr)


@mock.patch('socket.socket')
def test_call(_):
    import json
    conn = cli.RoboticsConnection(('1.2.3.4', 5678))
    expect = {
        'method': 'call',
        'data': {
            'call': 'test',
            'args': {'a': 'b'}
        }
    }
    with mock.patch.object(conn, 'send') as send_mock:
        conn.call('test', {'a': 'b'})
        assert json.loads(send_mock.call_args[0][0]) == expect


@mock.patch('socket.socket')
def test_send(_):
    remote_addr = ('1.2.3.4', 5678)
    conn = cli.RoboticsConnection(remote_addr)
    conn.send('1234')
    conn.sock.send.assert_called_with(b'1234\n')


@mock.patch.object(cli.RoboticsConnection, 'call')
@mock.patch('socket.socket')
def test_init(_, call_mock):
    remote_addr = ('1.2.3.4', 5678)
    conn = cli.RoboticsConnection(remote_addr)
    conn.robot_init()
    call_mock.assert_called_with('init', {})


@mock.patch.object(cli, 'handle_args')
def test_main(handle_args_mock):
    cli.main(('init',))
    handle_args_mock.assert_called_with(argparse.Namespace(subparser='init', remote=('127.0.0.1', 47777)))
