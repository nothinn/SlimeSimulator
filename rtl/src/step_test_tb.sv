// Step Test Testbench - Instantiates step_controller with trail memory for testing

module step_test_tb #(
    parameter WIDTH = 320,
    parameter HEIGHT = 240,
    parameter NUM_AGENTS = 100,
    parameter FP_INT_BITS = 12,
    parameter FP_FRAC_BITS = 12,
    parameter FP_TOTAL = FP_INT_BITS + FP_FRAC_BITS + 1
) (
    input  logic clk,
    input  logic rst_n,
    input  logic step_request,
    output logic step_ready,
    output logic step_busy,
    output logic [31:0] step_count,

    // Control parameters
    input  logic signed [FP_TOTAL-1:0] sensor_angle,
    input  logic signed [FP_TOTAL-1:0] sensor_distance,
    input  logic signed [FP_TOTAL-1:0] turn_speed,
    input  logic signed [FP_TOTAL-1:0] move_speed,
    input  logic signed [FP_TOTAL-1:0] deposit_amount,
    input  logic [31:0] lfsr_state,

    // Agent debug interface
    input  logic [9:0]  debug_agent_idx,
    input  logic [1:0]  debug_agent_sel,
    output logic signed [FP_TOTAL-1:0] debug_agent_data,

    // Agent initialization interface
    input  logic debug_agent_write_en,
    input  logic signed [FP_TOTAL-1:0] debug_agent_data_write
);

    // Trail memory (320×240 = 76,800 entries × 18 bits)
    localparam TRAIL_DEPTH = WIDTH * HEIGHT;
    logic [17:0] trail_mem [TRAIL_DEPTH];

    // Trail interface signals
    logic [18:0] trail_addr_read, trail_addr_write;
    logic [17:0] trail_data_read, trail_data_write;
    logic trail_we;

    // Dual-port RAM for trail (read/write)
    always_ff @(posedge clk) begin
        if (trail_we) begin
            trail_mem[trail_addr_write] <= trail_data_write;
        end
    end

    assign trail_data_read = trail_mem[trail_addr_read];

    // =========================================================================
    // Step Controller Instance
    // =========================================================================

    step_controller #(
        .NUM_AGENTS(NUM_AGENTS),
        .FP_INT_BITS(FP_INT_BITS),
        .FP_FRAC_BITS(FP_FRAC_BITS),
        .FP_TOTAL(FP_TOTAL),
        .TRIG_BITS(10),
        .WIDTH(WIDTH),
        .HEIGHT(HEIGHT)
    ) u_step_controller (
        .clk(clk),
        .rst_n(rst_n),
        .step_request(step_request),
        .step_ready(step_ready),
        .step_busy(step_busy),
        .step_count(step_count),
        .sensor_angle(sensor_angle),
        .sensor_distance(sensor_distance),
        .turn_speed(turn_speed),
        .move_speed(move_speed),
        .deposit_amount(deposit_amount),
        .lfsr_state(lfsr_state),
        .trail_data_b_out(trail_data_read),
        .trail_addr_b(trail_addr_write),
        .trail_data_b_in(trail_data_write),
        .trail_we_b(trail_we),
        .debug_agent_idx(debug_agent_idx),
        .debug_agent_sel(debug_agent_sel),
        .debug_agent_data(debug_agent_data),
        .debug_agent_write_en(debug_agent_write_en),
        .debug_agent_data_write(debug_agent_data_write)
    );

    // Trail address is output from step_controller
    assign trail_addr_read = trail_addr_write;

endmodule
