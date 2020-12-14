#include "Vexample.h"
#include "verilated.h"
#include "verilated_vcd_c.h"

typedef Vexample TB;
#include "testbench.hh"


void prep(const std::string port, const std::vector<uint64_t> &value) {

  if ("rst" == port) {
    dut->rst = static_cast<const uint8_t>(value[0]);
  } else if ("up_axis_tlast" == port) {
    dut->up_axis_tlast = static_cast<const uint8_t>(value[0]);
  } else if ("up_axis_tvalid" == port) {
    dut->up_axis_tvalid = static_cast<const uint8_t>(value[0]);
  } else if ("dn_axis_tready" == port) {
    dut->dn_axis_tready = static_cast<const uint8_t>(value[0]);
  } else if ("axim_awlen" == port) {
    dut->axim_awlen = static_cast<const uint8_t>(value[0]);
  } else if ("axim_awid" == port) {
    dut->axim_awid = static_cast<const uint8_t>(value[0]);
  } else if ("axim_awcache" == port) {
    dut->axim_awcache = static_cast<const uint8_t>(value[0]);
  } else if ("axim_awqos" == port) {
    dut->axim_awqos = static_cast<const uint8_t>(value[0]);
  } else if ("axim_awprot" == port) {
    dut->axim_awprot = static_cast<const uint8_t>(value[0]);
  } else if ("axim_awsize" == port) {
    dut->axim_awsize = static_cast<const uint8_t>(value[0]);
  } else if ("axim_awburst" == port) {
    dut->axim_awburst = static_cast<const uint8_t>(value[0]);
  } else if ("axim_awlock" == port) {
    dut->axim_awlock = static_cast<const uint8_t>(value[0]);
  } else if ("axim_awvalid" == port) {
    dut->axim_awvalid = static_cast<const uint8_t>(value[0]);
  } else if ("axim_wlast" == port) {
    dut->axim_wlast = static_cast<const uint8_t>(value[0]);
  } else if ("axim_wvalid" == port) {
    dut->axim_wvalid = static_cast<const uint8_t>(value[0]);
  } else if ("axim_bid" == port) {
    dut->axim_bid = static_cast<const uint8_t>(value[0]);
  } else if ("axim_bresp" == port) {
    dut->axim_bresp = static_cast<const uint8_t>(value[0]);
  } else if ("axim_bvalid" == port) {
    dut->axim_bvalid = static_cast<const uint8_t>(value[0]);
  } else if ("axim_arlen" == port) {
    dut->axim_arlen = static_cast<const uint8_t>(value[0]);
  } else if ("axim_arid" == port) {
    dut->axim_arid = static_cast<const uint8_t>(value[0]);
  } else if ("axim_arcache" == port) {
    dut->axim_arcache = static_cast<const uint8_t>(value[0]);
  } else if ("axim_arqos" == port) {
    dut->axim_arqos = static_cast<const uint8_t>(value[0]);
  } else if ("axim_arprot" == port) {
    dut->axim_arprot = static_cast<const uint8_t>(value[0]);
  } else if ("axim_arsize" == port) {
    dut->axim_arsize = static_cast<const uint8_t>(value[0]);
  } else if ("axim_arburst" == port) {
    dut->axim_arburst = static_cast<const uint8_t>(value[0]);
  } else if ("axim_arlock" == port) {
    dut->axim_arlock = static_cast<const uint8_t>(value[0]);
  } else if ("axim_arvalid" == port) {
    dut->axim_arvalid = static_cast<const uint8_t>(value[0]);
  } else if ("axim_rready" == port) {
    dut->axim_rready = static_cast<const uint8_t>(value[0]);
  } else if ("axim2ram_awready" == port) {
    dut->axim2ram_awready = static_cast<const uint8_t>(value[0]);
  } else if ("axim2ram_wready" == port) {
    dut->axim2ram_wready = static_cast<const uint8_t>(value[0]);
  } else if ("axim2ram_bready" == port) {
    dut->axim2ram_bready = static_cast<const uint8_t>(value[0]);
  } else if ("axim2ram_arready" == port) {
    dut->axim2ram_arready = static_cast<const uint8_t>(value[0]);
  } else if ("axim2ram_rid" == port) {
    dut->axim2ram_rid = static_cast<const uint8_t>(value[0]);
  } else if ("axim2ram_rresp" == port) {
    dut->axim2ram_rresp = static_cast<const uint8_t>(value[0]);
  } else if ("axim2ram_rlast" == port) {
    dut->axim2ram_rlast = static_cast<const uint8_t>(value[0]);
  } else if ("axim2ram_rvalid" == port) {
    dut->axim2ram_rvalid = static_cast<const uint8_t>(value[0]);
  } else if ("axim_awaddr" == port) {
    dut->axim_awaddr = static_cast<const uint16_t>(value[0]);
  } else if ("axim_wstrb" == port) {
    dut->axim_wstrb = static_cast<const uint16_t>(value[0]);
  } else if ("axim_araddr" == port) {
    dut->axim_araddr = static_cast<const uint16_t>(value[0]);
  } else if ("axim2ram_rstrb" == port) {
    dut->axim2ram_rstrb = static_cast<const uint16_t>(value[0]);
  } else if ("axim_wdata" == port) {
    for (std::size_t i = 0; i != value.size(); ++i) {
       dut->axim_wdata[i] = static_cast<const uint32_t>(value[i]);
    }
  } else if ("axim2ram_rdata" == port) {
    for (std::size_t i = 0; i != value.size(); ++i) {
       dut->axim2ram_rdata[i] = static_cast<const uint32_t>(value[i]);
    }
  } else if ("up_axis_tdata" == port) {
    dut->up_axis_tdata = static_cast<const uint64_t>(value[0]);
  } else {
    printf("WARNING: requested port \'%s\' not found.\n", port.c_str());
  }
}

py::dict update() {

  py::list axim_wdata;
  for (auto &item : dut->axim_wdata) {
    axim_wdata.append(item);
  }

  py::list axim_rdata;
  for (auto &item : dut->axim_rdata) {
    axim_rdata.append(item);
  }

  py::list axim2ram_wdata;
  for (auto &item : dut->axim2ram_wdata) {
    axim2ram_wdata.append(item);
  }

  py::list axim2ram_rdata;
  for (auto &item : dut->axim2ram_rdata) {
    axim2ram_rdata.append(item);
  }

  return py::dict (
    "rst"_a = dut->rst,
    "up_axis_tlast"_a = dut->up_axis_tlast,
    "up_axis_tvalid"_a = dut->up_axis_tvalid,
    "up_axis_tready"_a = dut->up_axis_tready,
    "dn_axis_tlast"_a = dut->dn_axis_tlast,
    "dn_axis_tvalid"_a = dut->dn_axis_tvalid,
    "dn_axis_tready"_a = dut->dn_axis_tready,
    "axim_awlen"_a = dut->axim_awlen,
    "axim_awid"_a = dut->axim_awid,
    "axim_awcache"_a = dut->axim_awcache,
    "axim_awqos"_a = dut->axim_awqos,
    "axim_awprot"_a = dut->axim_awprot,
    "axim_awsize"_a = dut->axim_awsize,
    "axim_awburst"_a = dut->axim_awburst,
    "axim_awlock"_a = dut->axim_awlock,
    "axim_awvalid"_a = dut->axim_awvalid,
    "axim_awready"_a = dut->axim_awready,
    "axim_wlast"_a = dut->axim_wlast,
    "axim_wvalid"_a = dut->axim_wvalid,
    "axim_wready"_a = dut->axim_wready,
    "axim_bid"_a = dut->axim_bid,
    "axim_bresp"_a = dut->axim_bresp,
    "axim_bvalid"_a = dut->axim_bvalid,
    "axim_bready"_a = dut->axim_bready,
    "axim_arlen"_a = dut->axim_arlen,
    "axim_arid"_a = dut->axim_arid,
    "axim_arcache"_a = dut->axim_arcache,
    "axim_arqos"_a = dut->axim_arqos,
    "axim_arprot"_a = dut->axim_arprot,
    "axim_arsize"_a = dut->axim_arsize,
    "axim_arburst"_a = dut->axim_arburst,
    "axim_arlock"_a = dut->axim_arlock,
    "axim_arvalid"_a = dut->axim_arvalid,
    "axim_arready"_a = dut->axim_arready,
    "axim_rid"_a = dut->axim_rid,
    "axim_rresp"_a = dut->axim_rresp,
    "axim_rlast"_a = dut->axim_rlast,
    "axim_rvalid"_a = dut->axim_rvalid,
    "axim_rready"_a = dut->axim_rready,
    "axim2ram_awlen"_a = dut->axim2ram_awlen,
    "axim2ram_awid"_a = dut->axim2ram_awid,
    "axim2ram_awcache"_a = dut->axim2ram_awcache,
    "axim2ram_awqos"_a = dut->axim2ram_awqos,
    "axim2ram_awprot"_a = dut->axim2ram_awprot,
    "axim2ram_awsize"_a = dut->axim2ram_awsize,
    "axim2ram_awburst"_a = dut->axim2ram_awburst,
    "axim2ram_awlock"_a = dut->axim2ram_awlock,
    "axim2ram_awvalid"_a = dut->axim2ram_awvalid,
    "axim2ram_awready"_a = dut->axim2ram_awready,
    "axim2ram_wlast"_a = dut->axim2ram_wlast,
    "axim2ram_wvalid"_a = dut->axim2ram_wvalid,
    "axim2ram_wready"_a = dut->axim2ram_wready,
    "axim2ram_bid"_a = dut->axim2ram_bid,
    "axim2ram_bresp"_a = dut->axim2ram_bresp,
    "axim2ram_bvalid"_a = dut->axim2ram_bvalid,
    "axim2ram_bready"_a = dut->axim2ram_bready,
    "axim2ram_arlen"_a = dut->axim2ram_arlen,
    "axim2ram_arid"_a = dut->axim2ram_arid,
    "axim2ram_arcache"_a = dut->axim2ram_arcache,
    "axim2ram_arqos"_a = dut->axim2ram_arqos,
    "axim2ram_arprot"_a = dut->axim2ram_arprot,
    "axim2ram_arsize"_a = dut->axim2ram_arsize,
    "axim2ram_arburst"_a = dut->axim2ram_arburst,
    "axim2ram_arlock"_a = dut->axim2ram_arlock,
    "axim2ram_arvalid"_a = dut->axim2ram_arvalid,
    "axim2ram_arready"_a = dut->axim2ram_arready,
    "axim2ram_rid"_a = dut->axim2ram_rid,
    "axim2ram_rresp"_a = dut->axim2ram_rresp,
    "axim2ram_rlast"_a = dut->axim2ram_rlast,
    "axim2ram_rvalid"_a = dut->axim2ram_rvalid,
    "axim2ram_rready"_a = dut->axim2ram_rready,
    "axim_awaddr"_a = dut->axim_awaddr,
    "axim_wstrb"_a = dut->axim_wstrb,
    "axim_araddr"_a = dut->axim_araddr,
    "axim_rstrb"_a = dut->axim_rstrb,
    "axim2ram_awaddr"_a = dut->axim2ram_awaddr,
    "axim2ram_wstrb"_a = dut->axim2ram_wstrb,
    "axim2ram_araddr"_a = dut->axim2ram_araddr,
    "axim2ram_rstrb"_a = dut->axim2ram_rstrb,
    "axim_wdata"_a = axim_wdata,
    "axim_rdata"_a = axim_rdata,
    "axim2ram_wdata"_a = axim2ram_wdata,
    "axim2ram_rdata"_a = axim2ram_rdata,
    "up_axis_tdata"_a = dut->up_axis_tdata,
    "dn_axis_tdata"_a = dut->dn_axis_tdata
  );
}
