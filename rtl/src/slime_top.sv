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
    parameter WIDTH        = 160,
    parameter HEIGHT       = 120
) (
    input  logic clk_100mhz,    // 100 MHz system clock

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
    output logic [15:0] led,

    // Simulation control (for testbench)
    input  logic sim_start  // Direct start signal for simulation/testbench
);

    // =========================================================================
    // Reset Generation
    // =========================================================================
    // Generate internal reset signal - always 1 (never resetting) after power-on
    logic rst_n;
    assign rst_n = 1'b1;

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
    logic [4:0] btn_raw;
    (* mark_debug = "true" *) logic [4:0] btn_debounced;
    logic [4:0] btn_posedge_pulse;

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
    (* mark_debug = "true" *) wire sim_pause = sw[0];

    // =========================================================================
    // Speed Control
    // =========================================================================
    (* mark_debug = "true" *) logic [3:0] speed_level;  // 0-15, default 8
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
    (* mark_debug = "true" *) logic [LFSR_WIDTH-1:0] lfsr_state;
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

    logic [18:0] trail_addr_a;
    (* mark_debug = "true" *) logic [18:0] trail_addr_b;  // Debug: agent write address
    logic [17:0] trail_data_a;
    (* mark_debug = "true" *) logic [17:0] trail_data_b_out;  // Debug: agent read data
    (* mark_debug = "true" *) logic [17:0] trail_data_b_in;   // Debug: agent write data
    (* mark_debug = "true" *) logic        trail_we_b;         // Debug: agent write enable

    // Simple dual-port RAM - 18-bit trail values
    logic [17:0] trail_mem [0:WIDTH*HEIGHT-1];

    // Port A (VGA read)
    always_ff @(posedge clk_25mhz) begin
        trail_data_a <= trail_mem[trail_addr_a];
    end

    // Port B (Agent read/write with accumulation)
    always_ff @(posedge clk_100mhz) begin
        if (trail_we_b) begin
            // Accumulate trail (saturating add)
            if (trail_mem[trail_addr_b] + trail_data_b_in > 18'h3FFFF) begin
                trail_mem[trail_addr_b] <= 18'h3FFFF;  // Saturate at 18-bit max
            end else begin
                trail_mem[trail_addr_b] <= trail_mem[trail_addr_b] + trail_data_b_in;
            end
        end
        trail_data_b_out <= trail_mem[trail_addr_b];
    end

    // =========================================================================
    // VGA Controller
    // =========================================================================
    (* mark_debug = "true" *) logic [9:0] pixel_x;
    (* mark_debug = "true" *) logic [8:0] pixel_y;
    logic pixel_valid;
    (* mark_debug = "true" *) logic frame_start;

    // Frame counter for debug monitoring
    (* mark_debug = "true" *) logic [31:0] frame_count;

    always_ff @(posedge clk_25mhz or negedge rst_n) begin
        if (!rst_n) begin
            frame_count <= '0;
        end
        else if (frame_start) begin
            frame_count <= frame_count + 1'b1;
        end
    end

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

    // VGA trail map address (downscale from 640x480 to 160x120)
    // VGA is 4x upscaled from simulation: 640/160 = 4, 480/120 = 4
    assign trail_addr_a = (pixel_y >> 2) * WIDTH + (pixel_x >> 2);

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

    (* mark_debug = "true" *) sim_state_t sim_state;
    (* mark_debug = "true" *) logic [$clog2(WIDTH*HEIGHT)-1:0] agent_idx;  // Iterate through all memory locations
    (* mark_debug = "true" *) logic sim_running;

    // Decay multiplier (0.95 in fixed-point Q12.12)
    localparam FP_DECAY = 25'h_0F33;  // 0.95 * 4096 ≈ 3891 = 0x0F33

    // Temporary registers for decay
    logic [17:0] trail_val_before_decay;
    logic [35:0] trail_val_after_mult;  // 18 + 25 bits for multiply result
    logic [17:0] trail_val_decayed;

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
                        // Write LFSR-generated trail values across entire memory
                        // (Note: Now using orchestrator, but keep this for fallback)
                        sim_trail_addr <= agent_idx;

                        // Create organic patterns using LFSR mixed with position for variation
                        sim_trail_data <= (lfsr_state[7:0] ^ {agent_idx[7:0]});

                        // Iterate through all memory locations (WIDTH * HEIGHT = 19200)
                        if (agent_idx == (WIDTH * HEIGHT - 1)) begin
                            agent_idx <= '0;
                            sim_state <= SIM_DIFFUSE;
                        end
                        else begin
                            agent_idx <= agent_idx + 1'b1;
                        end
                    end
                end

                SIM_DIFFUSE: begin
                    // Apply decay to trail map (one pixel per cycle)
                    if (!sim_pause) begin
                        // Read current trail value
                        trail_val_before_decay <= trail_mem[agent_idx];

                        // Multiply by decay factor (shift result for fixed-point)
                        // trail_mem[i] * FP_DECAY >> 12
                        trail_val_after_mult <= trail_mem[agent_idx] * FP_DECAY;
                        trail_val_decayed <= (trail_mem[agent_idx] * FP_DECAY) >> FP_FRAC_BITS;

                        // Write back decayed value
                        trail_mem[agent_idx] <= (trail_mem[agent_idx] * FP_DECAY) >> FP_FRAC_BITS;

                        // Advance to next pixel
                        if (agent_idx == (WIDTH * HEIGHT - 1)) begin
                            agent_idx <= '0;
                            sim_state <= SIM_WAIT_FRAME;
                        end else begin
                            agent_idx <= agent_idx + 1'b1;
                        end
                    end
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

    // Trail memory write enable for simple pattern generator
    assign sim_trail_we = (sim_state == SIM_RUN_AGENTS) && !sim_pause;

    // =========================================================================
    // Agent Processor Integration via Orchestrator
    // =========================================================================
    // The agent_orchestrator manages:
    // - Agent state memory (position x,y and angle for each agent)
    // - Agent initialization across the screen
    // - Trail deposition during agent processing
    //
    // This bridges to the full agent_processor pipeline for future expansion

    logic [18:0] orch_trail_addr;
    logic [17:0] orch_trail_data;
    logic        orch_trail_we;
    logic [17:0] orch_trail_read_data;

    logic [18:0] pattern_trail_addr;
    logic [7:0]  pattern_trail_data;
    logic        pattern_trail_we;

    // Outputs from simple pattern state machine (computed internally)
    logic [18:0] sim_trail_addr;
    logic [7:0]  sim_trail_data;
    logic        sim_trail_we;

    assign pattern_trail_addr = sim_trail_addr;
    assign pattern_trail_data = sim_trail_data;
    assign pattern_trail_we = sim_trail_we;

    // Mux between simple pattern and agent orchestrator
    // Use orchestrator when simulation is running
    logic use_orchestrator;
    assign use_orchestrator = (sim_state == SIM_RUN_AGENTS) && !sim_pause;

    // Final mux: select between pattern generator and orchestrator
    assign trail_addr_b = use_orchestrator ? orch_trail_addr : pattern_trail_addr;
    assign trail_data_b_in = use_orchestrator ? orch_trail_data : {{10{1'b0}}, pattern_trail_data};
    assign trail_we_b = use_orchestrator ? orch_trail_we : pattern_trail_we;

    // Agent Coordinator - Orchestrates real agent simulation
    // Use sim_start if provided (for testbench), otherwise use btn_start
    logic coordinator_start;
    assign coordinator_start = sim_start | btn_start;

    agent_coordinator #(
        .NUM_AGENTS(NUM_AGENTS),
        .FP_INT_BITS(FP_INT_BITS),
        .FP_FRAC_BITS(FP_FRAC_BITS),
        .FP_TOTAL(FP_TOTAL),
        .TRIG_BITS(TRIG_BITS),
        .WIDTH(WIDTH),
        .HEIGHT(HEIGHT)
    ) u_coordinator (
        .clk(clk_100mhz),
        .rst_n(rst_n),
        .start(coordinator_start),
        .pause(sim_pause),
        .lfsr_state(lfsr_state),
        .sensor_angle(SENSOR_ANGLE),
        .sensor_distance(SENSOR_DISTANCE),
        .turn_speed(DEFAULT_TURN_SPEED),
        .move_speed(current_move_speed),
        .deposit_amount(DEPOSIT_AMOUNT),
        .trail_data_b_out(orch_trail_read_data),
        .trail_addr_b(orch_trail_addr),
        .trail_data_b_in(orch_trail_data),
        .trail_we_b(orch_trail_we),
        .done()
    );

endmodule
