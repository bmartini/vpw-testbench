"""
AXIM Master Interface
"""

from collections import deque
from math import ceil
from types import ModuleType
from typing import Any, Callable, Deque, Dict, Generator, List, Union

import vpw


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

    def _unpack(self, val: Union[int, List[int]]) -> int:
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

    def _w(self) -> Generator:

        self._dut.prep(f"{self.interface}_wstrb", [(1 << int(self.data_width/8) - 1)])

        while True:
            if not self.queue_w:
                self._dut.prep(f"{self.interface}_wdata", vpw.pack(self.data_width, 0))
                self._dut.prep(f"{self.interface}_wlast", [0])
                self._dut.prep(f"{self.interface}_wvalid", [0])
                io = yield
            else:
                # access current burst of data to be sent
                burst_data: List[int] = self.queue_w[0]
                burst_nb: int = len(burst_data)

                for i, data in enumerate(burst_data):
                    self._dut.prep(f"{self.interface}_wdata", vpw.pack(self.data_width, data))
                    self._dut.prep(f"{self.interface}_wlast", [int((i+1) == burst_nb)])
                    self._dut.prep(f"{self.interface}_wvalid", [1])

                    io = yield
                    while io[f"{self.interface}_wready"] == 0:
                        io = yield

                self.queue_w.popleft()

    def _aw(self) -> Generator:

        self._dut.prep(f"{self.interface}_awcache", [0])  # NON_CACHE_NON_BUFFER
        self._dut.prep(f"{self.interface}_awqos", [0])  # NOT_QOS_PARTICIPANT
        self._dut.prep(f"{self.interface}_awprot", [0])  # DATA_SECURE_NORMAL
        self._dut.prep(f"{self.interface}_awsize", [int(self.data_width / 8)])  # BYTES PER BEAT
        self._dut.prep(f"{self.interface}_awburst", [1])  # INCREMENTING

        while True:
            if not self.queue_aw:
                self._dut.prep(f"{self.interface}_awaddr", [0])
                self._dut.prep(f"{self.interface}_awlen", [0])
                self._dut.prep(f"{self.interface}_awid", [0])
                self._dut.prep(f"{self.interface}_awvalid", [0])
                io = yield
            else:
                current_aw: Dict[str, Any] = self.queue_aw[0]

                self._dut.prep(f"{self.interface}_awaddr", [current_aw["awaddr"]])
                self._dut.prep(f"{self.interface}_awlen", [current_aw["awlen"]])
                self._dut.prep(f"{self.interface}_awid", [current_aw["awid"]])
                self._dut.prep(f"{self.interface}_awvalid", [1])

                io = yield
                while io[f"{self.interface}_awready"] == 0:
                    io = yield

                self.queue_aw.popleft()

    def _r(self) -> Generator:
        burst_id: int = 0

        # store current burst of data being received
        burst_data: List[int] = []

        # setup
        self._dut.prep(f"{self.interface}_rready", [1])

        while True:
            io = yield

            if io[f"{self.interface}_rready"] and io[f"{self.interface}_rvalid"]:
                data = vpw.unpack(self.data_width, io[f"{self.interface}_rdata"])
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

    def _ar(self) -> Generator:

        while True:
            if not self.queue_ar:
                self._dut.prep(f"{self.interface}_araddr", [0])
                self._dut.prep(f"{self.interface}_arlen", [0])
                self._dut.prep(f"{self.interface}_arid", [0])
                self._dut.prep(f"{self.interface}_arvalid", [0])
                io = yield
            else:
                current_ar: Dict[str, Any] = self.queue_ar[0]

                self._dut.prep(f"{self.interface}_araddr", [current_ar["araddr"]])
                self._dut.prep(f"{self.interface}_arlen", [current_ar["arlen"]])
                self._dut.prep(f"{self.interface}_arid", [current_ar["arid"]])
                self._dut.prep(f"{self.interface}_arvalid", [1])

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
        self.queue_aw.append({"awaddr": int(addr),
                              "awlen": int(len(burst) - 1),
                              "awid": int(write_id)})

    def send_read(self, addr: int, length: int, read_id: int = 0) -> None:
        """
        Non-Blocking: Queue a burst address to send, the address is in bytes
        but must be AXIM word aligned. The length must respect the 4KB
        boundaries as per the AXI spec and be less than 256 beats in length.
        """
        assert(((8 * addr) % self.data_width) == 0)
        assert(((addr % 4096) + int(length * self.data_width / 8)) <= 4096)
        assert(length <= 256)
        self.queue_ar.append({"araddr": int(addr),
                              "arlen": int(length - 1),
                              "arid": int(read_id)})

    def recv_read(self, read_id: int = 0) -> List[int]:
        """
        Non-Blocking: Returns a burst of received data contained in a list, one
        beat per list element.
        """
        if not self.queue_r[read_id]:
            return []
        else:
            return self.queue_r[read_id].popleft()

    def write(self, tick: Callable, address: int, data: List[int], tag: int = 0) -> None:
        """Blocking function to send (write) an array of data over the AXIM.

        Args:
            tick: Function called to progress the clock some period of time.
            address: Absolute address in bytes.
            data: List of data to send with one element per beat.
            tag: Optional burst ID used to identify a transaction.
        """
        # size of data array in bytes
        size = int(self.data_width * len(data) / 8)

        # queue write requests
        burst_address = address
        burst_size = 0
        beat_addr = 0
        beat_size = 0

        while (burst_address + burst_size) < (address + size):
            # calculate the start address of current burst as being the after previous burst
            burst_address = burst_address + burst_size

            # limit the burst size to 4KB or less by first calculating the number of bytes to the next
            # 4KB boundary and comparing it to the remainder of the array to be read
            burst_size = min(int(4096 - (burst_address % 4096)), int(address + size - burst_address))

            beat_addr = beat_addr + beat_size
            beat_size = ceil(8 * burst_size / self.data_width)

            self.send_write(burst_address, data[beat_addr:beat_addr + beat_size], tag)

        # wait until all write data has been sent
        while self.queue_w:
            tick()

    def read(self, tick: Callable, address: int, size: int, tag: int = 0) -> List[int]:
        """Blocking function to request (read) an array of data from over the AXIM.

        Args:
            tick: Function called to progress the clock some period of time.
            address: Absolute address in bytes.
            size: Data size in bytes.
            tag: Optional burst ID used to identify a transaction.
        Return:
            List of data read from the module with one element per beat.
        """
        # queue read requests
        burst_address = address
        burst_size = 0

        while (burst_address + burst_size) < (address + size):
            # calculate the start address of current burst as being the after previous burst
            burst_address = burst_address + burst_size

            # limit the burst size to 4KB or less by first calculating the number of bytes to the next
            # 4KB boundary and comparing it to the remainder of the array to the read
            burst_size = min(int(4096 - (burst_address % 4096)), int(address + size - burst_address))

            # limit burst length to 256 beats or less
            burst_size = int(self.data_width * min(int(8 * burst_size / self.data_width), 256) / 8)

            self.send_read(burst_address, int(8 * burst_size / self.data_width), tag)

        # collect all read bursts resulting from the queued requests
        data_target = ceil(8 * size / self.data_width)
        data: List[int] = []
        while len(data) < data_target:
            tick()
            data = data + self.recv_read(tag)

        return data

    def init(self, dut: ModuleType) -> Generator:
        self._dut: ModuleType = dut

        ch_w = self._w()
        ch_aw = self._aw()
        ch_r = self._r()
        ch_ar = self._ar()

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
