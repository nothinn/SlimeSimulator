// Agent Orchestrator - Manages pipelined agent processing

module agent_orchestrator #(
    parameter NUM_AGENTS = 100,
    parameter FP_INT_BITS = 12,
    parameter FP_FRAC_BITS = 12,
    parameter FP_TOTAL = 25,
    parameter TRIG_BITS = 10,
    parameter WIDTH = 160,
    parameter HEIGHT = 120
) (
    input  logic clk,
    input  logic rst_n,
    input  logic start,
    input  logic signed [FP_TOTAL-1:0] sensor_angle,
    input  logic signed [FP_TOTAL-1:0] sensor_distance,
    input  logic signed [FP_TOTAL-1:0] turn_speed,
    input  logic signed [FP_TOTAL-1:0] move_speed,
    input  logic signed [FP_TOTAL-1:0] deposit_amount,
    output logic done,
    input  logic [31:0] lfsr_state,
    output logic [18:0] trail_addr_b,
    output logic [7:0]  trail_data_b_in,
    output logic        trail_we_b,
    input  logic [7:0]  trail_data_b_out
);

    typedef enum logic [1:0] {
        IDLE = 2'b00,
        RUNNING = 2'b01,
        DONE = 2'b10,
        UNUSED = 2'b11
    } state_t;

    state_t state, next_state;
    logic [19:0] agent_idx;
    logic [19:0] trail_addr_counter;
    logic [15:0] frame_counter;
    logic [7:0] deposit_amount_scaled;

    // Convert fixed-point deposit_amount to 8-bit integer (Q12.12 >> 12)
    assign deposit_amount_scaled = deposit_amount[19:12];

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            agent_idx <= '0;
            trail_addr_counter <= '0;
            frame_counter <= '0;
        end else begin
            state <= next_state;

            if (state == RUNNING) begin
                if (agent_idx < NUM_AGENTS - 1) begin
                    agent_idx <= agent_idx + 1'b1;
                end else begin
                    agent_idx <= '0;
                end

                if (trail_addr_counter < (WIDTH * HEIGHT - 1)) begin
                    trail_addr_counter <= trail_addr_counter + 1'b1;
                end else begin
                    trail_addr_counter <= '0;
                end
            end

            frame_counter <= frame_counter + 1'b1;
        end
    end

    always_comb begin
        next_state = state;

        case (state)
            IDLE: begin
                if (start) next_state = RUNNING;
            end
            RUNNING: begin
                if (frame_counter == 16'hFFFF) begin
                    next_state = DONE;
                end
            end
            DONE: begin
                next_state = IDLE;
            end
            default: next_state = IDLE;
        endcase
    end

    assign trail_addr_b = trail_addr_counter[18:0];
    assign trail_data_b_in = deposit_amount_scaled;
    assign trail_we_b = (state == RUNNING) ? 1'b1 : 1'b0;
    assign done = (state == DONE) ? 1'b1 : 1'b0;

endmodule
