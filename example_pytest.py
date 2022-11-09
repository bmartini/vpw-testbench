"""
Example testbench for use with pytest
"""

import vpw
import vpw.axis
import vpw.axim
import vpw.axim2ram

import pytest
import random
import shutil
import tempfile


@pytest.fixture(scope="module")
def design():
    workspace = tempfile.mkdtemp()

    dut = vpw.create(package='example_pytest',
                     module='example',
                     clock='clk',
                     workspace=workspace)
    yield dut

    shutil.rmtree(workspace)


@pytest.fixture
def context(design):
    vpw.init(design, trace=False)

    up_stream = vpw.axis.Master("up_axis", 32, concat=2)
    vpw.register(up_stream)

    dn_stream = vpw.axis.Slave("dn_axis", 32, concat=2)
    vpw.register(dn_stream)

    axim = vpw.axim.Master("axim", 128, 16)
    vpw.register(axim)

    vpw.register(vpw.axim2ram.Memory("axim2ram", 128, 16))

    yield up_stream, dn_stream, axim

    vpw.idle(100)
    vpw.finish()


def test_stream_one(context):
    """Test AXI-Streaming interface with one stream."""
    up_stream, dn_stream, _ = context

    data = [n+1 for n in range(16)]
    up_stream.send(data, position=0)
    dn_stream.ready(True, position=0)

    vpw.idle(100)

    stream = dn_stream.recv(position=0)
    assert stream == data, "received stream not the as sent"


def test_stream_two(context):
    """Test AXI-Streaming interface with two streams."""
    up_stream, dn_stream, _ = context

    data1 = [n+1 for n in range(16)]
    data2 = [17, 18, 19, 20, 21, 22, 23, 24]
    up_stream.send(data1, position=0)
    up_stream.send(data2, position=1)

    dn_stream.ready(True, position=0)
    dn_stream.ready(True, position=1)

    vpw.idle(100)

    stream1 = dn_stream.recv(position=0)
    assert stream1 == data1, "received stream 1 not the as sent"

    stream2 = dn_stream.recv(position=1)
    assert stream2 == data2, "received stream 2 not the as sent"


def test_stream_intermittent_ready(context):
    """Test AXI-Streaming interface.

    Send one stream with intermittent downstream ready.
    """
    up_stream, dn_stream, _ = context

    data = [n+1 for n in range(10)]
    up_stream.send(data, position=0)

    while len(dn_stream.queue[0]) == 0:
        dn_stream.ready(bool(random.getrandbits(1)))
        vpw.tick()

    vpw.idle(10)

    stream = dn_stream.recv(position=0)
    assert stream == data, "received stream not the as sent"


def test_stream_intermittent_valid(context):
    """Test AXI-Streaming interface.

    Send one stream with intermittent upstream valid.
    """
    up_stream, dn_stream, _ = context

    data = [n+1 for n in range(10)]
    up_stream.send(data, position=1)
    dn_stream.ready(True, position=1)

    while len(dn_stream.queue[1]) == 0:
        up_stream.pause(bool(random.getrandbits(1)), 1)
        vpw.tick()

    vpw.idle(10)

    stream = dn_stream.recv(position=1)
    assert stream == data, "received stream not the as sent"


def test_memory_mapped(context):
    """Test AXI-MM interface with large write/read pair."""
    _, _, axim = context

    data = [n+1 for n in range(512)]
    axim.write(vpw.tick, 256, data, 1)

    received = axim.read(vpw.tick, 256, int(len(data) * 128 / 8), 1)

    for s, r in zip(data, received):
        assert s == r, "data value sent is not what was received"
