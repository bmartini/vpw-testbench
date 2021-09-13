`ifndef _bram_
`define _bram_

`default_nettype none

module bram
  #(parameter BRAM_DWIDTH = 32,
    parameter BRAM_AWIDTH = 8)
   (input   wire                        clk,

    // Write Interface
    input   wire    [BRAM_DWIDTH-1:0]   wr_data,
    input   wire    [BRAM_AWIDTH-1:0]   wr_addr,
    input   wire                        wr_en,

    // Read Interface
    output  logic   [BRAM_DWIDTH-1:0]   rd_data,
    input   wire    [BRAM_AWIDTH-1:0]   rd_addr,
    input   wire                        rd_en
);

    localparam DEPTH = 1<<BRAM_AWIDTH;

    logic [BRAM_DWIDTH-1:0] mem [DEPTH];

    always_ff @(posedge clk) begin
        if (wr_en) begin
            mem[wr_addr] <= wr_data;
        end
    end


    always_ff @(posedge clk) begin
        rd_data <= 'b0;

        if (rd_en) begin
            rd_data <= mem[rd_addr];
        end
    end


endmodule

`default_nettype wire

`endif //  `ifndef _bram_
