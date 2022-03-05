#!/usr/bin/env python3
"""
Tutorial_1a testbench
"""

import vpw

if __name__ == '__main__':

    dut = vpw.create(package='tutorial_1a',
                     module='bram',
                     clock='clk',
                     parameter={'BRAM_DWIDTH': 32,
                                'BRAM_AWIDTH': 8})

    dut.init(trace=True)

    for _ in range(10):
        dut.tick()

    dut.prep("wr_data", [0])
    dut.prep("wr_addr", [0])
    dut.prep("wr_en", [0])
    dut.prep("rd_addr", [0])
    dut.prep("rd_en", [0])
    dut.tick()

    print(f"\nSend data to be written to BRAM\n")
    for i in range(10):
        dut.prep("wr_data", [i + 1])
        dut.prep("wr_addr", [i])
        dut.prep("wr_en", [1])
        io = dut.tick()
        print(f"write addr: {i}, data: {io['wr_data']}")

    dut.prep("wr_data", [0])
    dut.prep("wr_addr", [0])
    dut.prep("wr_en", [0])

    for _ in range(10):
        dut.tick()

    print(f"\nReceive data as it is read from BRAM\n")
    # send read address, it is only after this 'tick' that the values are applied
    dut.prep("rd_addr", [0])
    dut.prep("rd_en", [1])
    io = dut.tick()

    for i in range(1, 11):
        dut.prep("rd_addr", [i])
        dut.prep("rd_en", [1])
        io = dut.tick()
        print(f"read addr: {(i - 1)}, data: {io['rd_data']}")

    dut.prep("rd_addr", [0])
    dut.prep("rd_en", [0])

    for _ in range(10):
        dut.tick()

    print("")
    dut.finish()
