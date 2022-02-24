#!/usr/bin/env python3
"""
Example testbench
"""

import vpw.util as util
import vpw.axis
import vpw.axim
import vpw.axim2ram

import random

if __name__ == '__main__':

    dut = util.parse(module='example',
                     clock='clk')
    util.init(dut)

    up_stream = vpw.axis.Master("up_axis", 32, concat=2)
    util.register(up_stream)

    dn_stream = vpw.axis.Slave("dn_axis", 32, concat=2)
    util.register(dn_stream)

    axim = vpw.axim.Master("axim", 128, 16)
    util.register(axim)

    util.register(vpw.axim2ram.Memory("axim2ram", 128, 16))

    # test AXI-Streaming interface
    data1 = [n+1 for n in range(16)]
    data2 = [17, 18, 19, 20, 21, 22, 23, 24]
    up_stream.send(data1, position=0)
    up_stream.send(data2, position=1)

    dn_stream.ready(True, position=0)
    dn_stream.ready(True, position=1)

    util.idle(100)

    print("First stream received")
    stream = dn_stream.recv(position=0)
    for x in stream:
        print(f"stream 1: {x}")

    print("Second stream received")
    stream = dn_stream.recv(position=1)
    for x in stream:
        print(f"stream 2: {x}")

    print("Intermittent ready on down stream receive")
    up_stream.send([n+1 for n in range(10)], position=0)
    while len(dn_stream.queue[0]) == 0:
        dn_stream.ready(bool(random.getrandbits(1)))
        util.tick()

    stream = dn_stream.recv(position=0)
    for x in stream:
        print(f"intermittent: {x}")

    # test AXI-MM interface
    axim.send_write(0, [n+1 for n in range(128)])

    util.idle(1000)

    axim.send_read(0, 128)

    while True:
        util.tick()
        burst = axim.recv_read()
        if burst:
            print(burst)
            for x, beat in enumerate(burst):
                assert((x+1) == beat)

            break

    util.idle(100)

    util.finish()
