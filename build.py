#!/usr/bin/env python3

from typing import Dict

# from parsy import regex
from parsy import string  # type: ignore


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
    return "\n  );\n}"


def create_cpp(ports: Dict[str, str]) -> str:
    body = ''

    body += generate_intro('example')

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


with open('obj_dir/Vexample.h', 'r') as f:
    header = f.readlines()

IN8 = string('VL_IN8(')
IN16 = string('VL_IN16(')
IN32 = string('VL_IN(')
IN64 = string('VL_IN64(')
INW = string('VL_INW(')

OUT8 = string('VL_OUT8(')
OUT16 = string('VL_OUT16(')
OUT32 = string('VL_OUT(')
OUT64 = string('VL_OUT64(')
OUTW = string('VL_OUTW(')

#  print(IN8.parse('     VL_IN8(axim2ram_rvalid,0,0);'))


portlist = {
    "rst": "IN8",
    "up_axis_tlast": "IN8",
    "up_axis_tvalid": "IN8",
    "up_axis_tready": "OUT8",
    "dn_axis_tlast": "OUT8",
    "dn_axis_tvalid": "OUT8",
    "dn_axis_tready": "IN8",
    "up_axis_tdata": "INW",
    "dn_axis_tdata": "OUTW"}


print(create_cpp(portlist))
