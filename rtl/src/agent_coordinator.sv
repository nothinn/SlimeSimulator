// Agent Coordinator - Manages sequential agent processing through pipelined processor
//
// Simple architecture:
// - Processes agents 0-999 sequentially
// - Each agent takes 19 cycles in the processor
// - Handles agent state storage and updates
// - Manages trail deposits from processor outputs

module agent_coordinator #(
    parameter NUM_AGENTS       = 1000,
    parameter FP_INT_BITS      = 12,
    parameter FP_FRAC_BITS     = 12,
    parameter FP_TOTAL         = FP_INT_BITS + FP_FRAC_BITS + 1,  // 25 bits
    parameter TRIG_BITS        = 10,
    parameter WIDTH            = 320,
    parameter HEIGHT           = 240
) (
    input  logic clk,
    input  logic rst_n,
    input  logic start,
    input  logic pause,
    input  logic [31:0] lfsr_state,

    // Control parameters
    input  logic signed [FP_TOTAL-1:0] sensor_angle,
    input  logic signed [FP_TOTAL-1:0] sensor_distance,
    input  logic signed [FP_TOTAL-1:0] turn_speed,
    input  logic signed [FP_TOTAL-1:0] move_speed,
    input  logic signed [FP_TOTAL-1:0] deposit_amount,

    // Trail map interface (18-bit values)
    input  logic [17:0] trail_data_b_out,
    output logic [18:0] trail_addr_b,
    output logic [17:0] trail_data_b_in,
    output logic trail_we_b,

    output logic done
);

    // Fixed-point scale
    localparam FP_SCALE = 1 << FP_FRAC_BITS;
    localparam AGENT_COUNT_LOG = $clog2(NUM_AGENTS);

    // =========================================================================
    // Agent Memory (distributed RAM blocks)
    // Store: x (25b), y (25b), angle (25b) per agent = 75 bits × 1000 = ~75KB
    // =========================================================================

    logic signed [FP_TOTAL-1:0] agent_x [NUM_AGENTS];
    logic signed [FP_TOTAL-1:0] agent_y [NUM_AGENTS];
    logic signed [FP_TOTAL-1:0] agent_angle [NUM_AGENTS];

    // =========================================================================
    // State Machine
    // =========================================================================

    typedef enum logic [2:0] {
        IDLE,
        INITIALIZE,
        RUNNING,
        DONE_STATE
    } state_t;

    state_t state, next_state;

    logic [AGENT_COUNT_LOG-1:0] current_agent_idx;
    logic [31:0] step_counter;

    // =========================================================================
    // Agent Processor Signals
    // =========================================================================

    logic proc_start;
    logic proc_busy;
    logic proc_done;
    logic signed [FP_TOTAL-1:0] proc_x_in, proc_y_in, proc_angle_in;
    logic signed [FP_TOTAL-1:0] proc_x_out, proc_y_out, proc_angle_out;
    logic proc_valid_out;
    logic [9:0] proc_trail_read_x, proc_trail_write_x;
    logic [8:0] proc_trail_read_y, proc_trail_write_y;
    logic signed [FP_TOTAL-1:0] proc_trail_write_data;
    logic proc_trail_read_en, proc_trail_write_en;
    logic proc_lfsr_en;

    // Latched processor outputs (captured when proc_done=1)
    logic signed [FP_TOTAL-1:0] latched_x_out, latched_y_out, latched_angle_out;
    logic latched_valid;

    // Previous agent index for write-back
    logic [AGENT_COUNT_LOG-1:0] prev_idx;

    // Extract LFSR bit
    logic lfsr_bit;
    assign lfsr_bit = lfsr_state[0];

    // =========================================================================
    // Agent Processor Instance
    // =========================================================================

    agent_processor #(
        .FP_INT_BITS(FP_INT_BITS),
        .FP_FRAC_BITS(FP_FRAC_BITS),
        .FP_TOTAL(FP_TOTAL),
        .TRIG_BITS(TRIG_BITS),
        .WIDTH(WIDTH),
        .HEIGHT(HEIGHT)
    ) u_processor (
        .clk(clk),
        .rst_n(rst_n),
        .start(proc_start),
        .sensor_angle(sensor_angle),
        .sensor_distance(sensor_distance),
        .turn_speed(turn_speed),
        .move_speed(move_speed),
        .deposit_amount(deposit_amount),
        .busy(proc_busy),
        .done(proc_done),
        .agent_x_in(proc_x_in),
        .agent_y_in(proc_y_in),
        .agent_angle_in(proc_angle_in),
        .agent_x_out(proc_x_out),
        .agent_y_out(proc_y_out),
        .agent_angle_out(proc_angle_out),
        .agent_valid_out(proc_valid_out),
        .trail_read_x(proc_trail_read_x),
        .trail_read_y(proc_trail_read_y),
        .trail_read_en(proc_trail_read_en),
        .trail_read_data({{(FP_TOTAL-18){1'b0}}, trail_data_b_out}),  // Extend to 25-bit
        .trail_read_valid(1'b1),
        .trail_write_x(proc_trail_write_x),
        .trail_write_y(proc_trail_write_y),
        .trail_write_data(proc_trail_write_data),
        .trail_write_en(proc_trail_write_en),
        .lfsr_en(proc_lfsr_en),
        .lfsr_bit(lfsr_bit)
    );

    // =========================================================================
    // Agent Memory Initialization
    // =========================================================================

    initial begin
        int i;
        logic signed [FP_TOTAL-1:0] angle, cx, cy, x, y, radius_fp;

        // Center canvas
        cx = (WIDTH * FP_SCALE) / 2;
        cy = (HEIGHT * FP_SCALE) / 2;

        // Initialize agents on circle (40% radius)
        radius_fp = (WIDTH * FP_SCALE) / 5;

        for (i = 0; i < NUM_AGENTS; i = i + 1) begin
            // Angle around circle: 0 to 2π
            angle = (i * 2 * 32'd3141593) / NUM_AGENTS;  // Approximate 2π/NUM_AGENTS

            // Position: x = cx + r*cos(θ), y = cy + r*sin(θ)
            // For now, use simple linear distribution on circle perimeter
            x = cx + (radius_fp / 2) * (i % 2 ? 1 : -1);
            y = cy + (radius_fp / 2) * (i / 2 % 2 ? 1 : -1);

            agent_x[i] = x;
            agent_y[i] = y;
            agent_angle[i] = angle;
        end
    end

    // =========================================================================
    // State Machine
    // =========================================================================

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            current_agent_idx <= '0;
            step_counter <= '0;
            latched_valid <= 1'b0;  // CRITICAL: Initialize latched_valid to prevent spurious write-backs
        end else begin
            // DEBUG: Print state transitions (simplified without .name())
            if (state != next_state) begin
                $display("[COORD] State transition (cycle=%0d): %0d -> %0d",
                    $time / 10, state, next_state);
            end

            state <= next_state;

            case (state)
                IDLE: begin
                    current_agent_idx <= '0;
                    step_counter <= '0;
                    if (next_state == INITIALIZE) begin
                        $display("[COORD] Entering INITIALIZE state");
                    end
                end

                INITIALIZE: begin
                    current_agent_idx <= '0;
                    step_counter <= '0;
                    if (next_state == RUNNING) begin
                        $display("[COORD] Entering RUNNING state (will process agents)");
                    end
                end

                RUNNING: begin
                    // Write back results from previous agent (latched on last cycle)
                    if (latched_valid) begin
                        prev_idx = (current_agent_idx == 0) ? (NUM_AGENTS - 1) : (current_agent_idx - 1'b1);
                        $display("[COORD] Writing back agent[%0d]: x=%0d y=%0d angle=%0d",
                            prev_idx, latched_x_out, latched_y_out, latched_angle_out);
                        agent_x[prev_idx] <= latched_x_out;
                        agent_y[prev_idx] <= latched_y_out;
                        agent_angle[prev_idx] <= latched_angle_out;
                        latched_valid <= 1'b0;
                    end

                    if (!pause && proc_done) begin
                        // Latch processor outputs
                        $display("[COORD] Processor done for agent[%0d], latching outputs x=%0d y=%0d angle=%0d",
                            current_agent_idx, proc_x_out, proc_y_out, proc_angle_out);
                        latched_x_out <= proc_x_out;
                        latched_y_out <= proc_y_out;
                        latched_angle_out <= proc_angle_out;
                        latched_valid <= 1'b1;

                        // Move to next agent
                        if (current_agent_idx < NUM_AGENTS - 1) begin
                            current_agent_idx <= current_agent_idx + 1'b1;
                            $display("[COORD] Advancing to agent[%0d]", current_agent_idx + 1);
                        end else begin
                            current_agent_idx <= '0;
                            step_counter <= step_counter + 1'b1;
                            $display("[COORD] Completed step %0d, resetting to agent[0]", step_counter);
                        end
                    end
                end

                DONE_STATE: begin
                    // Stay in DONE
                end

                default: state <= IDLE;
            endcase
        end
    end

    // Next state logic
    always_comb begin
        next_state = state;

        case (state)
            IDLE: begin
                if (start) next_state = INITIALIZE;
            end

            INITIALIZE: begin
                next_state = RUNNING;
            end

            RUNNING: begin
                // Run until stopped
                next_state = RUNNING;
            end

            DONE_STATE: begin
                next_state = DONE_STATE;
            end

            default: next_state = IDLE;
        endcase
    end

    // =========================================================================
    // Processor Input Mux
    // =========================================================================

    assign proc_start = (state == RUNNING) && !pause && !proc_busy;
    assign proc_x_in = agent_x[current_agent_idx];
    assign proc_y_in = agent_y[current_agent_idx];
    assign proc_angle_in = agent_angle[current_agent_idx];

    // DEBUG: Monitor processor start
    always_ff @(posedge clk) begin
        if (proc_start) begin
            $display("[COORD] Starting processor for agent[%0d]: x=%0d y=%0d angle=%0d (busy=%0b)",
                current_agent_idx, proc_x_in, proc_y_in, proc_angle_in, proc_busy);
        end
    end

    // =========================================================================
    // Trail Memory Interface
    // Priority: Processor write > Processor read
    // =========================================================================

    logic [9:0] read_x, write_x;
    logic [8:0] read_y, write_y;
    logic [18:0] read_addr, write_addr;

    // Wrap coordinates to valid canvas
    assign read_x = proc_trail_read_x % WIDTH;
    assign read_y = proc_trail_read_y % HEIGHT;
    assign write_x = proc_trail_write_x % WIDTH;
    assign write_y = proc_trail_write_y % HEIGHT;

    // Address calculation
    assign read_addr = (read_y * WIDTH) + read_x;
    assign write_addr = (write_y * WIDTH) + write_x;

    // Mux: prioritize write
    // Trail memory stores full fixed-point values (18 bits) to match Python
    // Python deposits 5.0 * 4096 = 20480 in fixed-point format
    // RTL should do the same, not scale down to integers
    logic [17:0] trail_write_fp;
    assign trail_write_fp = proc_trail_write_data[17:0];  // Use lower 18 bits of 25-bit fixed-point

    assign trail_addr_b = proc_trail_write_en ? write_addr : read_addr;
    assign trail_data_b_in = proc_trail_write_en ? trail_write_fp : 18'h0;
    assign trail_we_b = proc_trail_write_en;

    // DEBUG: Monitor trail writes
    always_ff @(posedge clk) begin
        if (proc_trail_write_en) begin
            $display("[COORD] Trail write: addr=%0d (%0d,%0d) data=%0d (from agent[%0d])",
                write_addr, write_x, write_y, trail_write_fp, current_agent_idx);
        end
    end

    // =========================================================================
    // Output
    // =========================================================================

    assign done = (state == DONE_STATE);

endmodule
