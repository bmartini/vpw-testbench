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
        self._concat = concat

        self.queue: List[Deque[List[int]]] = [deque() for _ in range(concat)]
        self.current: List[List[int]] = [[] for _ in range(concat)]
        self.pending: List[int] = [0] * concat
        self._pause: List[bool] = [False] * concat

        # create sub-tasks
        self._data = vpw.Slice(f"{interface}_tdata", data_width, concat)
        self._last = vpw.Slice(f"{interface}_tlast", 1, concat)
        self._valid = vpw.Slice(f"{interface}_tvalid", 1, concat)
        self._ready = vpw.Slice(f"{interface}_tready", 1, concat)

    def pause(self, active: bool, position: int = 0) -> None:
        """ Turn on/off AXIS valid signal. """
        self._pause[position] = active

    def send(self, data: List[int], position: int = 0) -> None:
        """ Pass in a list of data to send, one element per beat. """
        self.queue[position].append(data)
        self.pending[position] += len(data)

    def _section(self, position: int = 0) -> Generator:
        while True:
            self._data[position] = 0
            self._last[position] = 0
            self._valid[position] = 0

            if not self.queue[position]:
                yield
            else:
                self.current[position] = self.queue[position][0]

                for i, val in enumerate(self.current[position], start=1):
                    self._data[position] = val
                    self._last[position] = int(i == len(self.current[position]))
                    self._valid[position] = int(not self._pause[position])

                    yield
                    while self._valid[position] == 0 or self._ready[position] == 0:
                        self._valid[position] = int(not self._pause[position])
                        yield

                    self.pending[position] -= 1

                self.queue[position].popleft()

    def init(self, dut: ModuleType) -> Generator:

        # init sub-tasks
        ports = []
        ports.append(self._data.init(dut))
        ports.append(self._last.init(dut))
        ports.append(self._valid.init(dut))
        ports.append(self._ready.init(dut))
        for port in ports:
            next(port)

        streams = []
        for pos in range(self._concat):
            streams.append(self._section(pos))
            next(streams[pos])

        while True:
            io = yield

            # update sub-tasks
            for port in ports:
                port.send(io)

            for stream in streams:
                next(stream)


class Slave:
    def __init__(self, interface: str, data_width: int, concat: int = 1) -> None:
        assert(concat > 0)
        self._concat = concat

        self.queue: List[Deque[List[int]]] = [deque() for _ in range(concat)]
        self.current: List[List[int]] = [[] for _ in range(concat)]
        self.pending: List[int] = [0] * concat

        # create sub-tasks
        self._data = vpw.Slice(f"{interface}_tdata", data_width, concat)
        self._last = vpw.Slice(f"{interface}_tlast", 1, concat)
        self._valid = vpw.Slice(f"{interface}_tvalid", 1, concat)
        self._ready = vpw.Slice(f"{interface}_tready", 1, concat)

    def ready(self, active: bool, position: int = 0) -> None:
        """ Turn on/off AXIS ready signal. """
        self._ready[position] = int(active)

    def recv(self, position: int = 0) -> List[int]:
        """ Returns a list of data recived, one element per beat. """
        if not self.queue[position]:
            return []
        else:
            stream: List[int] = self.queue[position].popleft()
            self.pending[position] -= len(stream)
            return stream

    def init(self, dut: ModuleType) -> Generator:
        # setup
        for pos in range(self._concat):
            self._ready[pos] = 0

        # init sub-tasks
        ports = []
        ports.append(self._data.init(dut))
        ports.append(self._last.init(dut))
        ports.append(self._valid.init(dut))
        ports.append(self._ready.init(dut))
        for port in ports:
            next(port)

        while True:
            io = yield

            # update sub-tasks
            for port in ports:
                port.send(io)

            for pos in range(self._concat):
                if self._valid[pos] and self._ready[pos]:
                    self.current[pos].append(self._data[pos])
                    self.pending[pos] += 1

                    if self._last[pos]:
                        self.queue[pos].append(list(self.current[pos]))
                        self.current[pos] = []
