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

    // FIX #3: Export LFSR enable signal for synchronized stepping
    output logic lfsr_en_request,

    output logic done,
    output logic step_complete_pulse,  // Pulses when all agents finished processing for one step

    // Agent debug interface (for initialization validation)
    input  logic [9:0]  debug_agent_idx,     // Agent index (0-999)
    input  logic [1:0]  debug_agent_sel,     // 0=x, 1=y, 2=angle
    output logic signed [FP_TOTAL-1:0] debug_agent_data,    // Agent state output

    // Agent initialization write interface
    input  logic debug_agent_write_en,                        // Write enable
    input  logic signed [FP_TOTAL-1:0] debug_agent_data_write // Data to write
);

    // Fixed-point scale
    localparam FP_SCALE = 1 << FP_FRAC_BITS;
    localparam AGENT_COUNT_LOG = $clog2(NUM_AGENTS);

    // =========================================================================
    // Agent Memory (distributed RAM blocks)
    // Store: x (25b), y (25b), angle (25b) per agent = 75 bits × 1000 = ~75KB
    // =========================================================================

    // Force BRAM inference for agent memory arrays (critical for resource usage)
    (* ram_style = "block" *) logic signed [FP_TOTAL-1:0] agent_x [NUM_AGENTS];
    (* ram_style = "block" *) logic signed [FP_TOTAL-1:0] agent_y [NUM_AGENTS];
    (* ram_style = "block" *) logic signed [FP_TOTAL-1:0] agent_angle [NUM_AGENTS];

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

    // Step completion tracking
    logic step_just_completed;
    logic step_freeze_cycle;  // Freeze for one cycle after step completes to prevent double-processing
    logic step_writeback_cycle;  // Delayed pulse - fires AFTER last agent write-back completes

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
    // NOTE: Agents are initialized by the testbench via debug interface
    // RTL initialization is disabled to avoid compilation issues
    // =========================================================================

    // All agents initialized to (0,0) with angle 0
    // Testbench will write correct values via agent coordinate debug interface
    initial begin
        int i;
        for (i = 0; i < NUM_AGENTS; i = i + 1) begin
            agent_x[i] = '0;
            agent_y[i] = '0;
            agent_angle[i] = '0;
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
            step_freeze_cycle <= 1'b0;
            step_writeback_cycle <= 1'b0;
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
                    // Debug write has priority in INITIALIZE state as well
                    if (debug_agent_write_en) begin
                        case (debug_agent_sel)
                            2'b00: agent_x[debug_idx_safe] <= debug_agent_data_write;
                            2'b01: agent_y[debug_idx_safe] <= debug_agent_data_write;
                            2'b10: agent_angle[debug_idx_safe] <= debug_agent_data_write;
                            default: ; // No-op
                        endcase
                    end
                    current_agent_idx <= '0;
                    step_counter <= '0;
                    if (next_state == RUNNING) begin
                        $display("[COORD] Entering RUNNING state (will process agents)");
                    end
                end

                RUNNING: begin
                    // Debug write has priority over normal write-back
                    if (debug_agent_write_en) begin
                        case (debug_agent_sel)
                            2'b00: agent_x[debug_idx_safe] <= debug_agent_data_write;
                            2'b01: agent_y[debug_idx_safe] <= debug_agent_data_write;
                            2'b10: agent_angle[debug_idx_safe] <= debug_agent_data_write;
                            default: ; // No-op
                        endcase
                    end
                    // Write back results from previous agent (latched on last cycle)
                    else if (latched_valid) begin
                        prev_idx = (current_agent_idx == 0) ? (NUM_AGENTS - 1) : (current_agent_idx - 1'b1);
                        $display("[COORD] Writing back agent[%0d]: x=%0d y=%0d angle=%0d",
                            prev_idx, latched_x_out, latched_y_out, latched_angle_out);
                        agent_x[prev_idx] <= latched_x_out;
                        agent_y[prev_idx] <= latched_y_out;
                        agent_angle[prev_idx] <= latched_angle_out;
                        latched_valid <= 1'b0;

                        // If we just completed the last agent, fire write-back complete pulse
                        // This ensures testbench dumps AFTER agent 999's write-back completes
                        if (step_freeze_cycle) begin
                            step_writeback_cycle <= 1'b1;
                            $display("[COORD] Last agent write-back complete, firing step_complete_pulse");
                        end
                    end else begin
                        // Clear writeback pulse after one cycle
                        step_writeback_cycle <= 1'b0;
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
                            step_just_completed <= 1'b0;
                            step_freeze_cycle <= 1'b0;
                            $display("[COORD] Advancing to agent[%0d]", current_agent_idx + 1);
                        end else begin
                            // Step just completed - freeze for one cycle to prevent double-processing
                            current_agent_idx <= '0;
                            step_counter <= step_counter + 1'b1;
                            step_just_completed <= 1'b1;  // Signal step completion
                            step_freeze_cycle <= 1'b1;    // Prevent next agent from starting this cycle
                            $display("[COORD] Completed step %0d, resetting to agent[0] (freeze 1 cycle)", step_counter);
                        end
                    end else begin
                        step_just_completed <= 1'b0;
                        // Clear freeze after one cycle
                        if (step_freeze_cycle) begin
                            step_freeze_cycle <= 1'b0;
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

    // Don't start next agent if we just completed a step (freeze for 1 cycle)
    assign proc_start = (state == RUNNING) && !pause && !proc_busy && !step_freeze_cycle;
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

    // Coordinates from processor are already in pixel range [0, WIDTH) and [0, HEIGHT)
    // No wrapping needed - just direct assignment
    assign read_x = proc_trail_read_x;
    assign read_y = proc_trail_read_y;
    assign write_x = proc_trail_write_x;
    assign write_y = proc_trail_write_y;

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
    // FIX: Fire pulse AFTER last agent write-back completes (not when last agent finishes processing)
    // This ensures testbench dumps agent 999 AFTER its new values are written to memory
    assign step_complete_pulse = step_writeback_cycle;

    // FIX #3: Export LFSR enable request signal
    assign lfsr_en_request = proc_lfsr_en;

    // =========================================================================
    // Agent Debug Interface - Combinatorial agent memory readback
    // =========================================================================
    // Allow testbench to read agent state for validation without advancing simulation
    // debug_agent_sel: 0=x, 1=y, 2=angle

    logic [AGENT_COUNT_LOG-1:0] debug_idx_safe;
    assign debug_idx_safe = (debug_agent_idx < NUM_AGENTS) ? debug_agent_idx[AGENT_COUNT_LOG-1:0] : '0;

    always_comb begin
        case (debug_agent_sel)
            2'b00:   debug_agent_data = agent_x[debug_idx_safe];
            2'b01:   debug_agent_data = agent_y[debug_idx_safe];
            2'b10:   debug_agent_data = agent_angle[debug_idx_safe];
            default: debug_agent_data = '0;
        endcase
    end

    // =========================================================================
    // Agent Write Interface - Allow testbench to initialize agents
    // =========================================================================
    // Debug writes are now merged into the main state machine always block
    // (in INITIALIZE and RUNNING states) to avoid dual-port RAM inference issues

endmodule
