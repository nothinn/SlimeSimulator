// Agent Simulation Testbench Wrapper
// Integrates agent processor with trail memory for cocotb testing
// Simplified for verification against Python model

module agent_sim_tb #(
    parameter NUM_AGENTS = 10,
    parameter WIDTH = 64,
    parameter HEIGHT = 64,
    parameter FP_INT_BITS = 12,
    parameter FP_FRAC_BITS = 12,
    parameter LFSR_WIDTH = 32
) (
    input logic clk,
    input logic rst_n,

    // Control
    input logic run_step,          // Pulse to run one simulation step
    output logic step_done,

    // Configuration
    input logic [24:0] move_speed_in,
    input logic [24:0] turn_speed_in,
    input logic [24:0] sensor_angle_in,
    input logic [24:0] sensor_distance_in,

    // LFSR seed
    input logic load_lfsr,
    input logic [31:0] lfsr_seed,

    // Agent initialization
    input logic init_agents,
    input logic [24:0] init_x,
    input logic [24:0] init_y,
    input logic [9:0] init_angle_idx,

    // Trail map read interface (for extraction)
    input logic [15:0] trail_read_addr,
    output logic [7:0] trail_read_data
);

    localparam FP_TOTAL = FP_INT_BITS + FP_FRAC_BITS + 1;
    localparam TRAIL_SIZE = WIDTH * HEIGHT;
    localparam AGENT_ADDR_BITS = $clog2(NUM_AGENTS);
    localparam TRAIL_ADDR_BITS = $clog2(TRAIL_SIZE);

    // =========================================================================
    // LFSR
    // =========================================================================
    logic [LFSR_WIDTH-1:0] lfsr_state;
    logic lfsr_enable;

    lfsr #(
        .WIDTH(LFSR_WIDTH),
        .SEED(32'hDEADBEEF)
    ) u_lfsr (
        .clk(clk),
        .rst_n(rst_n),
        .enable(lfsr_enable),
        .load(load_lfsr),
        .seed_val(lfsr_seed),
        .lfsr_out(lfsr_state),
        .valid()
    );

    // =========================================================================
    // Trail Map Memory
    // =========================================================================
    logic [7:0] trail_mem [0:TRAIL_SIZE-1];
    logic [TRAIL_ADDR_BITS-1:0] trail_write_addr;
    logic [7:0] trail_write_data_in;
    logic trail_write_en;
    logic [TRAIL_ADDR_BITS-1:0] trail_proc_read_addr;
    logic [7:0] trail_proc_read_data;

    // Write port
    always_ff @(posedge clk) begin
        if (trail_write_en) begin
            // Saturating add for trail deposit
            if (trail_mem[trail_write_addr] + trail_write_data_in > 255)
                trail_mem[trail_write_addr] <= 8'hFF;
            else
                trail_mem[trail_write_addr] <= trail_mem[trail_write_addr] + trail_write_data_in;
        end
    end

    // Read port for processor
    always_ff @(posedge clk) begin
        trail_proc_read_data <= trail_mem[trail_proc_read_addr];
    end

    // Read port for extraction
    assign trail_read_data = trail_mem[trail_read_addr[TRAIL_ADDR_BITS-1:0]];

    // =========================================================================
    // Agent Memory
    // =========================================================================
    typedef struct packed {
        logic signed [FP_TOTAL-1:0] x;
        logic signed [FP_TOTAL-1:0] y;
        logic signed [FP_TOTAL-1:0] angle;
    } agent_t;

    agent_t agent_mem [0:NUM_AGENTS-1];
    logic [AGENT_ADDR_BITS-1:0] current_agent_idx;
    agent_t current_agent;

    // Agent memory read/write
    integer i;
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (i = 0; i < NUM_AGENTS; i = i + 1) begin
                agent_mem[i].x <= '0;
                agent_mem[i].y <= '0;
                agent_mem[i].angle <= '0;
            end
        end
        else if (init_agents) begin
            // Initialize all agents to same position
            for (i = 0; i < NUM_AGENTS; i = i + 1) begin
                agent_mem[i].x <= init_x;
                agent_mem[i].y <= init_y;
                agent_mem[i].angle <= {{(FP_TOTAL-10){1'b0}}, init_angle_idx};
            end
        end
        else if (agent_valid_out) begin
            // Write back updated agent
            agent_mem[current_agent_idx].x <= agent_x_out;
            agent_mem[current_agent_idx].y <= agent_y_out;
            agent_mem[current_agent_idx].angle <= agent_angle_out;
        end
    end

    // =========================================================================
    // Agent Processor
    // =========================================================================
    logic proc_start, proc_done, proc_busy;
    logic signed [FP_TOTAL-1:0] agent_x_in, agent_y_in, agent_angle_in;
    logic signed [FP_TOTAL-1:0] agent_x_out, agent_y_out, agent_angle_out;
    logic agent_valid_out;

    logic [9:0] trail_read_x;
    logic [8:0] trail_read_y;
    logic trail_read_en;
    logic [FP_TOTAL-1:0] trail_read_data_fp;
    logic trail_read_valid;

    logic [9:0] trail_write_x;
    logic [8:0] trail_write_y;
    logic [FP_TOTAL-1:0] trail_write_data_fp;
    logic trail_write_en_proc;

    agent_processor #(
        .FP_INT_BITS(FP_INT_BITS),
        .FP_FRAC_BITS(FP_FRAC_BITS),
        .WIDTH(WIDTH),
        .HEIGHT(HEIGHT)
    ) u_agent_proc (
        .clk(clk),
        .rst_n(rst_n),
        .start(proc_start),
        .busy(proc_busy),
        .done(proc_done),

        .sensor_angle(sensor_angle_in),
        .sensor_distance(sensor_distance_in),
        .turn_speed(turn_speed_in),
        .move_speed(move_speed_in),
        .deposit_amount({FP_TOTAL{1'b0}} | 25'd5),  // Deposit 5

        .agent_x_in(agent_x_in),
        .agent_y_in(agent_y_in),
        .agent_angle_in(agent_angle_in),

        .agent_x_out(agent_x_out),
        .agent_y_out(agent_y_out),
        .agent_angle_out(agent_angle_out),
        .agent_valid_out(agent_valid_out),

        .trail_read_x(trail_read_x),
        .trail_read_y(trail_read_y),
        .trail_read_en(trail_read_en),
        .trail_read_data(trail_read_data_fp),
        .trail_read_valid(trail_read_valid),

        .trail_write_x(trail_write_x),
        .trail_write_y(trail_write_y),
        .trail_write_data(trail_write_data_fp),
        .trail_write_en(trail_write_en_proc),

        .lfsr_en(lfsr_enable),
        .lfsr_bit(lfsr_state[0])
    );

    // Trail memory address translation
    assign trail_proc_read_addr = trail_read_y[TRAIL_ADDR_BITS-1:0] * WIDTH + trail_read_x[TRAIL_ADDR_BITS-1:0];
    assign trail_read_data_fp = {17'b0, trail_proc_read_data};
    assign trail_read_valid = 1'b1;  // Assume 1 cycle latency

    assign trail_write_addr = trail_write_y[TRAIL_ADDR_BITS-1:0] * WIDTH + trail_write_x[TRAIL_ADDR_BITS-1:0];
    assign trail_write_data_in = trail_write_data_fp[7:0];
    assign trail_write_en = trail_write_en_proc;

    // Agent fetch
    assign agent_x_in = agent_mem[current_agent_idx].x;
    assign agent_y_in = agent_mem[current_agent_idx].y;
    assign agent_angle_in = agent_mem[current_agent_idx].angle;

    // =========================================================================
    // Control State Machine
    // =========================================================================
    typedef enum logic [2:0] {
        IDLE,
        PROCESS_AGENT,
        WAIT_AGENT_DONE,
        DIFFUSE,  // TODO: implement diffusion
        STEP_COMPLETE
    } ctrl_state_t;

    ctrl_state_t ctrl_state;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            ctrl_state <= IDLE;
            current_agent_idx <= '0;
            proc_start <= 1'b0;
            step_done <= 1'b0;
        end
        else begin
            proc_start <= 1'b0;
            step_done <= 1'b0;

            case (ctrl_state)
                IDLE: begin
                    if (run_step) begin
                        current_agent_idx <= '0;
                        ctrl_state <= PROCESS_AGENT;
                    end
                end

                PROCESS_AGENT: begin
                    proc_start <= 1'b1;
                    ctrl_state <= WAIT_AGENT_DONE;
                end

                WAIT_AGENT_DONE: begin
                    if (proc_done) begin
                        if (current_agent_idx == NUM_AGENTS - 1) begin
                            ctrl_state <= DIFFUSE;
                        end
                        else begin
                            current_agent_idx <= current_agent_idx + 1'b1;
                            ctrl_state <= PROCESS_AGENT;
                        end
                    end
                end

                DIFFUSE: begin
                    // TODO: implement trail diffusion and decay
                    ctrl_state <= STEP_COMPLETE;
                end

                STEP_COMPLETE: begin
                    step_done <= 1'b1;
                    ctrl_state <= IDLE;
                end

                default: ctrl_state <= IDLE;
            endcase
        end
    end

endmodule
