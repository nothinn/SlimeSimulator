// Slime Simulator Top Level for Basys3
//
// Button mapping:
//   BTNC - Start/Reset simulation
//   BTNU - Speed up
//   BTND - Speed down
//   BTNL - Randomize (new seed)
//   BTNR - (reserved)
//
// Switch mapping:
//   SW[0] - Pause simulation
//
// VGA output: 640x480 @ 60Hz

module slime_top #(
    parameter NUM_AGENTS   = 1000,      // Limited by BRAM
    parameter FP_INT_BITS  = 12,
    parameter FP_FRAC_BITS = 12,
    parameter LFSR_WIDTH   = 32,
    parameter TRIG_BITS    = 10,
    parameter WIDTH        = 640,
    parameter HEIGHT       = 480
) (
    input  logic clk_100mhz,    // 100 MHz system clock
    input  logic rst_n,         // Active low reset (directly or button)

    // Buttons (directly active high on Basys3)
    input  logic btnc,          // Center - Start/Reset
    input  logic btnu,          // Up - Speed up
    input  logic btnd,          // Down - Speed down
    input  logic btnl,          // Left - Randomize
    input  logic btnr,          // Right - Reserved

    // Switches
    input  logic [15:0] sw,

    // VGA
    output logic [3:0] vga_r,
    output logic [3:0] vga_g,
    output logic [3:0] vga_b,
    output logic vga_hs,
    output logic vga_vs,

    // LEDs for status
    output logic [15:0] led
);

    // =========================================================================
    // Parameters
    // =========================================================================
    localparam FP_TOTAL = FP_INT_BITS + FP_FRAC_BITS + 1;
    localparam FP_SCALE = 1 << FP_FRAC_BITS;

    // Fixed-point constants (can be adjusted via speed control)
    localparam signed [FP_TOTAL-1:0] DEFAULT_MOVE_SPEED = FP_TOTAL'($rtoi(1.0 * FP_SCALE));
    localparam signed [FP_TOTAL-1:0] DEFAULT_TURN_SPEED = FP_TOTAL'($rtoi(0.3 * FP_SCALE));
    localparam signed [FP_TOTAL-1:0] SENSOR_ANGLE = FP_TOTAL'($rtoi(0.5 * FP_SCALE));
    localparam signed [FP_TOTAL-1:0] SENSOR_DISTANCE = FP_TOTAL'($rtoi(9.0 * FP_SCALE));
    localparam signed [FP_TOTAL-1:0] DEPOSIT_AMOUNT = FP_TOTAL'($rtoi(5.0 * FP_SCALE));
    localparam signed [FP_TOTAL-1:0] DECAY_RATE = FP_TOTAL'($rtoi(0.95 * FP_SCALE));

    // =========================================================================
    // Clock Generation
    // =========================================================================
    logic clk_25mhz;
    logic clk_locked;

    // Simple clock divider for 25MHz pixel clock (100/4 = 25)
    logic [1:0] clk_div;

    always_ff @(posedge clk_100mhz or negedge rst_n) begin
        if (!rst_n) begin
            clk_div <= '0;
        end
        else begin
            clk_div <= clk_div + 1'b1;
        end
    end

    assign clk_25mhz = clk_div[1];
    assign clk_locked = 1'b1;  // Always locked for simple divider

    // =========================================================================
    // Button Debouncing
    // =========================================================================
    logic [4:0] btn_raw, btn_debounced, btn_posedge_pulse;

    assign btn_raw = {btnr, btnl, btnd, btnu, btnc};

    debouncer_array #(
        .NUM_BUTTONS(5),
        .CLK_FREQ(100_000_000),
        .DEBOUNCE_MS(20)
    ) u_debouncer (
        .clk(clk_100mhz),
        .rst_n(rst_n),
        .btn_in(btn_raw),
        .btn_out(btn_debounced),
        .btn_posedge(btn_posedge_pulse),
        .btn_negedge()
    );

    wire btn_start    = btn_posedge_pulse[0];
    wire btn_speed_up = btn_posedge_pulse[1];
    wire btn_speed_dn = btn_posedge_pulse[2];
    wire btn_random   = btn_posedge_pulse[3];
    wire sim_pause    = sw[0];

    // =========================================================================
    // Speed Control
    // =========================================================================
    logic [3:0] speed_level;  // 0-15, default 8
    logic signed [FP_TOTAL-1:0] current_move_speed;

    always_ff @(posedge clk_100mhz or negedge rst_n) begin
        if (!rst_n) begin
            speed_level <= 4'd8;
        end
        else begin
            if (btn_speed_up && speed_level < 4'd15) begin
                speed_level <= speed_level + 1'b1;
            end
            else if (btn_speed_dn && speed_level > 4'd0) begin
                speed_level <= speed_level - 1'b1;
            end
        end
    end

    // Scale move speed based on level (0.25x to 2x)
    assign current_move_speed = (DEFAULT_MOVE_SPEED * (speed_level + 4)) >> 4;

    // =========================================================================
    // LFSR Random Number Generator
    // =========================================================================
    logic [LFSR_WIDTH-1:0] lfsr_state;
    logic lfsr_enable, lfsr_load;
    logic [LFSR_WIDTH-1:0] lfsr_seed;

    lfsr #(
        .WIDTH(LFSR_WIDTH),
        .SEED(32'hDEADBEEF)
    ) u_lfsr (
        .clk(clk_100mhz),
        .rst_n(rst_n),
        .enable(lfsr_enable),
        .load(lfsr_load),
        .seed_val(lfsr_seed),
        .lfsr_out(lfsr_state),
        .valid()
    );

    // New random seed from button
    always_ff @(posedge clk_100mhz or negedge rst_n) begin
        if (!rst_n) begin
            lfsr_load <= 1'b0;
            lfsr_seed <= 32'hDEADBEEF;
        end
        else begin
            lfsr_load <= btn_random;
            if (btn_random) begin
                // Use current LFSR state XORed with counter as new seed
                lfsr_seed <= lfsr_state ^ {16'h0, clk_div, 14'b0};
            end
        end
    end

    // =========================================================================
    // Trail Map Memory (Dual-port BRAM)
    // =========================================================================
    // Port A: VGA read
    // Port B: Agent read/write

    logic [18:0] trail_addr_a, trail_addr_b;  // 640*480 = 307200, needs 19 bits
    logic [7:0]  trail_data_a, trail_data_b_out;
    logic [7:0]  trail_data_b_in;
    logic        trail_we_b;

    // Simple dual-port RAM
    logic [7:0] trail_mem [0:WIDTH*HEIGHT-1];

    // Port A (VGA read)
    always_ff @(posedge clk_25mhz) begin
        trail_data_a <= trail_mem[trail_addr_a];
    end

    // Port B (Agent read/write)
    always_ff @(posedge clk_100mhz) begin
        if (trail_we_b) begin
            trail_mem[trail_addr_b] <= trail_data_b_in;
        end
        trail_data_b_out <= trail_mem[trail_addr_b];
    end

    // =========================================================================
    // VGA Controller
    // =========================================================================
    logic [9:0] pixel_x;
    logic [8:0] pixel_y;
    logic pixel_valid;
    logic frame_start;

    vga_controller u_vga (
        .clk(clk_25mhz),
        .rst_n(rst_n),
        .hsync(vga_hs),
        .vsync(vga_vs),
        .vga_r(vga_r),
        .vga_g(vga_g),
        .vga_b(vga_b),
        .pixel_x(pixel_x),
        .pixel_y(pixel_y),
        .pixel_valid(pixel_valid),
        .frame_start(frame_start),
        .pixel_data(trail_data_a)
    );

    // VGA trail map address
    assign trail_addr_a = pixel_y * WIDTH + pixel_x;

    // =========================================================================
    // Simulation State Machine
    // =========================================================================
    typedef enum logic [3:0] {
        SIM_IDLE,
        SIM_INIT,
        SIM_RUN_AGENTS,
        SIM_DIFFUSE,
        SIM_WAIT_FRAME
    } sim_state_t;

    sim_state_t sim_state;
    logic [$clog2(NUM_AGENTS)-1:0] agent_idx;
    logic sim_running;

    always_ff @(posedge clk_100mhz or negedge rst_n) begin
        if (!rst_n) begin
            sim_state <= SIM_IDLE;
            agent_idx <= '0;
            sim_running <= 1'b0;
        end
        else begin
            case (sim_state)
                SIM_IDLE: begin
                    if (btn_start) begin
                        sim_state <= SIM_INIT;
                        sim_running <= 1'b1;
                    end
                end

                SIM_INIT: begin
                    // Initialize agents (simplified - would need agent memory)
                    agent_idx <= '0;
                    sim_state <= SIM_RUN_AGENTS;
                end

                SIM_RUN_AGENTS: begin
                    if (!sim_pause) begin
                        if (agent_idx == NUM_AGENTS - 1) begin
                            agent_idx <= '0;
                            sim_state <= SIM_DIFFUSE;
                        end
                        else begin
                            agent_idx <= agent_idx + 1'b1;
                        end
                    end
                end

                SIM_DIFFUSE: begin
                    // Apply diffusion and decay to trail map
                    // (Simplified - would need diffusion kernel)
                    sim_state <= SIM_WAIT_FRAME;
                end

                SIM_WAIT_FRAME: begin
                    // Sync to VGA frame
                    if (frame_start) begin
                        sim_state <= SIM_RUN_AGENTS;
                    end
                end

                default: sim_state <= SIM_IDLE;
            endcase

            // Stop button
            if (btn_start && sim_running) begin
                sim_state <= SIM_IDLE;
                sim_running <= 1'b0;
            end
        end
    end

    // =========================================================================
    // LED Status Display
    // =========================================================================
    assign led[3:0]   = speed_level;
    assign led[4]     = sim_running;
    assign led[5]     = sim_pause;
    assign led[7:6]   = sim_state[1:0];
    assign led[15:8]  = lfsr_state[7:0];

    // LFSR enable during agent processing
    assign lfsr_enable = (sim_state == SIM_RUN_AGENTS) && !sim_pause;

endmodule
