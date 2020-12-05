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
    queue: Deque[List[int]] = deque()
    current: List[int] = []
    pending: int = 0

    def __init__(self, interface: str, data_width: int) -> None:
        self.interface = interface
        self.data_width = data_width

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

        # setup
        dut.prep(f"{self.interface}_tdata", [0])
        dut.prep(f"{self.interface}_tlast", [0])
        dut.prep(f"{self.interface}_tvalid", [0])
        yield

        while True:
            if not self.queue:
                dut.prep(f"{self.interface}_tdata", [0])
                dut.prep(f"{self.interface}_tlast", [0])
                dut.prep(f"{self.interface}_tvalid", [0])

                io = yield
            else:
                self.current = self.queue.popleft()

                for i, val in enumerate(self.current):
                    dut.prep(f"{self.interface}_tdata", self.__pack(val))
                    dut.prep(f"{self.interface}_tlast", [int((i+1) == len(self.current))])
                    dut.prep(f"{self.interface}_tvalid", [1])

                    io = yield
                    while io[f"{self.interface}_tready"] == 0:
                        io = yield

                    self.pending -= 1

                self.current = []


class Slave:
    queue: Deque[List[int]] = deque()
    current: List[int] = []
    pending: int = 0

    def __init__(self, interface: str, data_width: int) -> None:
        self.interface = interface
        self.data_width = data_width

    def __unpack(self, val: Union[int, List[int]]) -> int:
        if isinstance(val, int):
            assert(self.data_width <= 64)
            return val
        else:
            start = ceil(self.data_width/32)
            shift = [32*s for s in range(start)]
            number: int = 0
            for v, s in zip(val, shift):
                number = number | (v << s)

            return number

    def ready(self, active: bool) -> None:
        """ Turn on/off AXIS ready signal. """
        self.__dut.prep(f"{self.interface}_tready", [int(active)])

    def recv(self) -> Optional[List[int]]:
        """ Returns a list of data recived, one element per beat. """
        if not self.queue:
            return None
        else:
            stream: List[int] = self.queue.popleft()
            self.pending -= len(stream)
            return stream

    def init(self, dut) -> Generator:
        self.__dut = dut

        # setup
        dut.prep(f"{self.interface}_tready", [0])

        while True:
            io = yield

            if io[f"{self.interface}_tvalid"] and io[f"{self.interface}_tready"]:
                self.current.append(self.__unpack(io[f"{self.interface}_tdata"]))
                self.pending += 1
                if io[f"{self.interface}_tlast"]:
                    self.queue.append(list(self.current))
                    self.current = []
