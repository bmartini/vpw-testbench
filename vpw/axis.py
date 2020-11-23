"""
AXIS Slave and Master Interface
"""

from typing import Generator

class master:
    queue = []

    def __init__(self, interface: str, data_width: int):
        self.interface = interface
        self.data_width = data_width

    def send(self, data):
        # Pass in a list of data to send, one element per beat. The dat is
        # append to the queue and the queue is used as the source of data that
        # gets passed in.
        return

    def init(self, dut):
        self.dut = dut

        dut.prep(f"{self.interface}data", [0])
        dut.prep(f"{self.interface}last", [0])
        dut.prep(f"{self.interface}valid", [0])
        yield

        for x in range(10):
            dut.prep(f"{self.interface}data", [x + 1])
            dut.prep(f"{self.interface}last", [x == 9])
            dut.prep(f"{self.interface}valid", [1])

            io = yield
            while io[f"{self.interface}ready"] == 0:
                io = yield

        dut.prep(f"{self.interface}data", [0])
        dut.prep(f"{self.interface}last", [0])
        dut.prep(f"{self.interface}valid", [0])

        while True:
            yield


class slave:
    queue = []

    def __init__(self, interface: str, data_width: int):
        self.interface = interface
        self.data_width = data_width

    def recv(self, number):
        print(f"{self.interface}data")
        print(f"{self.interface}valid")
        print(f"{self.interface}last")
        print(f"{self.interface}ready")

    def init(self, dut):
        self.dut = dut

        dut.prep(f"{self.interface}ready", [1])
        io = yield

        while True:
            if io[f"{self.interface}valid"] and io[f"{self.interface}ready"]:
                print(io[f"{self.interface}data"])

            io = yield
