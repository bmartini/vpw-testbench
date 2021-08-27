#!/usr/bin/env python3

from typing import Dict
from typing import Tuple

from parsy import seq  # type: ignore
from parsy import regex  # type: ignore
from parsy import string  # type: ignore
from parsy import ParseError  # type: ignore

import click
import re
import subprocess
import sys


def generate_intro(name: str) -> str:
    return f'#include "V{name}.h"\n' \
           f'#include "verilated.h"\n' \
           f'#include "verilated_vcd_c.h"\n' \
           f'\n' \
           f'typedef V{name} TB;\n' \
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
               f'  for (auto &item : dut->{port}) {"{"}\n' \
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


def create_cpp(name: str, ports: Dict[str, str]) -> str:
    body = ''

    body += generate_intro(name)

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


def parse_header(name: str, clock: str) -> Tuple[str, Dict[str, str]]:
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

    with open(f'obj_dir/V{name}.h', 'r') as f:
        lines = f.readlines()

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
        print("Clock signal '{}' not in portlist: ".format(clock), portlist.keys(), file=sys.stderr)

    return name, portlist


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option('-c', '--clock', default='clk', help='Clock name of top module.')
@click.option('-n', '--name', default='example', help='Name of top module.')
def main(name: str, clock: str):

    subprocess.run([f'make', f'clean']),
    subprocess.run([f'make', f'TOP={name}', f'obj_dir/V{name}.cpp'])

    code = create_cpp(*parse_header(name, clock))

    with open(f'obj_dir/{name}.cc', 'w') as f:
        f.write(code)

    subprocess.run([f'make', f'TOP={name}', f'CLOCK={clock}'])


if __name__ == '__main__':
    main()
