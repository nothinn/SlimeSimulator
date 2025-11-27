// Minimal syntax test for agent_coordinator.sv
module test_coordinator_syntax;
    logic clk, rst_n, start, pause;
    logic [31:0] lfsr_state;
    logic [24:0] sensor_angle, sensor_distance, turn_speed, move_speed, deposit_amount;
    logic [17:0] trail_data_b_out;
    logic [18:0] trail_addr_b;
    logic [17:0] trail_data_b_in;
    logic trail_we_b, done;

    agent_coordinator #(
        .NUM_AGENTS(10),
        .FP_INT_BITS(12),
        .FP_FRAC_BITS(12),
        .FP_TOTAL(25),
        .TRIG_BITS(10),
        .WIDTH(320),
        .HEIGHT(240)
    ) dut (
        .clk(clk),
        .rst_n(rst_n),
        .start(start),
        .pause(pause),
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
        .done(done)
    );
endmodule
