#!/usr/bin/env python3
"""
Example testbench
"""

import vpw.util as vpw
import vpw.axis as axis
import vpw.axim as axim
import vpw.axim2ram as axim2ram

import random

if __name__ == '__main__':

    vpw.init()

    up_stream = axis.Master("up_axis", 32, concat=2)
    vpw.register(up_stream)

    dn_stream = axis.Slave("dn_axis", 32, concat=2)
    vpw.register(dn_stream)

    axim = axim.Master("axim", 128, 16)
    vpw.register(axim)

    vpw.register(axim2ram.Memory("axim2ram", 128, 16))

    # test AXI-Streaming interface
    data1 = [n+1 for n in range(16)]
    data2 = [17, 18, 19, 20, 21, 22, 23, 24]
    up_stream.send(data1, position=0)
    up_stream.send(data2, position=1)

    dn_stream.ready(True, position=0)
    dn_stream.ready(True, position=1)

    vpw.idle(100)

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
        vpw.tick()

    stream = dn_stream.recv(position=0)
    for x in stream:
        print(f"intermittent: {x}")

    # test AXI-MM interface
    axim.send_write(0, [n+1 for n in range(128)])

    vpw.idle(1000)

    axim.send_read(0, 128)

    while True:
        vpw.tick()
        burst = axim.recv_read()
        if isinstance(burst, list):
            print(burst)
            for x, beat in enumerate(burst):
                assert((x+1) == beat)

            break

    vpw.idle(100)

    vpw.finish()
