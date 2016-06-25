def translate(value, leftMin, leftMax, rightMin, rightMax):
    """
    Map one range of values to another.

    Parameters:
    value -- the number, between leftMin and leftMax to map into
             rightMin to rightMax
    leftMin -- bottom of range of value parameter
    leftMax -- top of range of value parameter
    rightMin -- bottom of range of output
    rightMax -- top of range of output
    """
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)
