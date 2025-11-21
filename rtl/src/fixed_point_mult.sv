// Fixed-Point Multiplier
// Q{INT_BITS}.{FRAC_BITS} format
// Result = (A * B) >> FRAC_BITS

module fixed_point_mult #(
    parameter INT_BITS  = 12,
    parameter FRAC_BITS = 12,
    parameter TOTAL_BITS = INT_BITS + FRAC_BITS + 1  // +1 for sign
) (
    input  logic signed [TOTAL_BITS-1:0] a,
    input  logic signed [TOTAL_BITS-1:0] b,
    output logic signed [TOTAL_BITS-1:0] result
);

    // Full precision product
    logic signed [2*TOTAL_BITS-1:0] full_product;

    assign full_product = a * b;

    // Shift right by FRAC_BITS and take lower TOTAL_BITS
    assign result = full_product[TOTAL_BITS + FRAC_BITS - 1 : FRAC_BITS];

endmodule


// Pipelined version for higher clock speeds
module fixed_point_mult_pipe #(
    parameter INT_BITS  = 12,
    parameter FRAC_BITS = 12,
    parameter TOTAL_BITS = INT_BITS + FRAC_BITS + 1
) (
    input  logic clk,
    input  logic rst_n,
    input  logic valid_in,
    input  logic signed [TOTAL_BITS-1:0] a,
    input  logic signed [TOTAL_BITS-1:0] b,
    output logic valid_out,
    output logic signed [TOTAL_BITS-1:0] result
);

    logic signed [2*TOTAL_BITS-1:0] full_product;
    logic valid_r;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            full_product <= '0;
            valid_r <= 1'b0;
        end
        else begin
            full_product <= a * b;
            valid_r <= valid_in;
        end
    end

    assign result = full_product[TOTAL_BITS + FRAC_BITS - 1 : FRAC_BITS];
    assign valid_out = valid_r;

endmodule
