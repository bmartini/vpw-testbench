"""
Verilator Python Wrapper Package
"""

from typing import List

from math import ceil

import testbench as dut  # type: ignore

# Maintains persistent background tasks in the form of a list of generators
# that get incremented every clock cycle.
background = []


def init(trace: bool = True):
    dut.init(trace)


def prep(port: str, value: List[int]):
    dut.prep(port, value)


def pack(data_width: int, val: int) -> List[int]:
    if data_width <= 64:
        return [val]
    else:
        start = ceil(data_width / 32)
        shift = [32*s for s in range(start)]
        return [((val >> s) & 0xffffffff) for s in shift]


def unpack(data_width: int, val: List[int]) -> int:
    if data_width <= 64:
        return val[0]
    else:
        start = ceil(data_width / 32)
        shift = [32*s for s in range(start)]
        number: int = 0
        for v, s in zip(val, shift):
            number = number | (v << s)

        return number


def register(interface):
    """ When an interface is registered with VPW it's first initiated and then
    its generator is run in the background """

    gen = interface.init(dut)
    next(gen)

    background.append(gen)


def tick():
    """ Advance TB clock """

    io = dut.tick()
    for gen in background:
        gen.send(io)

    return io


def idle(time: int = 1):
    """ Idle for a number of clock cycles """

    for _ in range(time):
        tick()


def finish():
    dut.finish()
