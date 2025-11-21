// Trig Lookup Table (Sin/Cos ROM)
// Stores sin values for one full period
// Cos is obtained by phase-shifting the index by 90 degrees (TABLE_SIZE/4)
//
// Matches Python TrigLUT implementation

module trig_lut #(
    parameter ADDR_BITS = 10,                    // 1024 entries
    parameter DATA_BITS = 25,                    // Q12.12 + sign
    parameter FRAC_BITS = 12
) (
    input  logic clk,
    input  logic [ADDR_BITS-1:0] angle_idx,     // Angle as table index
    output logic signed [DATA_BITS-1:0] sin_out,
    output logic signed [DATA_BITS-1:0] cos_out
);

    localparam TABLE_SIZE = 1 << ADDR_BITS;
    localparam QUARTER = TABLE_SIZE / 4;

    // ROM for sine values (initialized at synthesis)
    (* rom_style = "block" *) logic signed [DATA_BITS-1:0] sin_rom [0:TABLE_SIZE-1];
    (* rom_style = "block" *) logic signed [DATA_BITS-1:0] cos_rom [0:TABLE_SIZE-1];

    // Index for cosine (90 degree phase shift)
    logic [ADDR_BITS-1:0] cos_idx;
    assign cos_idx = angle_idx + QUARTER[ADDR_BITS-1:0];

    // Registered outputs for timing
    always_ff @(posedge clk) begin
        sin_out <= sin_rom[angle_idx];
        cos_out <= cos_rom[angle_idx];
    end

    // Initialize ROM with sine/cosine values
    // sin(2*pi*i/TABLE_SIZE) scaled by 2^FRAC_BITS
    initial begin
        for (int i = 0; i < TABLE_SIZE; i++) begin
            real angle = 2.0 * 3.14159265358979323846 * i / TABLE_SIZE;
            sin_rom[i] = $rtoi($floor($sin(angle) * (1 << FRAC_BITS) + 0.5));
            cos_rom[i] = $rtoi($floor($cos(angle) * (1 << FRAC_BITS) + 0.5));
        end
    end

endmodule


// Dual-port version for simultaneous sin/cos lookups at different angles
module trig_lut_dual #(
    parameter ADDR_BITS = 10,
    parameter DATA_BITS = 25,
    parameter FRAC_BITS = 12
) (
    input  logic clk,

    // Port A - for forward sensor
    input  logic [ADDR_BITS-1:0] angle_a,
    output logic signed [DATA_BITS-1:0] sin_a,
    output logic signed [DATA_BITS-1:0] cos_a,

    // Port B - for left/right sensors
    input  logic [ADDR_BITS-1:0] angle_b,
    output logic signed [DATA_BITS-1:0] sin_b,
    output logic signed [DATA_BITS-1:0] cos_b
);

    localparam TABLE_SIZE = 1 << ADDR_BITS;

    // ROM arrays
    (* rom_style = "block" *) logic signed [DATA_BITS-1:0] sin_rom [0:TABLE_SIZE-1];
    (* rom_style = "block" *) logic signed [DATA_BITS-1:0] cos_rom [0:TABLE_SIZE-1];

    // Registered outputs
    always_ff @(posedge clk) begin
        sin_a <= sin_rom[angle_a];
        cos_a <= cos_rom[angle_a];
        sin_b <= sin_rom[angle_b];
        cos_b <= cos_rom[angle_b];
    end

    // Initialize ROM
    initial begin
        for (int i = 0; i < TABLE_SIZE; i++) begin
            real angle = 2.0 * 3.14159265358979323846 * i / TABLE_SIZE;
            sin_rom[i] = $rtoi($floor($sin(angle) * (1 << FRAC_BITS) + 0.5));
            cos_rom[i] = $rtoi($floor($cos(angle) * (1 << FRAC_BITS) + 0.5));
        end
    end

endmodule
