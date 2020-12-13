`ifndef _example_
`define _example_

`default_nettype none

module example
  #(parameter AXIS_DWIDTH = 32,
    parameter AXIM_DWIDTH = 128,
    parameter AXIM_AWIDTH = 16)
   (input   wire                        clk,
    input   wire                        rst,

    // AXI-Stream Slave
    input   wire    [2*AXIS_DWIDTH-1:0] up_axis_tdata,
    input   wire    [1:0]               up_axis_tlast,
    input   wire    [1:0]               up_axis_tvalid,
    output  logic   [1:0]               up_axis_tready,

    // AXI-Stream Master
    output  logic   [2*AXIS_DWIDTH-1:0] dn_axis_tdata,
    output  logic   [1:0]               dn_axis_tlast,
    output  logic   [1:0]               dn_axis_tvalid,
    input   wire    [1:0]               dn_axis_tready,

    // AXI-MM Slave
    input   wire    [AXIM_AWIDTH-1:0]   axim_awaddr,
    input   wire    [7:0]               axim_awlen,
    input   wire    [3:0]               axim_awid,
    input   wire    [3:0]               axim_awcache,
    input   wire    [3:0]               axim_awqos,
    input   wire    [3:0]               axim_awprot,
    input   wire    [2:0]               axim_awsize,
    input   wire    [1:0]               axim_awburst,
    input   wire    [0:0]               axim_awlock,
    input   wire                        axim_awvalid,
    output  logic                       axim_awready,

    input   wire    [AXIM_DWIDTH-1:0]   axim_wdata,
    input   wire    [AXIM_DWIDTH/8-1:0] axim_wstrb,
    input   wire                        axim_wlast,
    input   wire                        axim_wvalid,
    output  logic                       axim_wready,

    input   wire    [3:0]               axim_bid,
    input   wire    [1:0]               axim_bresp,
    input   wire                        axim_bvalid,
    output  logic                       axim_bready,

    input   wire    [AXIM_AWIDTH-1:0]   axim_araddr,
    input   wire    [7:0]               axim_arlen,
    input   wire    [3:0]               axim_arid,
    input   wire    [3:0]               axim_arcache,
    input   wire    [3:0]               axim_arqos,
    input   wire    [3:0]               axim_arprot,
    input   wire    [2:0]               axim_arsize,
    input   wire    [1:0]               axim_arburst,
    input   wire    [0:0]               axim_arlock,
    input   wire                        axim_arvalid,
    output  logic                       axim_arready,

    output  logic   [AXIM_DWIDTH-1:0]   axim_rdata,
    output  logic   [AXIM_DWIDTH/8-1:0] axim_rstrb,
    output  logic   [3:0]               axim_rid,
    output  logic   [1:0]               axim_rresp,
    output  logic                       axim_rlast,
    output  logic                       axim_rvalid,
    input   wire                        axim_rready,

    // AXI-MM Master
    output  logic   [AXIM_AWIDTH-1:0]   axim2ram_awaddr,
    output  logic   [7:0]               axim2ram_awlen,
    output  logic   [3:0]               axim2ram_awid,
    output  logic   [3:0]               axim2ram_awcache,
    output  logic   [3:0]               axim2ram_awqos,
    output  logic   [3:0]               axim2ram_awprot,
    output  logic   [2:0]               axim2ram_awsize,
    output  logic   [1:0]               axim2ram_awburst,
    output  logic   [0:0]               axim2ram_awlock,
    output  logic                       axim2ram_awvalid,
    input   wire                        axim2ram_awready,

    output  logic   [AXIM_DWIDTH-1:0]   axim2ram_wdata,
    output  logic   [AXIM_DWIDTH/8-1:0] axim2ram_wstrb,
    output  logic                       axim2ram_wlast,
    output  logic                       axim2ram_wvalid,
    input   wire                        axim2ram_wready,

    output  logic   [3:0]               axim2ram_bid,
    output  logic   [1:0]               axim2ram_bresp,
    output  logic                       axim2ram_bvalid,
    input   wire                        axim2ram_bready,

    output  logic   [AXIM_AWIDTH-1:0]   axim2ram_araddr,
    output  logic   [7:0]               axim2ram_arlen,
    output  logic   [3:0]               axim2ram_arid,
    output  logic   [3:0]               axim2ram_arcache,
    output  logic   [3:0]               axim2ram_arqos,
    output  logic   [3:0]               axim2ram_arprot,
    output  logic   [2:0]               axim2ram_arsize,
    output  logic   [1:0]               axim2ram_arburst,
    output  logic   [0:0]               axim2ram_arlock,
    output  logic                       axim2ram_arvalid,
    input   wire                        axim2ram_arready,

    input   wire    [AXIM_DWIDTH-1:0]   axim2ram_rdata,
    input   wire    [AXIM_DWIDTH/8-1:0] axim2ram_rstrb,
    input   wire    [3:0]               axim2ram_rid,
    input   wire    [1:0]               axim2ram_rresp,
    input   wire                        axim2ram_rlast,
    input   wire                        axim2ram_rvalid,
    output  logic                       axim2ram_rready
);

    skid_buffer #(
        .DATA_WIDTH (AXIS_DWIDTH))
    skid_buffer_axis_0_ (
        .clk        (clk),
        .rst        (rst),

        .up_tdata   (up_axis_tdata  [0*AXIS_DWIDTH +: AXIS_DWIDTH]),
        .up_tlast   (up_axis_tlast  [0]),
        .up_tvalid  (up_axis_tvalid [0]),
        .up_tready  (up_axis_tready [0]),

        .dn_tdata   (dn_axis_tdata  [0*AXIS_DWIDTH +: AXIS_DWIDTH]),
        .dn_tlast   (dn_axis_tlast  [0]),
        .dn_tvalid  (dn_axis_tvalid [0]),
        .dn_tready  (dn_axis_tready [0])
    );


    skid_buffer #(
        .DATA_WIDTH (AXIS_DWIDTH))
    skid_buffer_axis_1_ (
        .clk        (clk),
        .rst        (rst),

        .up_tdata   (up_axis_tdata  [1*AXIS_DWIDTH +: AXIS_DWIDTH]),
        .up_tlast   (up_axis_tlast  [1]),
        .up_tvalid  (up_axis_tvalid [1]),
        .up_tready  (up_axis_tready [1]),

        .dn_tdata   (dn_axis_tdata  [1*AXIS_DWIDTH +: AXIS_DWIDTH]),
        .dn_tlast   (dn_axis_tlast  [1]),
        .dn_tvalid  (dn_axis_tvalid [1]),
        .dn_tready  (dn_axis_tready [1])
    );


    assign axim2ram_awaddr  = axim_awaddr;
    assign axim2ram_awlen   = axim_awlen;
    assign axim2ram_awid    = axim_awid;
    assign axim2ram_awcache = axim_awcache;
    assign axim2ram_awqos   = axim_awqos;
    assign axim2ram_awprot  = axim_awprot;
    assign axim2ram_awsize  = axim_awsize;
    assign axim2ram_awburst = axim_awburst;
    assign axim2ram_awlock  = axim_awlock;
    assign axim2ram_awvalid = axim_awvalid;
    assign axim_awready     = axim2ram_awready;

    assign axim2ram_wdata   = axim_wdata;
    assign axim2ram_wstrb   = axim_wstrb;
    assign axim2ram_wlast   = axim_wlast;
    assign axim2ram_wvalid  = axim_wvalid;
    assign axim_wready      = axim2ram_wready;

    assign axim2ram_bid     = axim_bid;
    assign axim2ram_bresp   = axim_bresp;
    assign axim2ram_bvalid  = axim_bvalid;
    assign axim_bready      = axim2ram_bready;

    assign axim2ram_araddr  = axim_araddr;
    assign axim2ram_arlen   = axim_arlen;
    assign axim2ram_arid    = axim_arid;
    assign axim2ram_arcache = axim_arcache;
    assign axim2ram_arqos   = axim_arqos;
    assign axim2ram_arprot  = axim_arprot;
    assign axim2ram_arsize  = axim_arsize;
    assign axim2ram_arburst = axim_arburst;
    assign axim2ram_arlock  = axim_arlock;
    assign axim2ram_arvalid = axim_arvalid;
    assign axim_arready     = axim2ram_arready;

    assign axim_rdata       = axim2ram_rdata;
    assign axim_rstrb       = axim2ram_rstrb;
    assign axim_rid         = axim2ram_rid;
    assign axim_rresp       = axim2ram_rresp;
    assign axim_rlast       = axim2ram_rlast;
    assign axim_rvalid      = axim2ram_rvalid;
    assign axim2ram_rready  = axim_rready;

endmodule

`default_nettype wire

`endif //  `ifndef _example_
