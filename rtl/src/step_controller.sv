// Step Controller - Synchronous stepping interface for agent simulation
//
// Provides step-based control where:
// - Each pulse on step_request processes one complete simulation step
// - step_ready indicates when the step is complete and outputs are stable
// - All agent states are stable for reading when step_ready=1
//
// This decouples the simulation from the main clock frequency, allowing
// for slow stepping and guaranteeing stable readout.

module step_controller #(
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

    // Step-based control interface
    input  logic step_request,          // Pulse to start one simulation step
    output logic step_ready,            // 1 when step complete and outputs stable
    output logic step_busy,             // 1 while processing a step
    output logic [31:0] step_count,     // Number of steps completed

    // Control parameters (stable during step)
    input  logic signed [FP_TOTAL-1:0] sensor_angle,
    input  logic signed [FP_TOTAL-1:0] sensor_distance,
    input  logic signed [FP_TOTAL-1:0] turn_speed,
    input  logic signed [FP_TOTAL-1:0] move_speed,
    input  logic signed [FP_TOTAL-1:0] deposit_amount,
    input  logic [31:0] lfsr_state,

    // Trail map interface
    input  logic [17:0] trail_data_b_out,
    output logic [18:0] trail_addr_b,
    output logic [17:0] trail_data_b_in,
    output logic trail_we_b,

    // Agent debug interface (for stable readout when step_ready=1)
    input  logic [9:0]  debug_agent_idx,
    input  logic [1:0]  debug_agent_sel,
    output logic signed [FP_TOTAL-1:0] debug_agent_data,

    // Agent initialization interface
    input  logic debug_agent_write_en,
    input  logic signed [FP_TOTAL-1:0] debug_agent_data_write
);

    // =========================================================================
    // Internal State Machine
    // =========================================================================

    typedef enum logic [2:0] {
        STEP_IDLE,           // Waiting for step_request pulse
        STEP_STARTING,       // Starting coordinator for one step
        STEP_PROCESSING,     // Waiting for all agents to process
        STEP_STABILIZING,    // Waiting for outputs to settle
        STEP_DONE            // Outputs are stable, ready to read
    } step_state_t;

    step_state_t step_state, next_step_state;

    // Coordinator control signals
    logic coord_start;
    logic coord_pause;
    logic coord_done;
    logic coord_step_complete;  // Signal from coordinator indicating all agents processed

    // Cycle counters
    logic [31:0] processing_cycles;
    logic [31:0] stabilize_cycles;
    logic step_request_prev;
    logic prev_step_count;

    // Calculate cycles needed: NUM_AGENTS * agent_processing_time
    // Account for: agent processor latency (19 cycles) + trail memory access + write-back
    // With memory contention and pipelining, use empirical measurement: ~300 cycles/agent in real hardware
    // For 1000 agents: expect ~300,000 cycles minimum per step
    // For 10 agents: expect ~3000 cycles minimum per step
    // Use conservative margin: (NUM_AGENTS * 300) + 1000
    localparam AGENT_PROCESS_CYCLES = (NUM_AGENTS < 50) ? ((NUM_AGENTS * 300) + 1000) : ((NUM_AGENTS * 300) + 2000);
    localparam SETTLE_TIME = 100;  // Wait for memory operations to settle

    // =========================================================================
    // Agent Coordinator Instance (unchanged from original)
    // =========================================================================

    agent_coordinator #(
        .NUM_AGENTS(NUM_AGENTS),
        .FP_INT_BITS(FP_INT_BITS),
        .FP_FRAC_BITS(FP_FRAC_BITS),
        .FP_TOTAL(FP_TOTAL),
        .TRIG_BITS(TRIG_BITS),
        .WIDTH(WIDTH),
        .HEIGHT(HEIGHT)
    ) u_coordinator (
        .clk(clk),
        .rst_n(rst_n),
        .start(coord_start),
        .pause(coord_pause),
        .lfsr_state(lfsr_state),
        .sensor_angle(sensor_angle),
        .sensor_distance(sensor_distance),
        .turn_speed(turn_speed),
        .move_speed(move_speed),
        .deposit_amount(deposit_amount),
        .trail_data_b_out(trail_data_b_out),
        .trail_addr_b(trail_addr_b),
        .trail_data_b_in(trail_data_b_in),
        .trail_we_b(trail_we_b),
        .lfsr_en_request(),  // Not used in step mode
        .done(coord_done),
        .step_complete_pulse(coord_step_complete),  // Signal when all agents complete processing
        .debug_agent_idx(debug_agent_idx),
        .debug_agent_sel(debug_agent_sel),
        .debug_agent_data(debug_agent_data),
        .debug_agent_write_en(debug_agent_write_en),
        .debug_agent_data_write(debug_agent_data_write)
    );

    // =========================================================================
    // Step Control State Machine
    // =========================================================================

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            step_state <= STEP_IDLE;
            processing_cycles <= '0;
            stabilize_cycles <= '0;
            step_count <= '0;
            step_request_prev <= 1'b0;
        end else begin
            step_state <= next_step_state;
            step_request_prev <= step_request;

            case (step_state)
                STEP_IDLE: begin
                    // Do nothing, wait for pulse
                    processing_cycles <= '0;
                    stabilize_cycles <= '0;
                end

                STEP_STARTING: begin
                    // Coordinator should have started, transition to processing
                    processing_cycles <= '0;
                end

                STEP_PROCESSING: begin
                    // Count cycles while agents are being processed
                    processing_cycles <= processing_cycles + 1'b1;
                end

                STEP_STABILIZING: begin
                    // Count cycles for output settling
                    stabilize_cycles <= stabilize_cycles + 1'b1;
                end

                STEP_DONE: begin
                    // Increment step counter when outputs are stable
                    step_count <= step_count + 1'b1;
                    processing_cycles <= '0;
                    stabilize_cycles <= '0;
                end

                default: step_state <= STEP_IDLE;
            endcase
        end
    end

    // Next state logic
    always_comb begin
        next_step_state = step_state;
        coord_start = 1'b0;
        coord_pause = 1'b0;
        step_busy = 1'b0;
        step_ready = 1'b0;

        case (step_state)
            STEP_IDLE: begin
                step_ready = 1'b1;  // Ready to accept next step
                step_busy = 1'b0;

                // Detect rising edge on step_request
                if (step_request && !step_request_prev) begin
                    next_step_state = STEP_STARTING;
                    coord_start = 1'b1;
                end
            end

            STEP_STARTING: begin
                step_busy = 1'b1;
                step_ready = 1'b0;
                // Transition immediately to processing (coordinator has latched start)
                next_step_state = STEP_PROCESSING;
            end

            STEP_PROCESSING: begin
                step_busy = 1'b1;
                step_ready = 1'b0;

                // Wait for step_complete_pulse from agent_coordinator
                // This signals that all NUM_AGENTS have been processed for this step
                // As a fallback, also use cycle counting (for safety margin)
                if (coord_step_complete || (processing_cycles >= AGENT_PROCESS_CYCLES)) begin
                    next_step_state = STEP_STABILIZING;
                end
            end

            STEP_STABILIZING: begin
                step_busy = 1'b1;
                step_ready = 1'b0;
                coord_pause = 1'b1;  // Pause coordinator to prevent next step

                // Wait for settling time
                if (stabilize_cycles >= SETTLE_TIME) begin
                    next_step_state = STEP_DONE;
                end
            end

            STEP_DONE: begin
                step_busy = 1'b0;
                step_ready = 1'b1;  // Outputs stable, safe to read
                coord_pause = 1'b1;  // Keep paused until next step

                // Wait for step_request to be released before accepting next pulse
                if (!step_request) begin
                    next_step_state = STEP_IDLE;
                end
            end

            default: begin
                step_ready = 1'b0;
                step_busy = 1'b0;
            end
        endcase
    end

endmodule
