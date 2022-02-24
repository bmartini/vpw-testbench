#!/usr/bin/env python3
"""
Tutorial_1b testbench
"""

import vpw.util as util

from typing import Generator


class Write:
    def __init__(self, addr_width: int, data_width: int) -> None:
        self.__data_width = data_width
        self.__addr_width = addr_width

    def set(self, addr: int, data: int) -> None:
        self.__dut.prep(f"wr_data", util.pack(self.__data_width, data))
        self.__dut.prep(f"wr_addr", util.pack(self.__addr_width, addr))
        self.__dut.prep(f"wr_en", [1])

    def init(self, dut) -> Generator:
        self.__dut = dut

        # init values applied to the write interface when registered
        self.__dut.prep(f"wr_data", util.pack(self.__data_width, 0))
        self.__dut.prep(f"wr_addr", util.pack(self.__addr_width, 0))
        self.__dut.prep(f"wr_en", [0])

        while True:
            yield  # pause until a tick
            self.__dut.prep(f"wr_data", util.pack(self.__data_width, 0))
            self.__dut.prep(f"wr_addr", util.pack(self.__addr_width, 0))
            self.__dut.prep(f"wr_en", [0])


class Read:
    def __init__(self, addr_width: int) -> None:
        self.__addr_width = addr_width

    def set(self, addr: int) -> None:
        self.__dut.prep(f"rd_addr", util.pack(self.__addr_width, addr))
        self.__dut.prep(f"rd_en", [1])

    def init(self, dut) -> Generator:
        self.__dut = dut

        # init values applied to the read interface when registered
        self.__dut.prep(f"rd_addr", util.pack(self.__addr_width, 0))
        self.__dut.prep(f"rd_en", [0])

        while True:
            yield  # pause until a tick
            self.__dut.prep(f"rd_addr", util.pack(self.__addr_width, 0))
            self.__dut.prep(f"rd_en", [0])


if __name__ == '__main__':

    dut = util.parse(package='tutorial_1b',
                     module='bram',
                     clock='clk')

    util.init(dut)

    write = Write(8, 32)
    util.register(write)

    read = Read(8)
    util.register(read)

    util.idle(10)

    print(f"\nSend data to be written to BRAM\n")
    for i in range(10):
        write.set(i, (i + 1))
        io = util.tick()
        print(f"write addr: {i}, data: {io['wr_data']}")

    util.idle(10)

    print(f"\nReceive data as it is read from BRAM\n")
    # send read address, it is only after this 'tick' that the values are applied
    read.set(0)
    io = util.tick()

    for i in range(1, 11):
        read.set(i)
        io = util.tick()
        print(f"read addr: {(i - 1)}, data: {io['rd_data']}")

    util.idle(10)

    print(f"")
    util.finish()
