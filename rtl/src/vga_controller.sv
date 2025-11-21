// VGA Controller for Basys3
// 640x480 @ 60Hz
// Pixel clock: 25.175 MHz (we'll use 25 MHz from 100MHz/4)
//
// Timing parameters:
// Horizontal: 640 visible, 16 front porch, 96 sync, 48 back porch = 800 total
// Vertical: 480 visible, 10 front porch, 2 sync, 33 back porch = 525 total

module vga_controller #(
    parameter H_VISIBLE   = 640,
    parameter H_FRONT     = 16,
    parameter H_SYNC      = 96,
    parameter H_BACK      = 48,
    parameter V_VISIBLE   = 480,
    parameter V_FRONT     = 10,
    parameter V_SYNC      = 2,
    parameter V_BACK      = 33
) (
    input  logic clk,           // 25 MHz pixel clock
    input  logic rst_n,

    // VGA outputs
    output logic hsync,
    output logic vsync,
    output logic [3:0] vga_r,
    output logic [3:0] vga_g,
    output logic [3:0] vga_b,

    // Framebuffer interface
    output logic [9:0]  pixel_x,    // 0-639
    output logic [8:0]  pixel_y,    // 0-479
    output logic        pixel_valid,
    output logic        frame_start,
    input  logic [7:0]  pixel_data  // 8-bit grayscale from trail map
);

    // Derived parameters
    localparam H_TOTAL = H_VISIBLE + H_FRONT + H_SYNC + H_BACK;  // 800
    localparam V_TOTAL = V_VISIBLE + V_FRONT + V_SYNC + V_BACK;  // 525

    // Counters
    logic [9:0] h_count;
    logic [9:0] v_count;

    // Horizontal counter
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            h_count <= '0;
        end
        else if (h_count == H_TOTAL - 1) begin
            h_count <= '0;
        end
        else begin
            h_count <= h_count + 1'b1;
        end
    end

    // Vertical counter
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            v_count <= '0;
        end
        else if (h_count == H_TOTAL - 1) begin
            if (v_count == V_TOTAL - 1) begin
                v_count <= '0;
            end
            else begin
                v_count <= v_count + 1'b1;
            end
        end
    end

    // Sync signals (active low)
    // HSYNC active during h_count [H_VISIBLE + H_FRONT, H_VISIBLE + H_FRONT + H_SYNC)
    // VSYNC active during v_count [V_VISIBLE + V_FRONT, V_VISIBLE + V_FRONT + V_SYNC)
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            hsync <= 1'b1;
            vsync <= 1'b1;
        end
        else begin
            hsync <= ~((h_count >= H_VISIBLE + H_FRONT) &&
                       (h_count < H_VISIBLE + H_FRONT + H_SYNC));
            vsync <= ~((v_count >= V_VISIBLE + V_FRONT) &&
                       (v_count < V_VISIBLE + V_FRONT + V_SYNC));
        end
    end

    // Visible area detection
    wire h_visible = (h_count < H_VISIBLE);
    wire v_visible = (v_count < V_VISIBLE);
    wire visible = h_visible && v_visible;

    // Pixel coordinates (only valid during visible area)
    assign pixel_x = h_count[9:0];
    assign pixel_y = v_count[8:0];
    assign pixel_valid = visible;

    // Frame start pulse (beginning of frame)
    assign frame_start = (h_count == 0) && (v_count == 0);

    // Color output with slime green tint
    // pixel_data is 0-255 intensity
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            vga_r <= 4'h0;
            vga_g <= 4'h0;
            vga_b <= 4'h0;
        end
        else if (visible) begin
            // Scale 8-bit to 4-bit and apply green tint
            // R = intensity * 0.78, G = intensity, B = intensity * 0.78
            vga_r <= (pixel_data[7:4] * 4'd13) >> 4;  // ~0.8
            vga_g <= pixel_data[7:4];                  // Full green
            vga_b <= (pixel_data[7:4] * 4'd13) >> 4;  // ~0.8
        end
        else begin
            vga_r <= 4'h0;
            vga_g <= 4'h0;
            vga_b <= 4'h0;
        end
    end

endmodule
