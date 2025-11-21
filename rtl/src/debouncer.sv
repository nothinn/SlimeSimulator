// Button Debouncer
// Filters mechanical bounce from push buttons
// Outputs clean single-cycle pulse on button press

module debouncer #(
    parameter CLK_FREQ = 100_000_000,  // 100 MHz
    parameter DEBOUNCE_MS = 20         // 20ms debounce time
) (
    input  logic clk,
    input  logic rst_n,
    input  logic btn_in,
    output logic btn_out,      // Debounced level
    output logic btn_posedge,  // Single-cycle pulse on press
    output logic btn_negedge   // Single-cycle pulse on release
);

    localparam DEBOUNCE_CYCLES = (CLK_FREQ / 1000) * DEBOUNCE_MS;
    localparam COUNTER_BITS = $clog2(DEBOUNCE_CYCLES + 1);

    logic [COUNTER_BITS-1:0] counter;
    logic btn_sync_0, btn_sync_1;  // Synchronizer
    logic btn_stable;
    logic btn_stable_prev;

    // Two-stage synchronizer for metastability
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            btn_sync_0 <= 1'b0;
            btn_sync_1 <= 1'b0;
        end
        else begin
            btn_sync_0 <= btn_in;
            btn_sync_1 <= btn_sync_0;
        end
    end

    // Debounce counter
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            counter <= '0;
            btn_stable <= 1'b0;
        end
        else begin
            if (btn_sync_1 != btn_stable) begin
                // Input changed, start counting
                if (counter == DEBOUNCE_CYCLES - 1) begin
                    // Stable for long enough, update output
                    btn_stable <= btn_sync_1;
                    counter <= '0;
                end
                else begin
                    counter <= counter + 1'b1;
                end
            end
            else begin
                // Input matches stable state, reset counter
                counter <= '0;
            end
        end
    end

    // Edge detection
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            btn_stable_prev <= 1'b0;
        end
        else begin
            btn_stable_prev <= btn_stable;
        end
    end

    assign btn_out = btn_stable;
    assign btn_posedge = btn_stable && !btn_stable_prev;
    assign btn_negedge = !btn_stable && btn_stable_prev;

endmodule


// Multiple button debouncer
module debouncer_array #(
    parameter NUM_BUTTONS = 4,
    parameter CLK_FREQ = 100_000_000,
    parameter DEBOUNCE_MS = 20
) (
    input  logic clk,
    input  logic rst_n,
    input  logic [NUM_BUTTONS-1:0] btn_in,
    output logic [NUM_BUTTONS-1:0] btn_out,
    output logic [NUM_BUTTONS-1:0] btn_posedge,
    output logic [NUM_BUTTONS-1:0] btn_negedge
);

    genvar i;
    generate
        for (i = 0; i < NUM_BUTTONS; i++) begin : gen_debouncer
            debouncer #(
                .CLK_FREQ(CLK_FREQ),
                .DEBOUNCE_MS(DEBOUNCE_MS)
            ) u_debouncer (
                .clk(clk),
                .rst_n(rst_n),
                .btn_in(btn_in[i]),
                .btn_out(btn_out[i]),
                .btn_posedge(btn_posedge[i]),
                .btn_negedge(btn_negedge[i])
            );
        end
    endgenerate

endmodule
