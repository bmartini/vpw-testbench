#!/usr/bin/env python3
"""
Tutorial_1a testbench
"""

import vpw.util as util

def prep_wr_bus(en, addr, data):
    util.prep(f"wr_data", util.pack(32, data))
    util.prep(f"wr_addr", util.pack(8, addr))
    util.prep(f"wr_en", [en])


def prep_rd_bus(en, addr):
    util.prep(f"rd_addr", util.pack(8, addr))
    util.prep(f"rd_en", [en])


if __name__ == '__main__':

    dut = util.parse(package='tutorial_1a',
                     module='bram',
                     clock='clk')

    util.init(dut)

    util.idle(10)
    prep_wr_bus(0, 0, 0)
    prep_rd_bus(0, 0)

    print(f"\nSend data to be written to BRAM\n")
    for i in range(10):
        prep_wr_bus(1, i, (i + 1))
        io = util.tick()
        print(f"write addr: {i}, data: {io['wr_data']}")

    prep_wr_bus(0, 0, 0)
    util.idle(10)

    print(f"\nReceive data as it is read from BRAM\n")
    # send read address, it is only after this 'tick' that the values are applied
    prep_rd_bus(1, 0)
    io = util.tick()

    for i in range(1, 11):
        prep_rd_bus(1, i)
        io = util.tick()
        print(f"read addr: {(i - 1)}, data: {io['rd_data']}")

    prep_rd_bus(0, 0)
    util.idle(10)

    print(f"")
    util.finish()