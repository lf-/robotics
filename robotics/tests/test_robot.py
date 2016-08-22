from unittest import mock

from .. import robot


def test_move():
    # full speed, no turn
    robot.robot.move(1, 0)
    assert robot.robot.throttleL == 1.0
    assert robot.robot.throttleR == 1.0
    # full speed, full right
    robot.robot.move(1, 1)
    assert robot.robot.throttleL == 1.0
    assert robot.robot.throttleR == 0.0
    # full speed, full left
    robot.robot.move(1, -1)
    assert robot.robot.throttleL == 0.0
    assert robot.robot.throttleR == 1.0
    # full reverse, no turn
    robot.robot.move(-1, 0)
    assert robot.robot.throttleL == -1.0
    assert robot.robot.throttleR == -1.0
    # full reverse, full right
    robot.robot.move(-1, 1)
    assert robot.robot.throttleL == -1.0
    assert robot.robot.throttleR == 0.0
    # full reverse, full left
    robot.robot.move(-1, -1)
    assert robot.robot.throttleL == 0.0
    assert robot.robot.throttleR == -1.0
    # reverse drive, full speed, full right
    robot.robot.reverse_drive = True
    robot.robot.move(1, 1)
    assert robot.robot.throttleL == 0.0
    assert robot.robot.throttleR == 1.0


def test_state():
    state = robot.robot.state
    for prop in robot.Robot.STATE_PROPS:
        assert prop in state
        assert state[prop] == getattr(robot.robot, prop)


def test_movement_properties():
    with mock.patch.object(robot.robot, 'move') as mock_move:
        assert robot.robot.throttle == robot.robot._throttle
        assert robot.robot.turn == robot.robot._turn
        robot.robot.throttle = 1
        mock_move.assert_called_with(1, robot.robot._turn)
        robot.robot.turn = 1
        mock_move.assert_called_with(robot.robot._throttle, 1)


def test_safe():
    robot.robot.safe()
    assert robot.robot.state == robot.Robot.SAFE_STATE
