#!/usr/bin/env python3
"""
Example testbench
"""

import vpw
import vpw.axis as axis


if __name__ == '__main__':

    vpw.init()

    up_stream = axis.master("up_axis_t", 64)
    vpw.register(up_stream)

    dn_stream = axis.slave("dn_axis_t", 64)
    vpw.register(dn_stream)

    vpw.idle(100)

    vpw.finish()
