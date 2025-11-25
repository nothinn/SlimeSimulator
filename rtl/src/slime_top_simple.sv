// Simplified Slime Simulator - Trail Animation Demo
// Demonstrates trail memory and VGA display without complex agent processor
// Shows scrolling/animated patterns to verify memory system works

module slime_top_simple #(
    parameter FP_INT_BITS  = 12,
    parameter FP_FRAC_BITS = 12,
    parameter LFSR_WIDTH   = 32,
    parameter SIM_WIDTH    = 160,
    parameter SIM_HEIGHT   = 120,
    parameter VGA_WIDTH    = 640,
    parameter VGA_HEIGHT   = 480
) (
    input  logic clk_100mhz,

    // Buttons
    input  logic btnc,          // Start/stop animation
    input  logic btnu,          // Speed up
    input  logic btnd,          // Speed down
    input  logic btnl,          // Randomize
    input  logic btnr,          // Reset

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
    // Clock Generation
    // =========================================================================
    logic clk_25mhz;
    logic [1:0] clk_div = 2'b00;

    always_ff @(posedge clk_100mhz) begin
        clk_div <= clk_div + 1'b1;
    end
    assign clk_25mhz = clk_div[1];

    // =========================================================================
    // Reset Generation
    // =========================================================================
    logic rst_n;
    logic [3:0] por_counter = 4'hF;

    always_ff @(posedge clk_100mhz) begin
        if (btnr)
            por_counter <= 4'hF;
        else if (por_counter != 0)
            por_counter <= por_counter - 1'b1;
    end
    assign rst_n = (por_counter == 0);

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
    wire btn_randomize = btn_posedge_pulse[3];

    // =========================================================================
    // Trail Map Memory (BRAM)
    // =========================================================================
    localparam TRAIL_ADDR_BITS = $clog2(SIM_WIDTH * SIM_HEIGHT);

    logic [TRAIL_ADDR_BITS-1:0] trail_addr_a, trail_addr_write;
    logic [7:0] trail_data_a, trail_data_write;
    logic trail_write_en;

    // Trail memory
    logic [7:0] trail_mem [0:SIM_WIDTH*SIM_HEIGHT-1];

    // Port A: VGA read
    always_ff @(posedge clk_25mhz) begin
        trail_data_a <= trail_mem[trail_addr_a];
    end

    // Trail write (memory update)
    always_ff @(posedge clk_100mhz) begin
        if (trail_write_en) begin
            trail_mem[trail_addr_write] <= trail_data_write;
        end
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

    // VGA trail map address with coordinate clamping
    // Map VGA pixels (640x480) to simulation memory (160x120) with 4x upscaling
    logic [9:0] sim_x;
    logic [8:0] sim_y;

    assign sim_x = (pixel_x >> 2) < SIM_WIDTH ? (pixel_x >> 2) : (SIM_WIDTH - 1);
    assign sim_y = (pixel_y >> 2) < SIM_HEIGHT ? (pixel_y >> 2) : (SIM_HEIGHT - 1);
    assign trail_addr_a = sim_y * SIM_WIDTH + sim_x;

    // =========================================================================
    // Animation State Machine
    // =========================================================================
    logic running;
    logic [3:0] speed_level;
    logic [15:0] update_counter;
    logic [15:0] update_period;
    logic [18:0] frame_counter;
    logic [15:0] trail_update_idx;

    // Speed control (0-15, default 8)
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

    // Update period: slower speed = longer period
    // Period ranges from 256 (fast) to 4096 (slow) 100MHz cycles
    assign update_period = (256 << (15 - speed_level[3:0]));

    // Animation update logic
    always_ff @(posedge clk_100mhz or negedge rst_n) begin
        if (!rst_n) begin
            running <= 1'b1;
            update_counter <= 16'h0;
            trail_update_idx <= 19'h0;
            trail_write_en <= 1'b0;
            trail_data_write <= 8'h0;
            trail_addr_write <= {TRAIL_ADDR_BITS{1'b0}};
            // Trail memory clears incrementally via button or updates
            frame_counter <= 19'h0;
        end
        else begin
            // Track frame count
            if (frame_start) begin
                frame_counter <= frame_counter + 1'b1;
            end

            // Handle button inputs
            if (btn_start) begin
                running <= ~running;
            end

            // Counter always increments when running
            update_counter <= update_counter + 1'b1;

            // Default: no write unless overridden
            trail_write_en <= 1'b0;

            if (btn_randomize) begin
                // Randomize: set one random location to bright
                trail_addr_write <= (frame_counter[17:0] * 73) % (SIM_WIDTH * SIM_HEIGHT);
                trail_data_write <= 8'hFF;
                trail_write_en <= 1'b1;
            end
            else if (running && update_counter >= update_period) begin
                // Trail animation: update trails based on pattern
                update_counter <= 16'h0;

                // Write pattern value to current location based on SW
                trail_addr_write <= trail_update_idx;
                trail_write_en <= 1'b1;

                // Pattern is determined by SW[2:0] - switch position directly controls output
                case (sw[2:0])
                    3'b000: trail_data_write <= 8'hFF;  // Bright green
                    3'b001: trail_data_write <= 8'hCC;  // Medium-bright
                    3'b010: trail_data_write <= 8'h88;  // Medium
                    3'b011: trail_data_write <= 8'h44;  // Medium-dim
                    3'b100: trail_data_write <= 8'h22;  // Dim
                    3'b101: trail_data_write <= 8'h11;  // Very dim
                    3'b110: trail_data_write <= 8'h00;  // Black
                    3'b111: trail_data_write <= 8'hAA;  // Alternate
                endcase

                // Move to next trail location
                trail_update_idx <= trail_update_idx + 1'b1;
                if (trail_update_idx >= (SIM_WIDTH * SIM_HEIGHT - 1)) begin
                    trail_update_idx <= 19'h0;
                end
            end
        end
    end

    // =========================================================================
    // LED Status Display
    // =========================================================================
    assign led[3:0]   = speed_level;           // Current speed level
    assign led[4]     = running;               // Animation running
    assign led[5]     = btn_debounced[0];      // BTNC status
    assign led[7:6]   = sw[1:0];               // Pattern selection
    assign led[11:8]  = frame_counter[11:8];   // Frame counter (high bits)
    assign led[15:12] = trail_update_idx[15:12]; // Update progress

endmodule
