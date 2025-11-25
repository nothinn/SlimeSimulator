// Debug Wrapper for Trail Memory Access
// Provides AXI-Lite interface for reading trail map via JTAG
// Also includes frame capture and comparison support

module debug_wrapper #(
    parameter WIDTH = 640,
    parameter HEIGHT = 480,
    parameter ADDR_WIDTH = 19,  // ceil(log2(640*480)) = 19
    parameter DATA_WIDTH = 8
) (
    input  logic clk,
    input  logic rst_n,

    // Trail memory interface (directly connected to trail BRAM)
    output logic [ADDR_WIDTH-1:0] trail_rd_addr,
    input  logic [DATA_WIDTH-1:0] trail_rd_data,

    // Simulation control
    output logic debug_freeze,      // Freeze simulation for capture
    input  logic frame_start,       // Frame sync signal
    input  logic [31:0] frame_count,

    // VIO interface signals
    input  logic vio_capture_trigger,
    input  logic vio_freeze,
    input  logic vio_read_enable,
    input  logic [ADDR_WIDTH-1:0] vio_read_addr,
    output logic vio_capture_done,
    output logic [DATA_WIDTH-1:0] vio_trail_data,

    // AXI-Lite Slave Interface (for JTAG-to-AXI access)
    input  logic [31:0] s_axi_araddr,
    input  logic s_axi_arvalid,
    output logic s_axi_arready,
    output logic [31:0] s_axi_rdata,
    output logic [1:0] s_axi_rresp,
    output logic s_axi_rvalid,
    input  logic s_axi_rready,

    // Write channel (for control registers)
    input  logic [31:0] s_axi_awaddr,
    input  logic s_axi_awvalid,
    output logic s_axi_awready,
    input  logic [31:0] s_axi_wdata,
    input  logic [3:0] s_axi_wstrb,
    input  logic s_axi_wvalid,
    output logic s_axi_wready,
    output logic [1:0] s_axi_bresp,
    output logic s_axi_bvalid,
    input  logic s_axi_bready
);

    // =========================================================================
    // Address Map:
    // 0x0000_0000 - 0x0004_AFFF: Trail memory (640*480 = 307200 bytes)
    // 0x0010_0000: Control register
    // 0x0010_0004: Status register
    // 0x0010_0008: Frame count
    // 0x0010_000C: Width
    // 0x0010_0010: Height
    // =========================================================================

    localparam TRAIL_MEM_SIZE = WIDTH * HEIGHT;
    localparam CTRL_REG_BASE = 32'h0010_0000;

    // Control/Status registers
    logic capture_triggered;
    logic capture_done_reg;
    logic freeze_reg;

    // AXI state machine
    typedef enum logic [2:0] {
        AXI_IDLE,
        AXI_READ_TRAIL,
        AXI_READ_WAIT,
        AXI_READ_RESP,
        AXI_WRITE_RESP
    } axi_state_t;

    axi_state_t axi_state;
    logic [31:0] read_addr_reg;
    logic [31:0] read_data_reg;

    // Freeze control (from VIO or AXI)
    assign debug_freeze = vio_freeze | freeze_reg;

    // VIO data output
    assign vio_capture_done = capture_done_reg;
    assign vio_trail_data = trail_rd_data;

    // Trail memory address mux
    always_comb begin
        if (vio_read_enable) begin
            trail_rd_addr = vio_read_addr;
        end
        else begin
            trail_rd_addr = read_addr_reg[ADDR_WIDTH-1:0];
        end
    end

    // Capture trigger logic
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            capture_triggered <= 1'b0;
            capture_done_reg <= 1'b0;
        end
        else begin
            if (vio_capture_trigger && !capture_triggered) begin
                capture_triggered <= 1'b1;
                capture_done_reg <= 1'b0;
            end
            else if (capture_triggered && frame_start) begin
                // Capture on next frame boundary
                capture_done_reg <= 1'b1;
                capture_triggered <= 1'b0;
            end
        end
    end

    // AXI-Lite State Machine
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            axi_state <= AXI_IDLE;
            s_axi_arready <= 1'b0;
            s_axi_rvalid <= 1'b0;
            s_axi_rdata <= 32'b0;
            s_axi_rresp <= 2'b00;
            s_axi_awready <= 1'b0;
            s_axi_wready <= 1'b0;
            s_axi_bvalid <= 1'b0;
            s_axi_bresp <= 2'b00;
            read_addr_reg <= 32'b0;
            read_data_reg <= 32'b0;
            freeze_reg <= 1'b0;
        end
        else begin
            case (axi_state)
                AXI_IDLE: begin
                    s_axi_arready <= 1'b1;
                    s_axi_awready <= 1'b1;
                    s_axi_wready <= 1'b1;
                    s_axi_rvalid <= 1'b0;
                    s_axi_bvalid <= 1'b0;

                    if (s_axi_arvalid && s_axi_arready) begin
                        // Read request
                        read_addr_reg <= s_axi_araddr;
                        s_axi_arready <= 1'b0;

                        if (s_axi_araddr < TRAIL_MEM_SIZE) begin
                            // Trail memory read - need wait cycle for BRAM
                            axi_state <= AXI_READ_TRAIL;
                        end
                        else begin
                            // Register read - immediate
                            axi_state <= AXI_READ_RESP;
                        end
                    end
                    else if (s_axi_awvalid && s_axi_wvalid) begin
                        // Write request
                        s_axi_awready <= 1'b0;
                        s_axi_wready <= 1'b0;

                        // Handle control register writes
                        if (s_axi_awaddr == CTRL_REG_BASE) begin
                            freeze_reg <= s_axi_wdata[0];
                        end

                        axi_state <= AXI_WRITE_RESP;
                    end
                end

                AXI_READ_TRAIL: begin
                    // Wait one cycle for BRAM read
                    axi_state <= AXI_READ_WAIT;
                end

                AXI_READ_WAIT: begin
                    // BRAM data ready, latch it
                    read_data_reg <= {24'b0, trail_rd_data};
                    axi_state <= AXI_READ_RESP;
                end

                AXI_READ_RESP: begin
                    s_axi_rvalid <= 1'b1;
                    s_axi_rresp <= 2'b00;  // OKAY

                    // Select data source based on address
                    if (read_addr_reg < TRAIL_MEM_SIZE) begin
                        s_axi_rdata <= read_data_reg;
                    end
                    else begin
                        case (read_addr_reg)
                            CTRL_REG_BASE:        s_axi_rdata <= {31'b0, freeze_reg};
                            CTRL_REG_BASE + 4:    s_axi_rdata <= {30'b0, capture_done_reg, capture_triggered};
                            CTRL_REG_BASE + 8:    s_axi_rdata <= frame_count;
                            CTRL_REG_BASE + 12:   s_axi_rdata <= WIDTH;
                            CTRL_REG_BASE + 16:   s_axi_rdata <= HEIGHT;
                            default:              s_axi_rdata <= 32'hDEADBEEF;
                        endcase
                    end

                    if (s_axi_rready) begin
                        s_axi_rvalid <= 1'b0;
                        axi_state <= AXI_IDLE;
                    end
                end

                AXI_WRITE_RESP: begin
                    s_axi_bvalid <= 1'b1;
                    s_axi_bresp <= 2'b00;  // OKAY

                    if (s_axi_bready) begin
                        s_axi_bvalid <= 1'b0;
                        axi_state <= AXI_IDLE;
                    end
                end

                default: axi_state <= AXI_IDLE;
            endcase
        end
    end

endmodule


// Simple AXI-Lite to local bus bridge for direct BRAM access
module axi_lite_bram_bridge #(
    parameter ADDR_WIDTH = 19,
    parameter DATA_WIDTH = 8
) (
    input  logic clk,
    input  logic rst_n,

    // AXI-Lite interface
    input  logic [31:0] s_axi_araddr,
    input  logic s_axi_arvalid,
    output logic s_axi_arready,
    output logic [31:0] s_axi_rdata,
    output logic [1:0] s_axi_rresp,
    output logic s_axi_rvalid,
    input  logic s_axi_rready,

    // BRAM interface
    output logic [ADDR_WIDTH-1:0] bram_addr,
    input  logic [DATA_WIDTH-1:0] bram_rdata,
    output logic bram_en
);

    typedef enum logic [1:0] {
        IDLE,
        READ_WAIT,
        READ_RESP
    } state_t;

    state_t state;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            s_axi_arready <= 1'b1;
            s_axi_rvalid <= 1'b0;
            s_axi_rdata <= 32'b0;
            s_axi_rresp <= 2'b00;
            bram_addr <= '0;
            bram_en <= 1'b0;
        end
        else begin
            case (state)
                IDLE: begin
                    s_axi_arready <= 1'b1;
                    bram_en <= 1'b0;

                    if (s_axi_arvalid && s_axi_arready) begin
                        bram_addr <= s_axi_araddr[ADDR_WIDTH-1:0];
                        bram_en <= 1'b1;
                        s_axi_arready <= 1'b0;
                        state <= READ_WAIT;
                    end
                end

                READ_WAIT: begin
                    // Wait for BRAM read latency
                    bram_en <= 1'b0;
                    state <= READ_RESP;
                end

                READ_RESP: begin
                    s_axi_rdata <= {24'b0, bram_rdata};
                    s_axi_rvalid <= 1'b1;
                    s_axi_rresp <= 2'b00;

                    if (s_axi_rready) begin
                        s_axi_rvalid <= 1'b0;
                        state <= IDLE;
                    end
                end

                default: state <= IDLE;
            endcase
        end
    end

endmodule
