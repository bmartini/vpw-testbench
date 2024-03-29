#!/usr/bin/env python3
"""
Tutorial_1b testbench
"""

import vpw


def prep_wr_bus(en, addr, data):
    vpw.prep("wr_data", vpw.pack(128, data))
    vpw.prep("wr_addr", vpw.pack(8, addr))
    vpw.prep("wr_en", [en])


def prep_rd_bus(en, addr):
    vpw.prep("rd_addr", vpw.pack(8, addr))
    vpw.prep("rd_en", [en])


if __name__ == '__main__':

    dut = vpw.create(package='tutorial_1b',
                     module='bram',
                     clock='clk',
                     parameter={'BRAM_DWIDTH': 128,
                                'BRAM_AWIDTH': 8})

    vpw.init(dut)

    vpw.idle(10)
    prep_wr_bus(0, 0, 0)
    prep_rd_bus(0, 0)

    print("\nSend data to be written to BRAM\n")
    for i in range(10):
        prep_wr_bus(1, i, (i + 1))
        io = vpw.tick()
        print(f"write addr: {i}, data: {vpw.unpack(128, io['wr_data'])}")

    prep_wr_bus(0, 0, 0)
    vpw.idle(10)

    print("\nReceive data as it is read from BRAM\n")
    # send read address, it is only after this 'tick' that the values are applied
    prep_rd_bus(1, 0)
    io = vpw.tick()

    for i in range(1, 11):
        prep_rd_bus(1, i)
        io = vpw.tick()
        print(f"read addr: {(i - 1)}, data: {vpw.unpack(128, io['rd_data'])}")

    prep_rd_bus(0, 0)
    vpw.idle(10)

    print("")
    vpw.finish()
