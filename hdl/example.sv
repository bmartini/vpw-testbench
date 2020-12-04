`ifndef _example_
`define _example_

module example
  #(parameter DATA_WIDTH = 2)
   (input   wire                        clk,
    input   wire                        rst,

    input   wire    [DATA_WIDTH-1:0]    up_axis_tdata,
    input   wire                        up_axis_tlast,
    input   wire                        up_axis_tvalid,
    output  logic                       up_axis_tready,

    output  logic   [DATA_WIDTH-1:0]    dn_axis_tdata,
    output  logic                       dn_axis_tlast,
    output  logic                       dn_axis_tvalid,
    input   wire                        dn_axis_tready
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
    assign up_data_t    = up_axis_tready ? up_axis_tdata  : skid_data;

    assign up_last_t    = up_axis_tready ? up_axis_tlast  : skid_last;

    assign up_valid_t   = up_axis_tready ? up_axis_tvalid : skid_valid;


    // when down stream is ready or up stream has valid data, set upstream
    // ready to high if the modules 'down' pipeline is not stalled
    always_ff @(posedge clk) begin
        if (rst) up_axis_tready <= 1'b0;
        else if (dn_axis_tready | up_axis_tvalid) begin
            up_axis_tready <= dn_active;
        end
    end


    always_ff @(posedge clk) begin
        if      (rst)       dn_axis_tlast <= 1'b0;
        else if (dn_active) dn_axis_tlast <= up_last_t;
    end


    always_ff @(posedge clk) begin
        if      (rst)       dn_axis_tvalid <= 1'b0;
        else if (dn_active) dn_axis_tvalid <= up_valid_t;
    end


    always_ff @(posedge clk) begin
        if (dn_active) dn_axis_tdata <= up_data_t;
    end


    // do not stall pipeline until it is primed
    assign dn_active = ~dn_axis_tvalid | dn_axis_tready;


endmodule

`endif //  `ifndef _example_
