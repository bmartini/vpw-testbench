#!/usr/bin/env python3
"""
Tutorial_1c testbench
"""

import vpw

from typing import Generator


class Write:
    def __init__(self, addr_width: int, data_width: int) -> None:
        self.__data_width = data_width
        self.__addr_width = addr_width

    def set(self, addr: int, data: int) -> None:
        self.__dut.prep("wr_data", vpw.pack(self.__data_width, data))
        self.__dut.prep("wr_addr", vpw.pack(self.__addr_width, addr))
        self.__dut.prep("wr_en", [1])

    def init(self, dut) -> Generator:
        self.__dut = dut

        # init values applied to the write interface when registered
        self.__dut.prep("wr_data", vpw.pack(self.__data_width, 0))
        self.__dut.prep("wr_addr", vpw.pack(self.__addr_width, 0))
        self.__dut.prep("wr_en", [0])

        while True:
            yield  # pause until a tick
            self.__dut.prep("wr_data", vpw.pack(self.__data_width, 0))
            self.__dut.prep("wr_addr", vpw.pack(self.__addr_width, 0))
            self.__dut.prep("wr_en", [0])


class Read:
    def __init__(self, addr_width: int) -> None:
        self.__addr_width = addr_width

    def set(self, addr: int) -> None:
        self.__dut.prep("rd_addr", vpw.pack(self.__addr_width, addr))
        self.__dut.prep("rd_en", [1])

    def init(self, dut) -> Generator:
        self.__dut = dut

        # init values applied to the read interface when registered
        self.__dut.prep("rd_addr", vpw.pack(self.__addr_width, 0))
        self.__dut.prep("rd_en", [0])

        while True:
            yield  # pause until a tick
            self.__dut.prep("rd_addr", vpw.pack(self.__addr_width, 0))
            self.__dut.prep("rd_en", [0])


if __name__ == '__main__':

    dut = vpw.create(package='tutorial_1c',
                     module='bram',
                     clock='clk')

    vpw.init(dut)

    write = Write(8, 32)
    vpw.register(write)

    read = Read(8)
    vpw.register(read)

    vpw.idle(10)

    print("\nSend data to be written to BRAM\n")
    for i in range(10):
        write.set(i, (i + 1))
        io = vpw.tick()
        print(f"write addr: {i}, data: {io['wr_data']}")

    vpw.idle(10)

    print("\nReceive data as it is read from BRAM\n")
    # send read address, it is only after this 'tick' that the values are applied
    read.set(0)
    io = vpw.tick()

    for i in range(1, 11):
        read.set(i)
        io = vpw.tick()
        print(f"read addr: {(i - 1)}, data: {io['rd_data']}")

    vpw.idle(10)

    print("")
    vpw.finish()
