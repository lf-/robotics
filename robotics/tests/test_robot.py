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
