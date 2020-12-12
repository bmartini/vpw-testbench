`ifndef _skid_buffer_
`define _skid_buffer_

`default_nettype none

module skid_buffer
  #(parameter DATA_WIDTH = 32)
   (input   wire                        clk,
    input   wire                        rst,

    input   wire    [DATA_WIDTH-1:0]    up_tdata,
    input   wire                        up_tlast,
    input   wire                        up_tvalid,
    output  logic                       up_tready,

    output  logic   [DATA_WIDTH-1:0]    dn_tdata,
    output  logic                       dn_tlast,
    output  logic                       dn_tvalid,
    input   wire                        dn_tready
);

    logic   [DATA_WIDTH-1:0]    skid_data;
    logic                       skid_last;
    logic                       skid_valid;

    logic   [DATA_WIDTH-1:0]    up_data_t;
    logic                       up_last_t;
    logic                       up_valid_t;

    wire                        dn_active;


    // skid_data reflects downstream data last cycle
    always_ff @(posedge clk) begin
        skid_data <= up_data_t;
    end


    always_ff @(posedge clk) begin
        if (rst)    skid_last <= 1'b0;
        else        skid_last <= up_last_t & ~dn_active;
    end


    // skid_valid remembers if there is valid data in the skid register until
    // it's consumed by the downstream
    always_ff @(posedge clk) begin
        if (rst)    skid_valid <= 1'b0;
        else        skid_valid <= up_valid_t & ~dn_active;
    end


    // muxing between incoming data or data waiting to be passed down stream
    assign up_data_t    = up_tready ? up_tdata  : skid_data;

    assign up_last_t    = up_tready ? up_tlast  : skid_last;

    assign up_valid_t   = up_tready ? up_tvalid : skid_valid;


    // when down stream is ready or up stream has valid data, set upstream
    // ready to high if the modules 'down' pipeline is not stalled
    always_ff @(posedge clk) begin
        if (rst) up_tready <= 1'b0;
        else if (dn_tready | up_tvalid) begin
            up_tready <= dn_active;
        end
    end


    always_ff @(posedge clk) begin
        if      (rst)       dn_tlast <= 1'b0;
        else if (dn_active) dn_tlast <= up_last_t;
    end


    always_ff @(posedge clk) begin
        if      (rst)       dn_tvalid <= 1'b0;
        else if (dn_active) dn_tvalid <= up_valid_t;
    end


    always_ff @(posedge clk) begin
        if (dn_active) dn_tdata <= up_data_t;
    end


    // do not stall pipeline until it is primed
    assign dn_active = ~dn_tvalid | dn_tready;


endmodule

`default_nettype wire

`endif //  `ifndef _skid_buffer_
