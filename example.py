#!/usr/bin/env python3
"""
Example testbench
"""

import vpw.util as vpw
import vpw.axis as axis

import random

if __name__ == '__main__':

    vpw.init()

    up_stream = axis.Master("up_axis", 64)
    vpw.register(up_stream)

    dn_stream = axis.Slave("dn_axis", 64)
    vpw.register(dn_stream)

    data1 = [n+1 for n in range(16)]
    data2 = [17, 18, 19, 20, 21, 22, 23, 24]
    up_stream.send(data1)
    up_stream.send(data2)

    vpw.idle(10)

    dn_stream.ready(True)

    vpw.idle(100)

    print("First stream received")
    stream = dn_stream.recv()
    for x in stream:
        print(f"stream 1: {x}")

    print("Second stream received")
    stream = dn_stream.recv()
    for x in stream:
        print(f"stream 2: {x}")

    print("Intermittent ready on down stream receive")
    up_stream.send([n+1 for n in range(10)])
    while len(dn_stream.queue) == 0:
        dn_stream.ready(bool(random.getrandbits(1)))
        vpw.tick()

    stream = dn_stream.recv()
    for x in stream:
        print(f"intermittent: {x}")

    vpw.finish()
