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
    // These match the Python LFSR.TAPS exactly
    generate
        if (WIDTH == 8) begin : gen_8bit
            // Taps: 8, 6, 5, 4
            assign feedback = lfsr_reg[7] ^ lfsr_reg[5] ^ lfsr_reg[4] ^ lfsr_reg[3];
        end
        else if (WIDTH == 16) begin : gen_16bit
            // Taps: 16, 15, 13, 4
            assign feedback = lfsr_reg[15] ^ lfsr_reg[14] ^ lfsr_reg[12] ^ lfsr_reg[3];
        end
        else if (WIDTH == 24) begin : gen_24bit
            // Taps: 24, 23, 22, 17
            assign feedback = lfsr_reg[23] ^ lfsr_reg[22] ^ lfsr_reg[21] ^ lfsr_reg[16];
        end
        else if (WIDTH == 32) begin : gen_32bit
            // Taps: 32, 22, 2, 1
            assign feedback = lfsr_reg[31] ^ lfsr_reg[21] ^ lfsr_reg[1] ^ lfsr_reg[0];
        end
        else if (WIDTH == 48) begin : gen_48bit
            // Taps: 48, 47, 21, 20
            assign feedback = lfsr_reg[47] ^ lfsr_reg[46] ^ lfsr_reg[20] ^ lfsr_reg[19];
        end
        else if (WIDTH == 64) begin : gen_64bit
            // Taps: 64, 63, 61, 60
            assign feedback = lfsr_reg[63] ^ lfsr_reg[62] ^ lfsr_reg[60] ^ lfsr_reg[59];
        end
        else begin : gen_default
            // Default to 32-bit
            assign feedback = lfsr_reg[31] ^ lfsr_reg[21] ^ lfsr_reg[1] ^ lfsr_reg[0];
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
