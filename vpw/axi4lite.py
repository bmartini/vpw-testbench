"""
AXI4Lite Slave Interface
"""

import vpw

from typing import Callable
from typing import Deque
from typing import Generator
from typing import Optional

from collections import deque


class Master:
    def __init__(self, interface: str, data_width: int, addr_width: int) -> None:
        assert((data_width % 8) == 0)
        assert(addr_width <= 64)
        self.interface = interface
        self.data_width = data_width
        self.addr_width = addr_width

        self.queue_w: Deque[int] = deque()   # write data channel
        self.queue_aw: Deque[int] = deque()  # write address channel
        self.queue_r: Deque[int] = deque()   # read data channel
        self.queue_ar: Deque[int] = deque()  # read address channel

    def __w(self) -> Generator:

        while True:
            if not self.queue_w:
                self.__dut.prep(f"{self.interface}_wdata", vpw.pack(self.data_width, 0))
                self.__dut.prep(f"{self.interface}_wstrb", [0])
                self.__dut.prep(f"{self.interface}_wvalid", [0])
                io = yield
            else:
                value: int = self.queue_w[0]
                strb: int = (1 << int(self.data_width/8)) - 1
                self.__dut.prep(f"{self.interface}_wdata", vpw.pack(self.data_width, value))
                self.__dut.prep(f"{self.interface}_wstrb", [strb])
                self.__dut.prep(f"{self.interface}_wvalid", [1])

                io = yield
                while io[f"{self.interface}_wready"] == 0:
                    io = yield

                self.queue_w.popleft()

    def __aw(self) -> Generator:

        while True:
            if not self.queue_aw:
                self.__dut.prep(f"{self.interface}_awaddr", [0])
                self.__dut.prep(f"{self.interface}_awprot", [0])
                self.__dut.prep(f"{self.interface}_awvalid", [0])
                io = yield
            else:
                addr: int = int(self.queue_aw[0] * (self.data_width/8))
                self.__dut.prep(f"{self.interface}_awaddr", [addr])
                self.__dut.prep(f"{self.interface}_awprot", [0])
                self.__dut.prep(f"{self.interface}_awvalid", [1])

                io = yield
                while io[f"{self.interface}_awready"] == 0:
                    io = yield

                self.queue_aw.popleft()

    def __r(self) -> Generator:

        # setup
        self.__dut.prep(f"{self.interface}_rready", [1])

        while True:
            io = yield

            if io[f"{self.interface}_rready"] and io[f"{self.interface}_rvalid"]:
                self.queue_r.append(vpw.unpack(self.data_width,
                                               io[f"{self.interface}_rdata"]))

    def __ar(self) -> Generator:

        while True:
            if not self.queue_ar:
                self.__dut.prep(f"{self.interface}_araddr", [0])
                self.__dut.prep(f"{self.interface}_arprot", [0])
                self.__dut.prep(f"{self.interface}_arvalid", [0])
                io = yield
            else:
                addr: int = int(self.queue_ar[0] * (self.data_width/8))
                self.__dut.prep(f"{self.interface}_araddr", [addr])
                self.__dut.prep(f"{self.interface}_arprot", [0])
                self.__dut.prep(f"{self.interface}_arvalid", [1])

                io = yield
                while io[f"{self.interface}_arready"] == 0:
                    io = yield

                self.queue_ar.popleft()

    def send_write(self, addr: int, value: int) -> None:
        """ Non-Blocking write address/data send """
        self.queue_w.append(value)
        self.queue_aw.append(addr)

    def send_read(self, addr: int) -> None:
        """ Non-Blocking read address send """
        self.queue_ar.append(addr)

    def recv_read(self) -> Optional[int]:
        """ Non-Blocking read data receive """
        if not self.queue_r:
            return None
        else:
            return self.queue_r.popleft()

    def write(self, tick: Callable, addr: int, value: int) -> None:
        """ Blocking write address/data send """
        self.send_write(addr, value)
        tick()

    def read(self, tick: Callable, addr: int) -> int:
        """ Blocking read address send & data receive """
        self.send_read(addr)
        while True:
            tick()

            value = self.recv_read()
            if isinstance(value, int):
                return value

    def init(self, dut) -> Generator:
        self.__dut = dut

        ch_w = self.__w()
        ch_aw = self.__aw()
        ch_r = self.__r()
        ch_ar = self.__ar()

        next(ch_w)
        next(ch_aw)
        next(ch_r)
        next(ch_ar)

        self.__dut.prep(f"{self.interface}_bready", [1])

        while True:
            io = yield

            ch_w.send(io)
            ch_aw.send(io)
            ch_r.send(io)
            ch_ar.send(io)
