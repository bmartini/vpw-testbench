"""
AXIS Slave and Master Interface
"""

from typing import Generator
from typing import Optional
from typing import Union
from typing import Deque
from typing import List

from math import ceil
from collections import deque


class Master:
    def __init__(self, interface: str, data_width: int) -> None:
        self.interface = interface
        self.data_width = data_width

        self.queue: Deque[List[int]] = deque()
        self.current: List[int] = []
        self.pending: int = 0

    def __pack(self, val: int) -> List[int]:
        if self.data_width <= 64:
            return [val]
        else:
            start = ceil(self.data_width/32)
            shift = [32*s for s in range(start)]
            return [((val >> s) & 0xffffffff) for s in shift]

    def send(self, data: List[int]) -> None:
        """ Pass in a list of data to send, one element per beat. """
        self.queue.append(data)
        self.pending += len(data)

    def init(self, dut) -> Generator:

        while True:
            if not self.queue:
                dut.prep(f"{self.interface}_tdata", [0])
                dut.prep(f"{self.interface}_tlast", [0])
                dut.prep(f"{self.interface}_tvalid", [0])

                io = yield
            else:
                self.current = self.queue[0]

                for i, val in enumerate(self.current):
                    dut.prep(f"{self.interface}_tdata", self.__pack(val))
                    dut.prep(f"{self.interface}_tlast", [int((i+1) == len(self.current))])
                    dut.prep(f"{self.interface}_tvalid", [1])

                    io = yield
                    while io[f"{self.interface}_tready"] == 0:
                        io = yield

                    self.pending -= 1

                self.queue.popleft()


class Slave:
    def __init__(self, interface: str, data_width: int, concat: int = 1) -> None:
        assert(concat > 0)
        self.interface = interface
        self.data_width = data_width
        self.concat = concat

        self.__ready = 0
        self.queue: List[Deque[List[int]]] = [deque() for _ in range(concat)]
        self.current: List[List[int]] = [[] for _ in range(concat)]
        self.pending: List[int] = [0] * concat

    def __unpack(self, val: Union[int, List[int]]) -> int:
        if isinstance(val, int):
            assert((self.concat * self.data_width) <= 64)
            return val
        else:
            start = ceil(self.concat * self.data_width / 32)
            shift = [32*s for s in range(start)]
            number: int = 0
            for v, s in zip(val, shift):
                number = number | (v << s)

            return number

    def ready(self, active: bool, position: int = 0) -> None:
        """ Turn on/off AXIS ready signal. """
        if active:
            self.__ready = self.__ready | (1 << position)
        else:
            self.__ready = self.__ready & ~(1 << position)

        self.__dut.prep(f"{self.interface}_tready", [self.__ready])

    def recv(self, position: int = 0) -> Optional[List[int]]:
        """ Returns a list of data recived, one element per beat. """
        if not self.queue[position]:
            return None
        else:
            stream: List[int] = self.queue[position].popleft()
            self.pending[position] -= len(stream)
            return stream

    def init(self, dut) -> Generator:
        self.__dut = dut

        # setup
        dut.prep(f"{self.interface}_tready", [0])
        mask = (1 << self.data_width) - 1

        while True:
            io = yield

            io_data = self.__unpack(io[f"{self.interface}_tdata"])
            io_last = io[f"{self.interface}_tlast"]
            io_valid = io[f"{self.interface}_tvalid"]
            io_ready = io[f"{self.interface}_tready"]

            for pos in range(self.concat):
                data = (io_data >> (pos * self.data_width)) & mask
                last = (io_last >> pos) & 1
                valid = (io_valid >> pos) & 1
                ready = (io_ready >> pos) & 1

                if valid and ready:
                    self.current[pos].append(data)
                    self.pending[pos] += 1

                    if last:
                        self.queue[pos].append(list(self.current[pos]))
                        self.current[pos] = []
