"""
AXIS Slave and Master Interface
"""

import vpw

from typing import Deque
from typing import Generator
from typing import List
from types import ModuleType

from collections import deque


class Master:
    def __init__(self, interface: str, data_width: int, concat: int = 1) -> None:
        assert(concat > 0)
        self.interface = interface
        self.data_width = data_width
        self.concat = concat

        self.__data = 0
        self.__last = 0
        self.__valid = 0
        self.queue: List[Deque[List[int]]] = [deque() for _ in range(concat)]
        self.current: List[List[int]] = [[] for _ in range(concat)]
        self.pending: List[int] = [0] * concat

    def send(self, data: List[int], position: int = 0) -> None:
        """ Pass in a list of data to send, one element per beat. """
        self.queue[position].append(data)
        self.pending[position] += len(data)

    def __section(self, position: int = 0) -> Generator:

        zero_data = ~(((1 << self.data_width) - 1) << (position * self.data_width))
        zero_flag = ~(1 << position)

        while True:
            if not self.queue[position]:
                self.__data = self.__data & zero_data
                self.__last = self.__last & zero_flag
                self.__valid = self.__valid & zero_flag

                self.__dut.prep(f"{self.interface}_tdata", [self.__data])
                self.__dut.prep(f"{self.interface}_tlast", [self.__last])
                self.__dut.prep(f"{self.interface}_tvalid", [self.__valid])

                io = yield
            else:
                self.current[position] = self.queue[position][0]

                for i, val in enumerate(self.current[position], start=1):
                    self.__data = self.__data & zero_data
                    self.__data = self.__data | (val << (position * self.data_width))

                    last = int(i == len(self.current[position]))
                    self.__last = self.__last & zero_flag
                    self.__last = self.__last | (last << position)

                    self.__valid = self.__valid | (1 << position)

                    self.__dut.prep(f"{self.interface}_tdata",
                                    vpw.pack((self.concat * self.data_width), self.__data))
                    self.__dut.prep(f"{self.interface}_tlast", [self.__last])
                    self.__dut.prep(f"{self.interface}_tvalid", [self.__valid])

                    io = yield
                    while (io[f"{self.interface}_tready"] & ~zero_flag) == 0:
                        io = yield

                    self.pending[position] -= 1

                self.queue[position].popleft()

    def init(self, dut: ModuleType) -> Generator:
        self.__dut: ModuleType = dut
        streams = []

        for pos in range(self.concat):
            streams.append(self.__section(pos))
            next(streams[pos])

        while True:
            io = yield

            for stream in streams:
                stream.send(io)


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

    def ready(self, active: bool, position: int = 0) -> None:
        """ Turn on/off AXIS ready signal. """
        if active:
            self.__ready = self.__ready | (1 << position)
        else:
            self.__ready = self.__ready & ~(1 << position)

        self.__dut.prep(f"{self.interface}_tready", [self.__ready])

    def recv(self, position: int = 0) -> List[int]:
        """ Returns a list of data recived, one element per beat. """
        if not self.queue[position]:
            return []
        else:
            stream: List[int] = self.queue[position].popleft()
            self.pending[position] -= len(stream)
            return stream

    def init(self, dut: ModuleType) -> Generator:
        self.__dut: ModuleType = dut

        # setup
        self.__dut.prep(f"{self.interface}_tready", [0])
        mask = (1 << self.data_width) - 1

        while True:
            io = yield

            io_data = vpw.unpack((self.concat * self.data_width),
                                 io[f"{self.interface}_tdata"])
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
