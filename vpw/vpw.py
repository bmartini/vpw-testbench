"""
Verilator Python Wrapper Package
"""

#import testbench as dut  # type: ignore

# Maintains persistent background tasks in the form of a list of generators
# that get incremented every clock cycle.
background = []


def init():
    dut.init()


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
