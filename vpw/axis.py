"""
AXIS Slave and Master Interface
"""

from typing import Generator

class master:

    def __init__(self, interface: str, data_width: int):
        self.interface = interface
        self.data_width = data_width

    def send(self, number):
        print(f"{self.interface}data")
        print(f"{self.interface}valid")
        print(f"{self.interface}last")
        print(f"{self.interface}ready")

    def init(self, dut):
        self.dut = dut

        # create and return a generator

        return


class slave:

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

        print(f"{self.interface}data")
        print(f"{self.interface}valid")
        print(f"{self.interface}last")
        print(f"{self.interface}ready")

        return
