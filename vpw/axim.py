"""
AXIM Master Interface
"""

from typing import Generator
from typing import Optional
from typing import Union
from typing import Deque
from typing import List
from typing import Dict
from typing import Any

from math import ceil
from collections import deque


class Master:
    def __init__(self, interface: str, data_width: int, addr_width: int) -> None:
        assert((data_width % 8) == 0)
        assert(addr_width <= 64)
        self.interface = interface
        self.data_width = data_width
        self.addr_width = addr_width

        # write data channel
        self.queue_w: Deque[List[int]] = deque()

        # write address channel
        self.queue_aw: Deque[Dict[str, Any]] = deque()

        # read data channel, queues contained in list addressable via (A)RID
        self.queue_r: List[Deque[List[int]]] = [deque() for _ in range(16)]

        # read address channel
        self.queue_ar: Deque[Dict[str, Any]] = deque()

        # keep track of lengths of requested read bursts, list addressable via (A)RID
        self.pending_ar: List[Deque[int]] = [deque() for _ in range(16)]

    def __pack(self, val: int) -> List[int]:
        if self.data_width <= 64:
            return [val]
        else:
            start = ceil(self.data_width / 32)
            shift = [32*s for s in range(start)]
            return [((val >> s) & 0xffffffff) for s in shift]

    def __unpack(self, val: Union[int, List[int]]) -> int:
        if isinstance(val, int):
            assert(self.data_width <= 64)
            return val
        else:
            start = ceil(self.data_width / 32)
            shift = [32*s for s in range(start)]
            number: int = 0
            for v, s in zip(val, shift):
                number = number | (v << s)

            return number

    def __w(self) -> Generator:

        self.__dut.prep(f"{self.interface}_wstrb", [(1 << int(self.data_width/8) - 1)])

        while True:
            if not self.queue_w:
                self.__dut.prep(f"{self.interface}_wdata", [0])
                self.__dut.prep(f"{self.interface}_wlast", [0])
                self.__dut.prep(f"{self.interface}_wvalid", [0])
                io = yield
            else:
                # access current burst of data to be sent
                burst_data: List[int] = self.queue_w[0]
                burst_nb: int = len(burst_data)

                for i, data in enumerate(burst_data):
                    self.__dut.prep(f"{self.interface}_wdata", self.__pack(data))
                    self.__dut.prep(f"{self.interface}_wlast", [int((i+1) == burst_nb)])
                    self.__dut.prep(f"{self.interface}_wvalid", [1])

                    io = yield
                    while io[f"{self.interface}_wready"] == 0:
                        io = yield

                self.queue_w.popleft()

    def __aw(self) -> Generator:

        self.__dut.prep(f"{self.interface}_awcache", [0])  # NON_CACHE_NON_BUFFER
        self.__dut.prep(f"{self.interface}_awqos", [0])  # NOT_QOS_PARTICIPANT
        self.__dut.prep(f"{self.interface}_awprot", [0])  # DATA_SECURE_NORMAL
        self.__dut.prep(f"{self.interface}_awsize", [int(self.data_width / 8)])  # BYTES PER BEAT
        self.__dut.prep(f"{self.interface}_awburst", [1])  # INCREMENTING

        while True:
            if not self.queue_aw:
                self.__dut.prep(f"{self.interface}_awaddr", [0])
                self.__dut.prep(f"{self.interface}_awlen", [0])
                self.__dut.prep(f"{self.interface}_awid", [0])
                self.__dut.prep(f"{self.interface}_awvalid", [0])
                io = yield
            else:
                current_aw: Dict[str, Any] = self.queue_aw[0]

                self.__dut.prep(f"{self.interface}_awaddr", [current_aw["awaddr"]])
                self.__dut.prep(f"{self.interface}_awlen", [current_aw["awlen"]])
                self.__dut.prep(f"{self.interface}_awid", [current_aw["awid"]])
                self.__dut.prep(f"{self.interface}_awvalid", [1])

                io = yield
                while io[f"{self.interface}_awready"] == 0:
                    io = yield

                self.queue_aw.popleft()

    def __r(self) -> Generator:
        burst_id: int = 0

        # store current burst of data being received
        burst_data: List[int] = []

        # setup
        self.__dut.prep(f"{self.interface}_rready", [1])

        while True:
            io = yield

            if io[f"{self.interface}_rready"] and io[f"{self.interface}_rvalid"]:
                data = self.__unpack(io[f"{self.interface}_rdata"])
                burst_data.append(data)

                if len(burst_data) == 1:
                    # first beat of a burst
                    burst_id = io[f"{self.interface}_rid"]

                    # check that there exists a pending read with the same ID
                    assert(self.pending_ar[burst_id])
                else:
                    # check that beat ID is consistent with the bursts
                    assert(burst_id == io[f"{self.interface}_rid"])

                if io[f"{self.interface}_rlast"]:
                    # check that received burst is the length requested
                    assert(self.pending_ar[burst_id][0] == len(burst_data))

                    self.queue_r[burst_id].append(burst_data)
                    self.pending_ar[burst_id].popleft()
                    burst_data = []

    def __ar(self) -> Generator:

        while True:
            if not self.queue_ar:
                self.__dut.prep(f"{self.interface}_araddr", [0])
                self.__dut.prep(f"{self.interface}_arlen", [0])
                self.__dut.prep(f"{self.interface}_arid", [0])
                self.__dut.prep(f"{self.interface}_arvalid", [0])
                io = yield
            else:
                current_ar: Dict[str, Any] = self.queue_ar[0]

                self.__dut.prep(f"{self.interface}_araddr", [current_ar["araddr"]])
                self.__dut.prep(f"{self.interface}_arlen", [current_ar["arlen"]])
                self.__dut.prep(f"{self.interface}_arid", [current_ar["arid"]])
                self.__dut.prep(f"{self.interface}_arvalid", [1])

                io = yield
                while io[f"{self.interface}_arready"] == 0:
                    io = yield

                self.pending_ar[current_ar["arid"]].append(current_ar["arlen"] + 1)
                self.queue_ar.popleft()

    def send_write(self, addr: int, burst: List[int], write_id: int = 0) -> None:
        """
        Non-Blocking: Queue to send an addressed burst of data, the address is
        in bytes but must be AXIM beat aligned. The burst has one beat per
        element and its length must respect the 4KB boundaries as per the AXI
        spec and be less than 256 beats in length.
        """
        assert((addr % self.data_width) == 0)
        assert(((addr % 4096) + int(len(burst) * self.data_width / 8)) <= 4096)
        assert(len(burst) <= 256)
        self.queue_w.append(burst)
        self.queue_aw.append({"awaddr": addr, "awlen": len(burst) - 1, "awid": write_id})

    def send_read(self, addr: int, length: int, read_id: int = 0) -> None:
        """
        Non-Blocking: Queue a burst address to send, the address is in bytes
        but must be AXIM word aligned. The length must respect the 4KB
        boundaries as per the AXI spec and be less than 256 beats in length.
        """
        assert(((8 * addr) % self.data_width) == 0)
        assert(((addr % 4096) + int(length * self.data_width / 8)) <= 4096)
        assert(length <= 256)
        self.queue_ar.append({"araddr": addr,
                              "arlen": length - 1,
                              "arid": read_id})

    def recv_read(self, read_id: int = 0) -> Optional[List[int]]:
        """
        Non-Blocking: Returns a burst of received data contained in a list, one
        beat per list element.
        """
        if not self.queue_r[read_id]:
            return None
        else:
            return self.queue_r[read_id].popleft()

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

        while True:
            io = yield

            ch_w.send(io)
            ch_aw.send(io)
            ch_r.send(io)
            ch_ar.send(io)
