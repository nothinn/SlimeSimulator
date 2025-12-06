`timescale 1ns/1ps

module slime_xsim_tb();
    // ===================================================================
    // Clock and Reset
    // ===================================================================
    logic clk_100mhz = 0;
    logic rst_n = 0;

    always #5 clk_100mhz = ~clk_100mhz;  // 100MHz clock

    // ===================================================================
    // DUT Instantiation
    // ===================================================================
    localparam WIDTH = 320;
    localparam HEIGHT = 240;
    localparam NUM_AGENTS = 100;

    logic [3:0] vga_r, vga_g, vga_b;
    logic vga_hs, vga_vs;
    logic [15:0] led;
    logic sim_start;
    logic [18:0] debug_trail_addr;
    logic [17:0] debug_trail_data;
    logic [9:0] debug_agent_idx;
    logic [1:0] debug_agent_sel;
    logic [24:0] debug_agent_data;
    logic debug_agent_write_en;
    logic [24:0] debug_agent_data_write;

    slime_top #(
        .NUM_AGENTS(NUM_AGENTS),
        .WIDTH(WIDTH),
        .HEIGHT(HEIGHT)
    ) dut (
        .clk_100mhz(clk_100mhz),
        .btnc(1'b0),
        .btnu(1'b0),
        .btnd(1'b0),
        .btnl(1'b0),
        .btnr(1'b0),
        .sw(16'b0),
        .vga_r(vga_r),
        .vga_g(vga_g),
        .vga_b(vga_b),
        .vga_hs(vga_hs),
        .vga_vs(vga_vs),
        .led(led),
        .sim_start(sim_start),
        .debug_trail_addr(debug_trail_addr),
        .debug_trail_data(debug_trail_data),
        .debug_agent_idx(debug_agent_idx),
        .debug_agent_sel(debug_agent_sel),
        .debug_agent_data(debug_agent_data),
        .debug_agent_write_en(debug_agent_write_en),
        .debug_agent_data_write(debug_agent_data_write)
    );

    // ===================================================================
    // Signal Probing - Direct Access to Internal Coordinator Signals
    // ===================================================================
    wire [2:0] coord_state = dut.u_coordinator.state;
    wire [9:0] coord_agent_idx = dut.u_coordinator.current_agent_idx;
    wire coord_step_complete_pulse = dut.u_coordinator.step_complete_pulse;
    wire proc_done = dut.u_coordinator.proc_done;
    wire proc_busy = dut.u_coordinator.proc_busy;
    wire [24:0] proc_x_out = dut.u_coordinator.proc_x_out;
    wire [24:0] proc_y_out = dut.u_coordinator.proc_y_out;
    wire [24:0] proc_angle_out = dut.u_coordinator.proc_angle_out;
    wire [24:0] agent_x_0 = dut.u_coordinator.agent_x[0];
    wire [24:0] agent_y_0 = dut.u_coordinator.agent_y[0];
    wire [24:0] agent_angle_0 = dut.u_coordinator.agent_angle[0];

    // ===================================================================
    // Test Stimulus
    // ===================================================================
    localparam FP_SCALE = 4096;

    initial begin
        // Initialize
        rst_n = 1'b0;
        sim_start = 1'b0;
        debug_agent_write_en = 1'b0;
        #100;
        rst_n = 1'b1;
        #100;

        // Initialize agent 0 at (160, 120), angle 0 radians
        $display("========================================");
        $display("Initializing Agent 0");
        $display("========================================");

        // Write X coordinate (160.0 * 4096 = 655360)
        debug_agent_idx = 10'd0;
        debug_agent_sel = 2'b00;
        debug_agent_data_write = 25'(160 * FP_SCALE);
        debug_agent_write_en = 1'b1;
        @(posedge clk_100mhz);

        // Write Y coordinate (120.0 * 4096 = 491520)
        debug_agent_sel = 2'b01;
        debug_agent_data_write = 25'(120 * FP_SCALE);
        @(posedge clk_100mhz);

        // Write angle (0 radians = 0)
        debug_agent_sel = 2'b10;
        debug_agent_data_write = 25'(0);
        @(posedge clk_100mhz);

        debug_agent_write_en = 1'b0;
        #100;

        // Start simulation
        $display("========================================");
        $display("Starting Simulation");
        $display("========================================");
        sim_start = 1'b1;
        @(posedge clk_100mhz);
        sim_start = 1'b0;

        // Monitor for step completions
        $display("Monitoring RTL execution...\n");

        #100000;  // Run for 100k cycles

        $display("\n========================================");
        $display("Test Complete");
        $display("========================================");
        $finish;
    end

    // ===================================================================
    // Monitoring and Logging - Comprehensive Step & Double-Processing Detection
    // ===================================================================

    // Track state machine transitions
    integer prev_state = -1;
    always @(posedge clk_100mhz) begin
        if (coord_state != prev_state && coord_state !== 3'bx && coord_state !== 3'bz) begin
            case (coord_state)
                3'b000: $display("[%0t] COORD STATE: IDLE", $time);
                3'b001: $display("[%0t] COORD STATE: INITIALIZE", $time);
                3'b010: $display("[%0t] COORD STATE: RUNNING", $time);
                3'b011: $display("[%0t] COORD STATE: DONE", $time);
                default: $display("[%0t] COORD STATE: UNKNOWN (%0d)", $time, coord_state);
            endcase
            prev_state = coord_state;
        end
    end

    // ===================================================================
    // DOUBLE-PROCESSING DETECTION: Track each agent per step
    // ===================================================================
    integer agents_processed_this_step [0:NUM_AGENTS-1];
    integer current_step_num = 0;
    integer prev_step_num = -1;
    integer double_process_count = 0;

    always @(posedge clk_100mhz) begin
        if (proc_done) begin
            // Detect step completion by wraparound
            if (current_step_num != prev_step_num) begin
                // New step detected - reset processing tracker
                for (int i = 0; i < NUM_AGENTS; i++) begin
                    agents_processed_this_step[i] = 0;
                end
                prev_step_num = current_step_num;
                $display("[%0t] === STEP BOUNDARY DETECTED: Step %0d → %0d ===",
                         $time, prev_step_num, current_step_num);
            end

            // Check if this agent was already processed this step
            if (agents_processed_this_step[coord_agent_idx] > 0) begin
                double_process_count++;
                $display("[%0t] !!! DOUBLE-PROCESSING DETECTED !!!", $time);
                $display("[%0t]     Agent[%0d] processed %0d times in step %0d",
                         $time, coord_agent_idx, agents_processed_this_step[coord_agent_idx] + 1,
                         current_step_num);
                $display("[%0t]     This is the smoking gun for the 2x movement bug!",
                         $time);
            end

            agents_processed_this_step[coord_agent_idx]++;
        end
    end

    // ===================================================================
    // STEP COMPLETION TRACKING with Movement Inspection
    // ===================================================================
    integer prev_step_complete = 0;
    integer step_count = 0;
    real x_step, y_step, angle_step;
    real x_prev_step = 160.0, y_prev_step = 120.0;
    real x_delta, y_delta;

    always @(posedge clk_100mhz) begin
        if (coord_step_complete_pulse && !prev_step_complete) begin
            step_count++;
            current_step_num = step_count;
            x_step = real'(agent_x_0) / FP_SCALE;
            y_step = real'(agent_y_0) / FP_SCALE;
            angle_step = real'(agent_angle_0) / FP_SCALE;

            // Calculate deltas for movement analysis
            x_delta = x_step - x_prev_step;
            y_delta = y_step - y_prev_step;

            $display("");
            $display("[%0t] ╔════════════════════════════════════════════════════════════╗",
                     $time);
            $display("[%0t] ║ STEP COMPLETE #%0d                                           ║",
                     $time, step_count);
            $display("[%0t] ╠════════════════════════════════════════════════════════════╣",
                     $time);
            $display("[%0t] ║ Agent[0] Position:  x=%.2f y=%.2f angle=%.4f                ║",
                     $time, x_step, y_step, angle_step);
            $display("[%0t] ║ Delta from prev:    dx=%+.2f dy=%+.2f                        ║",
                     $time, x_delta, y_delta);
            $display("[%0t] ║ Agents in step:     %0d processed                            ║",
                     $time, agents_processed_this_step[0]);
            if (double_process_count > 0) begin
                $display("[%0t] ║ ⚠️  TOTAL DOUBLE-PROCESSES: %0d                             ║",
                         $time, double_process_count);
            end
            $display("[%0t] ╚════════════════════════════════════════════════════════════╝",
                     $time);
            $display("");

            // Update previous for next delta calculation
            x_prev_step = x_step;
            y_prev_step = y_step;
        end
        prev_step_complete = coord_step_complete_pulse;
    end

    // ===================================================================
    // AGENT PROCESSING MONITOR - Per-agent tracking
    // ===================================================================
    integer prev_agent_idx = -1;
    integer total_agents_processed = 0;
    real x_proc, y_proc, angle_proc;

    always @(posedge clk_100mhz) begin
        if (proc_done) begin
            if (coord_agent_idx != prev_agent_idx) begin
                total_agents_processed++;
                if (coord_agent_idx == 0) begin
                    x_proc = real'(proc_x_out) / FP_SCALE;
                    y_proc = real'(proc_y_out) / FP_SCALE;
                    angle_proc = real'(proc_angle_out) / FP_SCALE;
                    $display("[%0t] [PROC] Agent[0] output: x=%.2f y=%.2f angle=%.4f (Total agents processed: %0d)",
                             $time, x_proc, y_proc, angle_proc, total_agents_processed);
                end
            end
            prev_agent_idx = coord_agent_idx;
        end
    end

    // ===================================================================
    // FINAL STATISTICS REPORT
    // ===================================================================
    final begin
        $display("");
        $display("╔════════════════════════════════════════════════════════════╗");
        $display("║              SIMULATION COMPLETE - FINAL REPORT             ║");
        $display("╠════════════════════════════════════════════════════════════╣");
        $display("║ Total steps completed: %0d                                  ║", step_count);
        $display("║ Total agents processed: %0d                                 ║", total_agents_processed);
        $display("║ Double-processing incidents: %0d                            ║", double_process_count);
        if (double_process_count > 0) begin
            $display("║ ⚠️  CONCLUSION: 2x bug IS caused by double-processing!      ║");
        end else begin
            $display("║ ✓ CONCLUSION: No double-processing detected                ║");
        end
        $display("╚════════════════════════════════════════════════════════════╝");
        $display("");
    end

endmodule
