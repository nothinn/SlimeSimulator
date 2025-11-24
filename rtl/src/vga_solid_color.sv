// Simple VGA Solid Color Test
// Outputs a solid color to help diagnose VGA hardware issues
// Useful for testing basic VGA connectivity

module vga_solid_color (
    input  logic clk_100mhz,
    input  logic btnr,           // Reset
    input  logic [2:0] sw,       // Color selection

    output logic [3:0] vga_r,
    output logic [3:0] vga_g,
    output logic [3:0] vga_b,
    output logic vga_hs,
    output logic vga_vs,

    output logic [15:0] led      // Debug LEDs
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
    logic frame_counter;

    // VGA Controller
    vga_controller u_vga (
        .clk(clk_25mhz),
        .rst_n(rst_n),
        .hsync(vga_hs),
        .vsync(vga_vs),
        .vga_r(),  // Unused - we set colors directly
        .vga_g(),
        .vga_b(),
        .pixel_x(pixel_x),
        .pixel_y(pixel_y),
        .pixel_valid(pixel_valid),
        .frame_start(frame_start),
        .pixel_data(8'h00)
    );

    // Frame counter for blinking
    always_ff @(posedge clk_25mhz or negedge rst_n) begin
        if (!rst_n)
            frame_counter <= 1'b0;
        else if (frame_start)
            frame_counter <= frame_counter + 1'b1;
    end

    // Solid color output based on switch selection
    always_ff @(posedge clk_25mhz or negedge rst_n) begin
        if (!rst_n) begin
            vga_r <= 4'h0;
            vga_g <= 4'h0;
            vga_b <= 4'h0;
        end
        else if (pixel_valid) begin
            case (sw[2:0])
                3'b000: begin  // Red
                    vga_r <= 4'hF;
                    vga_g <= 4'h0;
                    vga_b <= 4'h0;
                end
                3'b001: begin  // Green
                    vga_r <= 4'h0;
                    vga_g <= 4'hF;
                    vga_b <= 4'h0;
                end
                3'b010: begin  // Blue
                    vga_r <= 4'h0;
                    vga_g <= 4'h0;
                    vga_b <= 4'hF;
                end
                3'b011: begin  // Yellow (R+G)
                    vga_r <= 4'hF;
                    vga_g <= 4'hF;
                    vga_b <= 4'h0;
                end
                3'b100: begin  // Cyan (G+B)
                    vga_r <= 4'h0;
                    vga_g <= 4'hF;
                    vga_b <= 4'hF;
                end
                3'b101: begin  // Magenta (R+B)
                    vga_r <= 4'hF;
                    vga_g <= 4'h0;
                    vga_b <= 4'hF;
                end
                3'b110: begin  // White
                    vga_r <= 4'hF;
                    vga_g <= 4'hF;
                    vga_b <= 4'hF;
                end
                3'b111: begin  // Blinking white
                    vga_r <= {4{frame_counter}};
                    vga_g <= {4{frame_counter}};
                    vga_b <= {4{frame_counter}};
                end
            endcase
        end
        else begin
            vga_r <= 4'h0;
            vga_g <= 4'h0;
            vga_b <= 4'h0;
        end
    end

    // LED diagnostics
    assign led[2:0] = sw[2:0];              // Selected color
    assign led[3] = rst_n;                  // Reset status
    assign led[4] = clk_25mhz;              // 25MHz clock (should blink ~6Hz at LED update rate)
    assign led[5] = pixel_valid;            // Active during valid pixels
    assign led[6] = frame_start;            // Pulses at frame start (60Hz)
    assign led[7] = frame_counter;          // Blinks at 30Hz (frame counter toggle)
    assign led[8] = vga_hs;                 // Horizontal sync
    assign led[9] = vga_vs;                 // Vertical sync
    assign led[15:10] = 6'h00;

endmodule
