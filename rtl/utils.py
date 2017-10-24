#!/usr/bin/env python
# Copyright (c) 2016 Angel Terrones (<angelterrones@gmail.com>)

import math
import myhdl as hdl


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def createSignal(init, width):
    """
    Wrapper to create mydhl Signals.

    Args:
    - init:  Initial value.
    - width: Signal width.
    """
    assert width >= 1, "Invalid width = {0}".format(width)
    if width > 1:
        return hdl.Signal(hdl.modbv(init)[width:])
    else:
        return hdl.Signal(True if init else False)


def createModbv(init, width):
    """
    Wrapper to create unsigned bit vectors.

    Args:
    - init:  Initial value.
    - width: Signal width.
    """
    assert width >= 1, "Invalid width = {0}".format(width)
    return hdl.modbv(init)[width:]


def reverseBits(data):
    """
    Reverse bit order.

    Example:
    a = reverseBits(0x33)  # a == 0xCC.

    Args:
    - data: Bit-vector to reverse.
    """
    width = len(data)
    tmp = [data(i) for i in range(width)]  # reverse
    return hdl.ConcatSignal(*tmp)  # concat and return


def isPow2(num):
    """
    Check if a given number is a power of 2.

    Args:
    - num: Positive integer.
    """
    assert type(num) == int, "Wrong data type for {0}: {1}".format(num, type(num))
    return num >= 0 and ((num & (num - 1)) == 0)


def log2up(num):
    """
    Get minimal lenght of a bit-vector able to hold the given number.

    Args:
    - num: Positive integer.
    """
    assert type(num) == int, "Wrong data type for {0}: {1}".format(num, type(num))
    assert num > 0, "The argument must be a positive number"
    return int(math.ceil(math.log(num, 2)))


def loh2bin(num):
    """
    Priority encoder.

    Args:
    - num: Bit-vector.
    """
    assert len(num) > 0, "The argument must have a valid lenght"
    index = 0
    for i in range(len(num)):
        if num[i]:
            index = i

    return index


def andReduce(vector):
    """
    AND all elements of a n-bit array.

    Args:
    - num: Bit-vector.
    """
    sz = len(vector)
    assert sz > 0, "Argument must have a length > 0"
    value = True
    for i in range(sz):
        value = value and vector[i]
    return value


def orReduce(vector):
    """
    OR all elements of a n-bit array.

    Args:
    - num: Bit-vector.
    """
    sz = len(vector)
    assert sz > 0, "Argument must have a length > 0"
    value = False
    for i in range(sz):
        value = value or vector[i]
    return value

# Local Variables:
# flycheck-flake8-maximum-line-length: 200
# flycheck-flake8rc: ".flake8rc"
# End:
