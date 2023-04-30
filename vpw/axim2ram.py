"""
Simplified AXIM (software) Slave Interface driving a Memory
"""

from queue import Queue
from types import ModuleType
from typing import Any, Dict, Generator

import vpw


class Memory:
    def __init__(self, interface: str, data_width: int, addr_width: int) -> None:
        self.interface = interface
        self.data_width = data_width
        self.addr_width = addr_width

        self.queue_w: "Queue[Dict[str, Any]]" = Queue()  # write data channel
        self.queue_aw: "Queue[Dict[str, Any]]" = Queue(4)  # write address channel
        self.queue_ar: "Queue[Dict[str, Any]]" = Queue(4)  # read address channel

        self.ram: Dict[int, int] = {}

    def __w(self) -> Generator:
        beat_nb = 0
        address = 0
        length = 0
        last = 0

        # setup
        self.__dut.prep(f"{self.interface}_wready", [1])

        while True:
            io = yield

            if io[f"{self.interface}_wready"] and io[f"{self.interface}_wvalid"]:
                self.queue_w.put({"wdata": io[f"{self.interface}_wdata"],
                                  "wlast": io[f"{self.interface}_wlast"]})

            if beat_nb == 0 and not self.queue_aw.empty():
                beat_nb = 1
                burst = self.queue_aw.get()
                address = burst["awaddr"]
                length = burst["awlen"] + 1
                self.__dut.prep(f"{self.interface}_wready", [1])

            if beat_nb > 0 and not self.queue_w.empty():

                if beat_nb > length:
                    assert(last)
                    self.__dut.prep(f"{self.interface}_wready", [0])
                    last = 0
                    beat_nb = 0
                else:
                    beat = self.queue_w.get()
                    self.ram[int(8*address/self.data_width) + beat_nb - 1] = \
                        vpw.unpack(self.data_width, beat["wdata"])
                    last = beat["wlast"]
                    beat_nb += 1

    def __aw(self) -> Generator:

        # setup
        self.__dut.prep(f"{self.interface}_awready", [1])

        while True:
            io = yield

            if io[f"{self.interface}_awready"] and io[f"{self.interface}_awvalid"]:
                self.queue_aw.put({"awaddr": io[f"{self.interface}_awaddr"],
                                   "awlen": io[f"{self.interface}_awlen"]})

            if self.queue_aw.full():
                self.__dut.prep(f"{self.interface}_awready", [0])
            else:
                self.__dut.prep(f"{self.interface}_awready", [1])

    def __r(self) -> Generator:
        beat_nb = 0
        address = 0
        length = 0
        read_id = 0

        # setup
        self.__dut.prep(f"{self.interface}_rdata", vpw.pack(self.data_width, 0))
        self.__dut.prep(f"{self.interface}_rid", [0])
        self.__dut.prep(f"{self.interface}_rlast", [0])
        self.__dut.prep(f"{self.interface}_rvalid", [0])

        while True:
            io = yield

            if io[f"{self.interface}_rready"] and io[f"{self.interface}_rvalid"]:

                if beat_nb == length:
                    beat_nb = 0
                    self.__dut.prep(f"{self.interface}_rdata", vpw.pack(self.data_width, 0))
                    self.__dut.prep(f"{self.interface}_rid", [0])
                    self.__dut.prep(f"{self.interface}_rlast", [0])
                    self.__dut.prep(f"{self.interface}_rvalid", [0])
                else:
                    beat = 0
                    if int(8 * address / self.data_width) + beat_nb in self.ram:
                        beat = self.ram[int(8 * address / self.data_width) + beat_nb]

                    beat_nb += 1
                    self.__dut.prep(f"{self.interface}_rdata", vpw.pack(self.data_width, beat))
                    self.__dut.prep(f"{self.interface}_rid", [read_id])
                    self.__dut.prep(f"{self.interface}_rlast", [int(length == beat_nb)])
                    self.__dut.prep(f"{self.interface}_rvalid", [1])

            if beat_nb == 0 and not self.queue_ar.empty():
                beat_nb = 1
                burst = self.queue_ar.get()
                address = burst["araddr"]
                length = burst["arlen"] + 1
                read_id = burst["arid"]

                beat = 0
                if int(8 * address / self.data_width) + beat_nb - 1 in self.ram:
                    beat = self.ram[int(8 * address / self.data_width) + beat_nb - 1]

                self.__dut.prep(f"{self.interface}_rdata", vpw.pack(self.data_width, beat))
                self.__dut.prep(f"{self.interface}_rid", [read_id])
                self.__dut.prep(f"{self.interface}_rlast", [int(length == beat_nb)])
                self.__dut.prep(f"{self.interface}_rvalid", [1])

    def __ar(self) -> Generator:

        # setup
        self.__dut.prep(f"{self.interface}_arready", [1])

        while True:
            io = yield

            if io[f"{self.interface}_arready"] and io[f"{self.interface}_arvalid"]:
                self.queue_ar.put({"araddr": io[f"{self.interface}_araddr"],
                                   "arlen": io[f"{self.interface}_arlen"],
                                   "arid": io[f"{self.interface}_arid"]})

            if self.queue_ar.full():
                self.__dut.prep(f"{self.interface}_arready", [0])
            else:
                self.__dut.prep(f"{self.interface}_arready", [1])

    def init(self, dut: ModuleType) -> Generator:
        self.__dut: ModuleType = dut

        ch_w = self.__w()
        ch_aw = self.__aw()
        ch_r = self.__r()
        ch_ar = self.__ar()

        next(ch_w)
        next(ch_aw)
        next(ch_r)
        next(ch_ar)

        while True:
            io = yield

            ch_w.send(io)
            ch_aw.send(io)
            ch_r.send(io)
            ch_ar.send(io)
