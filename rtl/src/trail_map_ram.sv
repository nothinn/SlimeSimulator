// Trail Map RAM Module
// True dual-port BRAM for trail map storage
// Port A: VGA read (25 MHz)
// Port B: Agent read/write (100 MHz)
//
// Parameters:
//   PIPELINE_STAGES: Number of output register stages (0-2)
//                    0 = no pipeline (1 cycle read latency)
//                    1 = one pipeline stage (2 cycle read latency)
//                    2 = two pipeline stages (3 cycle read latency)

module trail_map_ram #(
    parameter WIDTH = 320,
    parameter HEIGHT = 240,
    parameter DATA_WIDTH = 18,
    parameter PIPELINE_STAGES = 0  // Configurable pipeline depth
) (
    // Port A (VGA read)
    input  logic clk_a,
    input  logic en_a,                      // Read enable for Port A
    input  logic [18:0] addr_a,
    output logic [DATA_WIDTH-1:0] data_a,

    // Port B (Agent read/write)
    input  logic clk_b,
    input  logic en_b,                      // Read enable for Port B
    input  logic [18:0] addr_b,
    input  logic [DATA_WIDTH-1:0] data_b_in,
    input  logic we_b,
    output logic [DATA_WIDTH-1:0] data_b_out
);

    // True dual-port RAM
    // Following Xilinx BRAM inference template for independent clocks
    (* ram_style = "block" *) logic [DATA_WIDTH-1:0] mem [0:WIDTH*HEIGHT-1];

    // Initialize memory to zero (for simulation only, hardware will power up with undefined values)
    initial begin
        for (int i = 0; i < WIDTH*HEIGHT; i++) begin
            mem[i] = '0;
        end
    end

    // BRAM output registers (stage 0)
    logic [DATA_WIDTH-1:0] mem_out_a = '0;
    logic [DATA_WIDTH-1:0] mem_out_b = '0;

    // Pipeline registers (initialized for simulation)
    logic [DATA_WIDTH-1:0] pipe_a [2] = '{default: '0};  // Up to 2 pipeline stages for Port A
    logic [DATA_WIDTH-1:0] pipe_b [2] = '{default: '0};  // Up to 2 pipeline stages for Port B

    // Port A: Read port with enable and optional pipeline
    always_ff @(posedge clk_a) begin
        if (en_a) begin
            mem_out_a <= mem[addr_a];
        end
    end

    // Port B: Read/write port with enable (write-first mode)
    always_ff @(posedge clk_b) begin
        if (we_b) begin
            mem[addr_b] <= data_b_in;
        end
        if (en_b) begin
            // Write-first: if writing and reading same address, forward the write data
            if (we_b) begin
                mem_out_b <= data_b_in;
            end else begin
                mem_out_b <= mem[addr_b];
            end
        end
    end

    // Pipeline stages for Port A
    always_ff @(posedge clk_a) begin
        pipe_a[0] <= mem_out_a;
        pipe_a[1] <= pipe_a[0];
    end

    // Pipeline stages for Port B
    always_ff @(posedge clk_b) begin
        pipe_b[0] <= mem_out_b;
        pipe_b[1] <= pipe_b[0];
    end

    // Output mux based on PIPELINE_STAGES parameter
    always_comb begin
        case (PIPELINE_STAGES)
            0: data_a = mem_out_a;
            1: data_a = pipe_a[0];
            2: data_a = pipe_a[1];
            default: data_a = mem_out_a;
        endcase
    end

    always_comb begin
        case (PIPELINE_STAGES)
            0: data_b_out = mem_out_b;
            1: data_b_out = pipe_b[0];
            2: data_b_out = pipe_b[1];
            default: data_b_out = mem_out_b;
        endcase
    end

endmodule
