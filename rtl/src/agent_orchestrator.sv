// Agent Orchestrator
// Manages agent memory and coordinates with agent processor
// Handles agent state for multiple agents and serializes processing

module agent_orchestrator #(
    parameter NUM_AGENTS   = 100,  // Start with fewer agents for testing
    parameter FP_INT_BITS  = 12,
    parameter FP_FRAC_BITS = 12,
    parameter FP_TOTAL     = FP_INT_BITS + FP_FRAC_BITS + 1,  // 25 bits
    parameter TRIG_BITS    = 10,
    parameter WIDTH        = 160,
    parameter HEIGHT       = 120
) (
    input  logic clk,
    input  logic rst_n,

    // Control
    input  logic start,
    input  logic [FP_TOTAL-1:0] sensor_angle,
    input  logic [FP_TOTAL-1:0] sensor_distance,
    input  logic [FP_TOTAL-1:0] turn_speed,
    input  logic [FP_TOTAL-1:0] move_speed,
    input  logic [FP_TOTAL-1:0] deposit_amount,
    output logic done,

    // LFSR interface
    input  logic [31:0] lfsr_state,

    // Trail map interface (Port A: VGA reads, Port B: agent writes)
    output logic [18:0] trail_addr_b,
    output logic [7:0]  trail_data_b_in,
    output logic        trail_we_b,
    input  logic [7:0]  trail_data_b_out
);

    // Agent storage: position (x, y) and angle for each agent
    // Using separate arrays for x, y, angle to simplify synthesis
    logic signed [FP_TOTAL-1:0] agent_x_mem [0:NUM_AGENTS-1];
    logic signed [FP_TOTAL-1:0] agent_y_mem [0:NUM_AGENTS-1];
    logic signed [FP_TOTAL-1:0] agent_angle_mem [0:NUM_AGENTS-1];

    // Current agent index
    logic [$clog2(NUM_AGENTS)-1:0] current_agent;
    logic [$clog2(NUM_AGENTS)-1:0] next_agent;

    // Fixed-point constants
    localparam FP_SCALE = 1 << FP_FRAC_BITS;
    localparam signed [FP_TOTAL-1:0] WIDTH_FP = FP_TOTAL'(WIDTH * FP_SCALE);
    localparam signed [FP_TOTAL-1:0] HEIGHT_FP = FP_TOTAL'(HEIGHT * FP_SCALE);

    // State machine
    typedef enum logic [2:0] {
        IDLE,
        INIT_AGENTS,
        PROCESSING,
        DONE_STATE
    } state_t;

    state_t state;

    // Initialize agents in a pattern across the screen
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            current_agent <= '0;
        end
        else begin
            case (state)
                IDLE: begin
                    if (start) begin
                        state <= INIT_AGENTS;
                        current_agent <= '0;
                    end
                end

                INIT_AGENTS: begin
                    // Initialize agents with positions spread across screen
                    // and random angles from LFSR
                    agent_x_mem[current_agent] <= ((current_agent % 16) * (WIDTH_FP >> 4));  // Spread horizontally
                    agent_y_mem[current_agent] <= ((current_agent / 16) * (HEIGHT_FP >> 3)); // Spread vertically
                    agent_angle_mem[current_agent] <= {{(FP_TOTAL-8){lfsr_state[7]}}, lfsr_state[7:0]};

                    if (current_agent == NUM_AGENTS - 1) begin
                        state <= PROCESSING;
                        current_agent <= '0;
                    end
                    else begin
                        current_agent <= current_agent + 1'b1;
                    end
                end

                PROCESSING: begin
                    // Process agents: update position and deposit trail
                    // For now, simple movement and trail deposition

                    // Get agent state
                    logic signed [FP_TOTAL-1:0] agent_x = agent_x_mem[current_agent];
                    logic signed [FP_TOTAL-1:0] agent_y = agent_y_mem[current_agent];
                    logic signed [FP_TOTAL-1:0] agent_angle = agent_angle_mem[current_agent];

                    // Simple update: move in direction of angle
                    // For now, just rotate and deposit trail
                    agent_angle_mem[current_agent] <= agent_angle + {{(FP_TOTAL-16){1'b0}}, 16'h0800};  // Small rotation

                    // Deposit trail at current position
                    trail_addr_b <= (agent_y >>> FP_FRAC_BITS) * WIDTH + (agent_x >>> FP_FRAC_BITS);
                    trail_data_b_in <= (lfsr_state[7:0] + {{(8-$clog2(NUM_AGENTS)){1'b0}}, current_agent}) >> 1;
                    trail_we_b <= 1'b1;

                    if (current_agent == NUM_AGENTS - 1) begin
                        state <= PROCESSING;  // Loop continuously
                        current_agent <= '0;
                    end
                    else begin
                        current_agent <= current_agent + 1'b1;
                    end
                end

                default: state <= IDLE;
            endcase
        end
    end

    assign done = (state == DONE_STATE);

endmodule
