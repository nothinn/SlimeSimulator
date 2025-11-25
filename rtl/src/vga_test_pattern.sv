// VGA Test Pattern Generator
// Generates various test patterns for VGA verification
//
// Patterns:
//   0: Color bars (8 vertical bars)
//   1: Gradient (horizontal)
//   2: Checkerboard
//   3: Border test (white border, black center)
//   4: Grid pattern
//   5: Red/Green/Blue screens
//   6: Crosshatch
//   7: Pass-through (normal operation)

module vga_test_pattern #(
    parameter WIDTH  = 640,
    parameter HEIGHT = 480
) (
    input  logic clk,
    input  logic rst_n,

    // Pattern selection (directly from switches)
    input  logic [2:0] pattern_sel,
    input  logic pattern_enable,     // SW to enable test pattern

    // Pixel coordinates from VGA controller
    input  logic [9:0] pixel_x,
    input  logic [8:0] pixel_y,
    input  logic pixel_valid,

    // Normal pixel data input
    input  logic [7:0] normal_pixel,

    // RGB output
    output logic [3:0] vga_r,
    output logic [3:0] vga_g,
    output logic [3:0] vga_b
);

    logic [3:0] pattern_r, pattern_g, pattern_b;
    logic [3:0] normal_r, normal_g, normal_b;

    // Normal slime display (green-ish)
    assign normal_g = normal_pixel[7:4];
    assign normal_r = normal_pixel[7:6];  // Slight red tint
    assign normal_b = 4'h0;

    // Pattern generation
    always_comb begin
        pattern_r = 4'h0;
        pattern_g = 4'h0;
        pattern_b = 4'h0;

        if (pixel_valid) begin
            case (pattern_sel)
                // =====================================================
                // Pattern 0: Color Bars (8 vertical bars)
                // =====================================================
                3'd0: begin
                    case (pixel_x[9:7])  // Divide screen into 8 sections
                        3'd0: begin pattern_r = 4'hF; pattern_g = 4'hF; pattern_b = 4'hF; end // White
                        3'd1: begin pattern_r = 4'hF; pattern_g = 4'hF; pattern_b = 4'h0; end // Yellow
                        3'd2: begin pattern_r = 4'h0; pattern_g = 4'hF; pattern_b = 4'hF; end // Cyan
                        3'd3: begin pattern_r = 4'h0; pattern_g = 4'hF; pattern_b = 4'h0; end // Green
                        3'd4: begin pattern_r = 4'hF; pattern_g = 4'h0; pattern_b = 4'hF; end // Magenta
                        3'd5: begin pattern_r = 4'hF; pattern_g = 4'h0; pattern_b = 4'h0; end // Red
                        3'd6: begin pattern_r = 4'h0; pattern_g = 4'h0; pattern_b = 4'hF; end // Blue
                        3'd7: begin pattern_r = 4'h0; pattern_g = 4'h0; pattern_b = 4'h0; end // Black
                    endcase
                end

                // =====================================================
                // Pattern 1: Horizontal Gradient
                // =====================================================
                3'd1: begin
                    // Gradient from black to white across screen
                    pattern_r = pixel_x[9:6];
                    pattern_g = pixel_x[9:6];
                    pattern_b = pixel_x[9:6];
                end

                // =====================================================
                // Pattern 2: Checkerboard (32x32 squares)
                // =====================================================
                3'd2: begin
                    if (pixel_x[5] ^ pixel_y[5]) begin
                        pattern_r = 4'hF;
                        pattern_g = 4'hF;
                        pattern_b = 4'hF;
                    end
                end

                // =====================================================
                // Pattern 3: Border Test (white border, center info)
                // =====================================================
                3'd3: begin
                    // White border (8 pixels wide)
                    if (pixel_x < 8 || pixel_x >= WIDTH-8 ||
                        pixel_y < 8 || pixel_y >= HEIGHT-8) begin
                        pattern_r = 4'hF;
                        pattern_g = 4'hF;
                        pattern_b = 4'hF;
                    end
                    // Center crosshair
                    else if (pixel_x == WIDTH/2 || pixel_y == HEIGHT/2) begin
                        pattern_r = 4'hF;
                        pattern_g = 4'h0;
                        pattern_b = 4'h0;
                    end
                    // Corner markers (red squares)
                    else if ((pixel_x < 40 && pixel_y < 40) ||
                             (pixel_x >= WIDTH-40 && pixel_y < 40) ||
                             (pixel_x < 40 && pixel_y >= HEIGHT-40) ||
                             (pixel_x >= WIDTH-40 && pixel_y >= HEIGHT-40)) begin
                        pattern_r = 4'hF;
                        pattern_g = 4'h0;
                        pattern_b = 4'h0;
                    end
                end

                // =====================================================
                // Pattern 4: Grid Pattern (64 pixel spacing)
                // =====================================================
                3'd4: begin
                    if ((pixel_x[5:0] == 6'd0) || (pixel_y[5:0] == 6'd0)) begin
                        pattern_r = 4'h8;
                        pattern_g = 4'h8;
                        pattern_b = 4'h8;
                    end
                    // Brighter lines every 64 pixels
                    if ((pixel_x[6:0] == 7'd0) || (pixel_y[6:0] == 7'd0)) begin
                        pattern_r = 4'hF;
                        pattern_g = 4'hF;
                        pattern_b = 4'hF;
                    end
                end

                // =====================================================
                // Pattern 5: RGB Screens (cycle with y position)
                // =====================================================
                3'd5: begin
                    if (pixel_y < HEIGHT/3) begin
                        pattern_r = 4'hF;  // Red
                    end
                    else if (pixel_y < 2*HEIGHT/3) begin
                        pattern_g = 4'hF;  // Green
                    end
                    else begin
                        pattern_b = 4'hF;  // Blue
                    end
                end

                // =====================================================
                // Pattern 6: Crosshatch with varying density
                // =====================================================
                3'd6: begin
                    // Diagonal lines
                    if (((pixel_x + pixel_y) & 8'h0F) == 0 ||
                        ((pixel_x - pixel_y) & 8'h0F) == 0) begin
                        pattern_r = 4'hF;
                        pattern_g = 4'hF;
                        pattern_b = 4'hF;
                    end
                end

                // =====================================================
                // Pattern 7: Resolution test (alternating pixels)
                // =====================================================
                3'd7: begin
                    // Finest pattern - alternating pixels
                    if (pixel_x[0] ^ pixel_y[0]) begin
                        pattern_r = 4'hF;
                        pattern_g = 4'hF;
                        pattern_b = 4'hF;
                    end
                end

                default: begin
                    pattern_r = 4'h0;
                    pattern_g = 4'h0;
                    pattern_b = 4'h0;
                end
            endcase
        end
    end

    // Output mux - test pattern or normal display
    always_comb begin
        if (pattern_enable && pixel_valid) begin
            vga_r = pattern_r;
            vga_g = pattern_g;
            vga_b = pattern_b;
        end
        else if (pixel_valid) begin
            vga_r = normal_r;
            vga_g = normal_g;
            vga_b = normal_b;
        end
        else begin
            vga_r = 4'h0;
            vga_g = 4'h0;
            vga_b = 4'h0;
        end
    end

endmodule


// Simple test pattern top module for standalone VGA testing
module vga_test_top (
    input  logic clk_100mhz,
    input  logic btnr,           // Reset

    input  logic [15:0] sw,      // SW[2:0] = pattern, SW[15] = enable test

    output logic [3:0] vga_r,
    output logic [3:0] vga_g,
    output logic [3:0] vga_b,
    output logic vga_hs,
    output logic vga_vs,

    output logic [15:0] led
);

    // Clock divider for 25MHz
    logic [1:0] clk_div = 2'b00;
    logic clk_25mhz;

    always_ff @(posedge clk_100mhz) begin
        clk_div <= clk_div + 1'b1;
    end
    assign clk_25mhz = clk_div[1];

    // Reset
    logic rst_n;
    logic [3:0] por_counter = 4'hF;

    always_ff @(posedge clk_100mhz) begin
        if (btnr)
            por_counter <= 4'hF;
        else if (por_counter != 0)
            por_counter <= por_counter - 1'b1;
    end
    assign rst_n = (por_counter == 0);

    // VGA signals
    logic [9:0] pixel_x;
    logic [8:0] pixel_y;
    logic pixel_valid;
    logic frame_start;
    logic [3:0] vga_r_int, vga_g_int, vga_b_int;

    // VGA Controller (directly output sync signals)
    vga_controller u_vga (
        .clk(clk_25mhz),
        .rst_n(rst_n),
        .hsync(vga_hs),
        .vsync(vga_vs),
        .vga_r(),  // Not used - test pattern generates color
        .vga_g(),
        .vga_b(),
        .pixel_x(pixel_x),
        .pixel_y(pixel_y),
        .pixel_valid(pixel_valid),
        .frame_start(frame_start),
        .pixel_data(8'h00)
    );

    // Test Pattern Generator
    vga_test_pattern #(
        .WIDTH(640),
        .HEIGHT(480)
    ) u_test_pattern (
        .clk(clk_25mhz),
        .rst_n(rst_n),
        .pattern_sel(sw[2:0]),
        .pattern_enable(1'b1),  // Always show test pattern
        .pixel_x(pixel_x),
        .pixel_y(pixel_y),
        .pixel_valid(pixel_valid),
        .normal_pixel(8'h00),
        .vga_r(vga_r),
        .vga_g(vga_g),
        .vga_b(vga_b)
    );

    // LED display
    assign led[2:0] = sw[2:0];      // Current pattern
    assign led[7:3] = 5'b0;
    assign led[8] = pixel_valid;
    assign led[9] = frame_start;
    assign led[15:10] = 6'b0;

endmodule
