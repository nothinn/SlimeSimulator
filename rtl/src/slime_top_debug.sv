// Slime Simulator Top Level with Debug Infrastructure
// Includes ILA, VIO, and JTAG-to-AXI for image capture
//
// Use this version when you need to capture and compare images
// For production, use slime_top.sv without debug overhead

module slime_top_debug #(
    parameter NUM_AGENTS   = 1000,
    parameter FP_INT_BITS  = 12,
    parameter FP_FRAC_BITS = 12,
    parameter LFSR_WIDTH   = 32,
    parameter TRIG_BITS    = 10,
    parameter WIDTH        = 640,
    parameter HEIGHT       = 480
) (
    input  logic clk_100mhz,

    // Buttons
    input  logic btnc,
    input  logic btnu,
    input  logic btnd,
    input  logic btnl,
    input  logic btnr,

    // Switches
    input  logic [15:0] sw,

    // VGA
    output logic [3:0] vga_r,
    output logic [3:0] vga_g,
    output logic [3:0] vga_b,
    output logic vga_hs,
    output logic vga_vs,

    // LEDs
    output logic [15:0] led
);

    // =========================================================================
    // Parameters
    // =========================================================================
    localparam FP_TOTAL = FP_INT_BITS + FP_FRAC_BITS + 1;
    localparam FP_SCALE = 1 << FP_FRAC_BITS;
    localparam TRAIL_ADDR_BITS = $clog2(WIDTH * HEIGHT);

    localparam signed [FP_TOTAL-1:0] DEFAULT_MOVE_SPEED = FP_TOTAL'($rtoi(1.0 * FP_SCALE));
    localparam signed [FP_TOTAL-1:0] DEFAULT_TURN_SPEED = FP_TOTAL'($rtoi(0.3 * FP_SCALE));

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
        if (btnr) begin
            por_counter <= 4'hF;
        end
        else if (por_counter != 0) begin
            por_counter <= por_counter - 1'b1;
        end
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
    wire btn_random   = btn_posedge_pulse[3];
    wire sim_pause    = sw[0];

    // =========================================================================
    // Speed Control
    // =========================================================================
    logic [3:0] speed_level;
    logic signed [FP_TOTAL-1:0] current_move_speed;

    always_ff @(posedge clk_100mhz or negedge rst_n) begin
        if (!rst_n) begin
            speed_level <= 4'd8;
        end
        else begin
            if (btn_speed_up && speed_level < 4'd15)
                speed_level <= speed_level + 1'b1;
            else if (btn_speed_dn && speed_level > 4'd0)
                speed_level <= speed_level - 1'b1;
        end
    end

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

    always_ff @(posedge clk_100mhz or negedge rst_n) begin
        if (!rst_n) begin
            lfsr_load <= 1'b0;
            lfsr_seed <= 32'hDEADBEEF;
        end
        else begin
            lfsr_load <= btn_random;
            if (btn_random)
                lfsr_seed <= lfsr_state ^ {16'h0, clk_div, 14'b0};
        end
    end

    // =========================================================================
    // Trail Map Memory (Dual-port BRAM)
    // =========================================================================
    logic [TRAIL_ADDR_BITS-1:0] trail_addr_a, trail_addr_b, trail_addr_debug;
    logic [7:0] trail_data_a, trail_data_b_out, trail_data_debug;
    logic [7:0] trail_data_b_in;
    logic trail_we_b;

    // Trail memory
    logic [7:0] trail_mem [0:WIDTH*HEIGHT-1];

    // Port A (VGA read)
    always_ff @(posedge clk_25mhz) begin
        trail_data_a <= trail_mem[trail_addr_a];
    end

    // Port B (Agent read/write)
    always_ff @(posedge clk_100mhz) begin
        if (trail_we_b)
            trail_mem[trail_addr_b] <= trail_data_b_in;
        trail_data_b_out <= trail_mem[trail_addr_b];
    end

    // Debug port (read-only, directly accessible)
    always_ff @(posedge clk_100mhz) begin
        trail_data_debug <= trail_mem[trail_addr_debug];
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
    logic debug_freeze;  // From debug wrapper
    logic [31:0] frame_count;

    // Frame counter
    always_ff @(posedge clk_100mhz or negedge rst_n) begin
        if (!rst_n) begin
            frame_count <= 32'b0;
        end
        else if (frame_start) begin
            frame_count <= frame_count + 1'b1;
        end
    end

    always_ff @(posedge clk_100mhz or negedge rst_n) begin
        if (!rst_n) begin
            sim_state <= SIM_IDLE;
            agent_idx <= '0;
            sim_running <= 1'b0;
        end
        else if (!debug_freeze) begin  // Pause when debug is capturing
            case (sim_state)
                SIM_IDLE: begin
                    if (btn_start) begin
                        sim_state <= SIM_INIT;
                        sim_running <= 1'b1;
                    end
                end

                SIM_INIT: begin
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
                    sim_state <= SIM_WAIT_FRAME;
                end

                SIM_WAIT_FRAME: begin
                    if (frame_start)
                        sim_state <= SIM_RUN_AGENTS;
                end

                default: sim_state <= SIM_IDLE;
            endcase

            if (btn_start && sim_running) begin
                sim_state <= SIM_IDLE;
                sim_running <= 1'b0;
            end
        end
    end

    assign lfsr_enable = (sim_state == SIM_RUN_AGENTS) && !sim_pause && !debug_freeze;

    // =========================================================================
    // Debug Infrastructure - VIO
    // =========================================================================
    logic vio_capture_trigger;
    logic vio_freeze;
    logic vio_read_enable;
    logic [TRAIL_ADDR_BITS-1:0] vio_read_addr;
    logic vio_capture_done;

    debug_vio u_vio (
        .clk(clk_100mhz),
        // Inputs to VIO (readable from host)
        .probe_in0(vio_capture_done),
        .probe_in1(frame_count),
        .probe_in2(trail_data_debug),
        // Outputs from VIO (controllable from host)
        .probe_out0(vio_capture_trigger),
        .probe_out1(vio_freeze),
        .probe_out2(vio_read_enable),
        .probe_out3(vio_read_addr)
    );

    // =========================================================================
    // Debug Infrastructure - ILA
    // =========================================================================
    debug_ila u_ila (
        .clk(clk_100mhz),
        .probe0(sim_state),
        .probe1(agent_idx),
        .probe2(lfsr_state),
        .probe3(trail_data_debug),
        .probe4(pixel_x),
        .probe5(pixel_y),
        .probe6(frame_start),
        .probe7(sim_running)
    );

    // =========================================================================
    // Debug Infrastructure - JTAG-to-AXI
    // =========================================================================
    // AXI signals
    logic [31:0] m_axi_araddr, m_axi_awaddr, m_axi_wdata, m_axi_rdata;
    logic m_axi_arvalid, m_axi_arready, m_axi_rvalid, m_axi_rready;
    logic m_axi_awvalid, m_axi_awready, m_axi_wvalid, m_axi_wready;
    logic m_axi_bvalid, m_axi_bready;
    logic [1:0] m_axi_rresp, m_axi_bresp;
    logic [3:0] m_axi_wstrb;

    debug_jtag_axi u_jtag_axi (
        .aclk(clk_100mhz),
        .aresetn(rst_n),
        .m_axi_araddr(m_axi_araddr),
        .m_axi_arvalid(m_axi_arvalid),
        .m_axi_arready(m_axi_arready),
        .m_axi_rdata(m_axi_rdata),
        .m_axi_rresp(m_axi_rresp),
        .m_axi_rvalid(m_axi_rvalid),
        .m_axi_rready(m_axi_rready),
        .m_axi_awaddr(m_axi_awaddr),
        .m_axi_awvalid(m_axi_awvalid),
        .m_axi_awready(m_axi_awready),
        .m_axi_wdata(m_axi_wdata),
        .m_axi_wstrb(m_axi_wstrb),
        .m_axi_wvalid(m_axi_wvalid),
        .m_axi_wready(m_axi_wready),
        .m_axi_bresp(m_axi_bresp),
        .m_axi_bvalid(m_axi_bvalid),
        .m_axi_bready(m_axi_bready)
    );

    // =========================================================================
    // Debug Wrapper - Connects AXI to Trail Memory
    // =========================================================================
    debug_wrapper #(
        .WIDTH(WIDTH),
        .HEIGHT(HEIGHT),
        .ADDR_WIDTH(TRAIL_ADDR_BITS),
        .DATA_WIDTH(8)
    ) u_debug_wrapper (
        .clk(clk_100mhz),
        .rst_n(rst_n),

        // Trail memory
        .trail_rd_addr(trail_addr_debug),
        .trail_rd_data(trail_data_debug),

        // Simulation control
        .debug_freeze(debug_freeze),
        .frame_start(frame_start),
        .frame_count(frame_count),

        // VIO interface
        .vio_capture_trigger(vio_capture_trigger),
        .vio_freeze(vio_freeze),
        .vio_read_enable(vio_read_enable),
        .vio_read_addr(vio_read_addr),
        .vio_capture_done(vio_capture_done),
        .vio_trail_data(),  // Already connected via debug port

        // AXI-Lite interface
        .s_axi_araddr(m_axi_araddr),
        .s_axi_arvalid(m_axi_arvalid),
        .s_axi_arready(m_axi_arready),
        .s_axi_rdata(m_axi_rdata),
        .s_axi_rresp(m_axi_rresp),
        .s_axi_rvalid(m_axi_rvalid),
        .s_axi_rready(m_axi_rready),
        .s_axi_awaddr(m_axi_awaddr),
        .s_axi_awvalid(m_axi_awvalid),
        .s_axi_awready(m_axi_awready),
        .s_axi_wdata(m_axi_wdata),
        .s_axi_wstrb(m_axi_wstrb),
        .s_axi_wvalid(m_axi_wvalid),
        .s_axi_wready(m_axi_wready),
        .s_axi_bresp(m_axi_bresp),
        .s_axi_bvalid(m_axi_bvalid),
        .s_axi_bready(m_axi_bready)
    );

    // =========================================================================
    // LED Status Display
    // =========================================================================
    assign led[3:0]   = speed_level;
    assign led[4]     = sim_running;
    assign led[5]     = sim_pause;
    assign led[6]     = debug_freeze;
    assign led[7]     = vio_capture_done;
    assign led[15:8]  = lfsr_state[7:0];

endmodule
