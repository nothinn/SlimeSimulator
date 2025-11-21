// LFSR - Linear Feedback Shift Register
// Matches Python implementation for RTL verification
//
// Uses maximal-length Galois LFSR with configurable width
// Tap positions for maximal-length sequences:
// - 32-bit: taps at 32, 22, 2, 1 (polynomial: x^32 + x^22 + x^2 + x + 1)

module lfsr #(
    parameter WIDTH = 32,
    parameter [WIDTH-1:0] SEED = 32'hDEADBEEF
) (
    input  logic clk,
    input  logic rst_n,
    input  logic enable,
    input  logic load,
    input  logic [WIDTH-1:0] seed_val,
    output logic [WIDTH-1:0] lfsr_out,
    output logic valid
);

    logic [WIDTH-1:0] lfsr_reg;
    logic feedback;

    // Generate feedback based on width
    // Python taps are 1-indexed from MSB, so tap N = bit[WIDTH-N]
    // These match the Python LFSR.TAPS exactly
    generate
        if (WIDTH == 8) begin : gen_8bit
            // Taps: 8, 6, 5, 4 -> bits 0, 2, 3, 4
            assign feedback = lfsr_reg[0] ^ lfsr_reg[2] ^ lfsr_reg[3] ^ lfsr_reg[4];
        end
        else if (WIDTH == 16) begin : gen_16bit
            // Taps: 16, 15, 13, 4 -> bits 0, 1, 3, 12
            assign feedback = lfsr_reg[0] ^ lfsr_reg[1] ^ lfsr_reg[3] ^ lfsr_reg[12];
        end
        else if (WIDTH == 24) begin : gen_24bit
            // Taps: 24, 23, 22, 17 -> bits 0, 1, 2, 7
            assign feedback = lfsr_reg[0] ^ lfsr_reg[1] ^ lfsr_reg[2] ^ lfsr_reg[7];
        end
        else if (WIDTH == 32) begin : gen_32bit
            // Taps: 32, 22, 2, 1 -> bits 0, 10, 30, 31
            assign feedback = lfsr_reg[0] ^ lfsr_reg[10] ^ lfsr_reg[30] ^ lfsr_reg[31];
        end
        else if (WIDTH == 48) begin : gen_48bit
            // Taps: 48, 47, 21, 20 -> bits 0, 1, 27, 28
            assign feedback = lfsr_reg[0] ^ lfsr_reg[1] ^ lfsr_reg[27] ^ lfsr_reg[28];
        end
        else if (WIDTH == 64) begin : gen_64bit
            // Taps: 64, 63, 61, 60 -> bits 0, 1, 3, 4
            assign feedback = lfsr_reg[0] ^ lfsr_reg[1] ^ lfsr_reg[3] ^ lfsr_reg[4];
        end
        else begin : gen_default
            // Default to 32-bit
            assign feedback = lfsr_reg[0] ^ lfsr_reg[10] ^ lfsr_reg[30] ^ lfsr_reg[31];
        end
    endgenerate

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            lfsr_reg <= SEED;
            valid <= 1'b0;
        end
        else if (load) begin
            // Load new seed (ensure non-zero)
            lfsr_reg <= (seed_val == '0) ? SEED : seed_val;
            valid <= 1'b0;
        end
        else if (enable) begin
            // Shift left and insert feedback at LSB
            lfsr_reg <= {lfsr_reg[WIDTH-2:0], feedback};
            valid <= 1'b1;
        end
        else begin
            valid <= 1'b0;
        end
    end

    assign lfsr_out = lfsr_reg;

endmodule
