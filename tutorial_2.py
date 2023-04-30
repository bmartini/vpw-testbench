#!/usr/bin/env python3
"""
Tutorial 2 testbench
"""

import random
from collections import deque
from types import ModuleType
from typing import Deque, Generator, List

import vpw


class Checker:
    def __init__(self, interface: str, data_width: int, reset: str) -> None:
        self.interface = interface
        self.data_width = data_width
        self.reset = reset

    def init(self, dut: ModuleType) -> Generator:

        io = yield
        past_data: int = vpw.unpack(self.data_width, io[f"{self.interface}_tdata"])
        past_last: bool = bool(io[f"{self.interface}_tlast"])
        past_valid: bool = bool(io[f"{self.interface}_tvalid"])
        past_ready: bool = bool(io[f"{self.interface}_tready"])
        past_reset: bool = bool(io[f"{self.reset}"])

        while True:

            io = yield
            current_data: int = vpw.unpack(self.data_width, io[f"{self.interface}_tdata"])
            current_last: bool = io[f"{self.interface}_tlast"]
            current_valid: bool = io[f"{self.interface}_tvalid"]
            current_ready: bool = io[f"{self.interface}_tready"]
            current_reset: bool = io[f"{self.reset}"]

            # data steady when stalled
            if past_valid & ~past_ready:
                assert (past_data == current_data), \
                       f"{self.interface}_tdata value changed when when stalled"

            # only lower valid after a transaction
            if ~past_reset & (past_valid & ~current_valid):
                assert past_ready, \
                       f"{self.interface}_tvalid going low was not after a transaction"

            # only lower last after a transaction
            if ~past_reset & (past_last & ~current_last):
                assert (past_ready & past_valid), \
                       f"{self.interface}_tlast going low was not after a transaction"

            # last only high when valid is high
            if current_last:
                assert current_valid, \
                       f"{self.interface}_tlast can only be high when tvalid is high"

            # only lower ready after a transaction
            if ~past_reset & (past_ready & ~current_ready):
                assert past_valid, \
                       f"{self.interface}_tready going low was not after a transaction"

            past_data = current_data
            past_last = current_last
            past_valid = current_valid
            past_ready = current_ready
            past_reset = current_reset


class Master:
    def __init__(self, interface: str, data_width: int) -> None:
        self.interface = interface
        self.data_width = data_width

        self.queue: Deque[List[int]] = deque()
        self.current: List[int] = []
        self.pending: int = 0

    def send(self, data: List[int]) -> None:
        """ Pass in a list of data to send, one element per beat. """
        self.queue.append(data)
        self.pending += len(data)

    def init(self, dut: ModuleType) -> Generator:

        while True:
            if not self.queue:
                dut.prep(f"{self.interface}_tdata", vpw.pack(self.data_width, 0))
                dut.prep(f"{self.interface}_tlast", [0])
                dut.prep(f"{self.interface}_tvalid", [0])

                io = yield
            else:
                self.current = self.queue[0]

                for i, val in enumerate(self.current):
                    dut.prep(f"{self.interface}_tdata", vpw.pack(self.data_width, val))
                    dut.prep(f"{self.interface}_tlast", [int((i+1) == len(self.current))])
                    dut.prep(f"{self.interface}_tvalid", [1])

                    io = yield
                    while io[f"{self.interface}_tready"] == 0:
                        io = yield

                    self.pending -= 1

                self.queue.popleft()


class Slave:
    def __init__(self, interface: str, data_width: int) -> None:
        self.interface = interface
        self.data_width = data_width

        self.queue: Deque[List[int]] = deque()
        self.current: List[int] = []
        self.pending: int = 0

    def ready(self, active: bool) -> None:
        """ Turn on/off AXIS ready signal. """
        self.__dut.prep(f"{self.interface}_tready", [int(active)])

    def recv(self) -> List[int]:
        """ Returns a list of data received, one element per beat. """
        if not self.queue:
            return []
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
                self.current.append(vpw.unpack(self.data_width, io[f"{self.interface}_tdata"]))
                self.pending += 1
                if io[f"{self.interface}_tlast"]:
                    self.queue.append(list(self.current))
                    self.current = []


if __name__ == '__main__':

    dut = vpw.create(package='tutorial_2',
                     module='skid_buffer',
                     clock='clk',
                     parameter={'DATA_WIDTH': 64})

    vpw.init(dut)

    up_stream = Master("up", 64)
    vpw.register(up_stream)
    vpw.register(Checker("up", 64, "rst"))

    dn_stream = Slave("dn", 64)
    vpw.register(dn_stream)
    vpw.register(Checker("dn", 64, "rst"))

    # send reset to the DUT
    vpw.idle(2)
    vpw.prep("rst", [1])
    vpw.idle(2)
    vpw.prep("rst", [0])
    vpw.idle(2)

    # create a data stream to send into module
    data = [n+1 for n in range(16)]
    up_stream.send(data)

    # randomly apply tready values to downstream interface to test intermittent streams
    while up_stream.pending > 0:
        io = vpw.tick()
        if bool(io["dn_tvalid"]):
            dn_stream.ready(bool(random.getrandbits(1)))
        elif not bool(io["dn_tready"]):
            dn_stream.ready(bool(random.getrandbits(1)))

    dn_stream.ready(True)
    vpw.idle(10)

    # test that data sent and results received match
    result = dn_stream.recv()
    for d, r in zip(data, result):
        assert (d == r), f"data sent '{d}' and result received '{r}' do not match"

    print(data)
    print(result)
    print("\nPASS: Data sent and result received match\n")

    vpw.finish()
