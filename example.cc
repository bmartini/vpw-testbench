#include "Vexample.h"
#include "verilated.h"
#include "verilated_vcd_c.h"

typedef Vexample TB;
#include "testbench.hh"


void prep(const std::string port, const std::vector<uint64_t> &value) {

  if ("rst" == port) {
    dut->rst = static_cast<uint8_t>(value[0]);
  } else if ("up_axis_tdata" == port) {
    dut->up_axis_tdata = static_cast<const uint64_t>(value[0]);
  } else if ("up_axis_tlast" == port) {
    dut->up_axis_tlast = static_cast<const uint8_t>(value[0]);
  } else if ("up_axis_tvalid" == port) {
    dut->up_axis_tvalid = static_cast<const uint8_t>(value[0]);
  } else if ("dn_axis_tready" == port) {
    dut->dn_axis_tready = static_cast<const uint8_t>(value[0]);
  } else {
    printf("WARNING: requested port \'%s\' not found.\n", port.c_str());
  }
}

py::dict update() {

  return py::dict (
    "rst"_a = dut->rst,

    "up_axis_tdata"_a = dut->up_axis_tdata,
    "up_axis_tlast"_a = dut->up_axis_tlast,
    "up_axis_tvalid"_a = dut->up_axis_tvalid,
    "up_axis_tready"_a = dut->up_axis_tready,

    "dn_axis_tdata"_a = dut->dn_axis_tdata,
    "dn_axis_tlast"_a = dut->dn_axis_tlast,
    "dn_axis_tvalid"_a = dut->dn_axis_tvalid,
    "dn_axis_tready"_a = dut->dn_axis_tready
  );
}
