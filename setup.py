#!/usr/bin/env python3

from setuptools import setup

setup(
    name = "vpw-testbench",
    version = "1",
    author = "Berin Martini",
    author_email = "berin.martini@gmail.com",
    description = ("Verilator Python Wrapper and testbench framework"),
    license = "MIT",
    keywords = "verilator",
    url = "https://github.com/bmartini/vpw-testbench",
    packages=["vpw"],
    package_data = {
        "vpw": ["testbench.hh"],
    },
    install_requires = [
        "typing",
        "parsy",
        "pybind11"
    ],
)
