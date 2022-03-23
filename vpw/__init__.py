"""
Verilator Python Wrapper Package
"""

from typing import Optional
from typing import Union
from typing import List
from typing import Dict
from typing import Tuple
from typing import Any
from typing import TextIO
from types import ModuleType

from parsy import seq  # type: ignore
from parsy import regex  # type: ignore
from parsy import string  # type: ignore
from parsy import ParseError  # type: ignore

from math import ceil
from subprocess import PIPE

import re
import os
import sys
import importlib
import subprocess

# Maintains persistent background tasks in the form of a list of generators
# that get incremented every clock cycle.
background = []

# Design Under Test
dut: ModuleType


def init(testbench: ModuleType, trace: bool = True):
    global dut
    dut = testbench
    dut.init(trace)


def prep(port: str, value: List[int]):
    global dut
    dut.prep(port, value)


def pack(data_width: int, val: int) -> List[int]:
    if data_width <= 64:
        return [val]
    else:
        start = ceil(data_width / 32)
        shift = [32*s for s in range(start)]
        return [((val >> s) & 0xffffffff) for s in shift]


def unpack(data_width: int, val: Union[int, List[int]]) -> int:
    if isinstance(val, int):
        assert(data_width <= 64)
        return val
    else:
        start = ceil(data_width / 32)
        shift = [32*s for s in range(start)]
        number: int = 0
        for v, s in zip(val, shift):
            number = number | (v << s)

        return number


def register(interface):
    """ When an interface is registered with VPW it's first initiated and then
    its generator is run in the background """

    global dut
    gen = interface.init(dut)
    next(gen)

    background.append(gen)


def tick():
    """ Advance TB clock """

    global dut
    io = dut.tick()
    for gen in background:
        try:
            gen.send(io)
        except StopIteration:
            background.remove(gen)

    return io


def idle(time: int = 1):
    """ Idle for a number of clock cycles """

    for _ in range(time):
        tick()


def finish():
    global dut
    dut.finish()


def parse(module: str, clock: str, header: TextIO) -> str:
    """ Parse Verilator module header file and return testbench interface file """

    def generate_intro(module: str) -> str:
        return f'#include "V{module}.h"\n' \
               f'#include "verilated.h"\n' \
               f'#include "verilated_vcd_c.h"\n' \
               f'\n' \
               f'typedef V{module} TB;\n' \
               f'#include "testbench.hh"\n' \
               f'\n' \
               f'\n' \
               f'void prep(const std::string port,' \
               f' const std::vector<uint64_t> &value) {"{"}\n' \
               f'\n' \
               f'  '

    def generate_prep_if(port: str, width: str) -> str:
        if (width != 'IN8' and width != "IN16" and width != "IN32" and
                width != "IN64" and width != "INW"):
            return ''
        else:
            return f'if ("{port}" == port) {"{"}\n'

    def generate_prep_body(port: str, width: str) -> str:
        if width == 'IN8':
            return f'    dut->{port} = static_cast<const uint8_t>(value[0]);\n  {"}"} else '
        elif width == "IN16":
            return f'    dut->{port} = static_cast<const uint16_t>(value[0]);\n  {"}"} else '
        elif width == "IN32":
            return f'    dut->{port} = static_cast<const uint32_t>(value[0]);\n  {"}"} else '
        elif width == "IN64":
            return f'    dut->{port} = static_cast<const uint64_t>(value[0]);\n  {"}"} else '
        elif width == "INW":
            return f'    for (std::size_t i = 0; i != value.size(); ++i) {"{"}\n' \
                   f'       dut->{port}[i] = static_cast<const uint32_t>(value[i]);\n' \
                   f'    {"}"}\n  {"}"} else '
        else:
            return ''

    def generate_update() -> str:
        return f'{"{"}\n' \
               f'    printf("WARNING: requested port \\\'%s\\\' not found.\\n", ' \
               f'port.c_str());\n' \
               f'  {"}"}\n' \
               f'{"}"}\n' \
               f'\n' \
               f'py::dict update() {"{"}\n\n'

    def generate_update_list(port: str, width: str) -> str:
        if width != "INW" and width != "OUTW":
            return ''
        else:
            return f'  py::list {port};\n' \
                   f'  for (auto &item : dut->{port}.m_storage) {"{"}\n' \
                   f'    {port}.append(item);\n' \
                   f'  {"}"}\n\n'

    def generate_update_return() -> str:
        return "  return py::dict ("

    def generate_update_dict(port: str, width: str) -> str:
        if width != "INW" and width != "OUTW":
            return f'    "{port}"_a = dut->{port}'
        else:
            return f'    "{port}"_a = {port}'

    def generate_update_end() -> str:
        return "\n  );\n}\n"

    def create_cpp(module: str, ports: Dict[str, str]) -> str:
        body = ''

        body += generate_intro(module)

        for port, width in ports.items():
            body += generate_prep_if(port, width)
            body += generate_prep_body(port, width)

        body += generate_update()

        for port, width in ports.items():
            body += generate_update_list(port, width)

        body += generate_update_return()

        port = list(ports.keys())[0]
        body += '\n' + generate_update_dict(port, ports[port])
        del ports[port]

        for port, width in ports.items():
            body += ',\n' + generate_update_dict(port, width)

        body += generate_update_end()
        return body

    def parse_header(module: str, clock: str, header: TextIO) \
            -> Tuple[str, Dict[str, str]]:

        in8 = string('    VL_IN8(').map(lambda x: 'IN8')
        in16 = string('    VL_IN16(').map(lambda x: 'IN16')
        in32 = string('    VL_IN(').map(lambda x: 'IN32')
        in64 = string('    VL_IN64(').map(lambda x: 'IN64')
        inw = string('    VL_INW(').map(lambda x: 'INW')

        out8 = string('    VL_OUT8(').map(lambda x: 'OUT8')
        out16 = string('    VL_OUT16(').map(lambda x: 'OUT16')
        out32 = string('    VL_OUT(').map(lambda x: 'OUT32')
        out64 = string('    VL_OUT64(').map(lambda x: 'OUT64')
        outw = string('    VL_OUTW(').map(lambda x: 'OUTW')

        ports = (in8 | in16 | in32 | in64 | inw | out8 | out16
                 | out32 | out64 | outw).desc('variable width definition')

        varname = regex(r'[a-zA-Z_0-9]+').desc('variable name')

        lines = header.readlines()

        portlist = {}
        for line in lines:
            # Collapse differences between different verilator versions
            line = re.sub(r'(\sVL_[A-Z0-9]*)\([\(\&]*([a-zA-Z0-9_]+)\)?,', r'\1(\2,', line)
            try:
                port_def, _ = seq(ports, varname).parse_partial(line)
                portlist[port_def[1]] = port_def[0]
            except ParseError:
                pass

        # remove clock from port list
        if clock in portlist:
            del portlist[clock]
        else:
            print(f"Clock signal '{clock}' not in portlist: ",
                  portlist.keys(), file=sys.stderr)

        return module, portlist

    return create_cpp(*parse_header(module, clock, header))


def create(package: Optional[str] = None, module: str = 'testbench', clock: str = 'clk',
           include: List[str] = ['./hdl'],
           parameter: Optional[Dict[str, Any]] = None,
           define: Optional[Dict[str, Any]] = None) -> ModuleType:

    package = module if package is None else package

    includes: List = []
    for dirs in include:
        includes = includes + [f'-I{dirs}']

    parameters: List = []
    if parameter:
        for macro, value in parameter.items():
            parameters = parameters + [f'-pvalue+{macro}={value}']

    defines: List = []
    if define:
        for macro, value in define.items():
            if value is None:
                defines = defines + [f'+define+{macro}']
            else:
                defines = defines + [f'+define+{macro}={value}']

    def topfile(include: List[str], module: str) -> List[str]:
        filename = [f"{module}.sv"]
        for dirname in include:
            for root, dirs, files in os.walk(dirname):
                if f"{module}.sv" in files:
                    filename = [f"{root}/{module}.sv"]
                if f"{module}.v" in files:
                    filename = [f"{root}/{module}.v"]
        return filename

    # shell out for build information
    verilator_root_rc = subprocess.run(['verilator', '-V'], stdout=PIPE, text=True)
    for line in verilator_root_rc.stdout.splitlines():
        if "VERILATOR_ROOT" in line:
            vinc = f'{line.split()[2]}/include'
            break

    pyinc_rc = subprocess.run(['python3', '-m', 'pybind11', '--includes'], stdout=PIPE, text=True)
    pyinc = list(pyinc_rc.stdout.strip().split(" "))

    output_rc = subprocess.run(['python3-config', '--extension-suffix'], stdout=PIPE, text=True)
    output = f"{package}{output_rc.stdout.strip()}"

    # remove any old build files
    subprocess.run(['rm', '-rf', f'{package}', f'{output}', f"{package}.vcd"])

    # verilate the SV module into C++
    verilate_module = ['verilator', '-Mdir', f'{package}']
    verilate_module = verilate_module + ['-CFLAGS', '-fPIC -std=c++17']
    verilate_module = verilate_module + includes
    verilate_module = verilate_module + ['--trace']
    verilate_module = verilate_module + ['-cc']
    verilate_module = verilate_module + parameters
    verilate_module = verilate_module + defines
    verilate_module = verilate_module + topfile(include, module)
    subprocess.run(verilate_module)

    # create the VPW testbench interface file
    with open(f'{package}/V{module}.h', 'r') as header:
        with open(f'{package}/{module}.cc', 'w') as code:
            code.write(parse(module, clock, header))

    # compile the verilated module into object files
    subprocess.run(['make', '--no-print-directory', '-C', f'{package}', '-f', f'V{module}.mk'])

    # compile the VPW testbench interface file and object files into a library
    compile_package = ['g++', '-O3', '-Wall']
    compile_package = compile_package + ['-D', f'PACKAGE={package}']
    compile_package = compile_package + ['-D', f'CLOCK={clock}']
    compile_package = compile_package + ['-shared']
    compile_package = compile_package + ['-std=c++17']
    compile_package = compile_package + ['-fPIC']
    compile_package = compile_package + pyinc
    compile_package = compile_package + ['-I.', f'-I{vinc}', f'-I{package}']
    compile_package = compile_package + [f'-I{os.path.dirname(__file__)}']
    compile_package = compile_package + [f'{vinc}/verilated.cpp']
    compile_package = compile_package + [f'{vinc}/verilated_vcd_c.cpp']
    compile_package = compile_package + [f'{package}/{module}.cc']
    compile_package = compile_package + [f'{package}/V{module}__ALL.a']
    compile_package = compile_package + ['-o', f'{output}']
    subprocess.run(compile_package)

    return importlib.import_module(package)
