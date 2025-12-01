// Quick test to verify DEFAULT_MOVE_SPEED calculation

module test_move_speed;

    localparam FP_INT_BITS  = 12;
    localparam FP_FRAC_BITS = 12;
    localparam FP_TOTAL     = FP_INT_BITS + FP_FRAC_BITS + 1;  // 25 bits
    localparam FP_SCALE     = 1 << FP_FRAC_BITS;  // 4096

    localparam signed [FP_TOTAL-1:0] DEFAULT_MOVE_SPEED = FP_TOTAL'($rtoi(1.0 * FP_SCALE));

    initial begin
        $display("FP_SCALE = %d (0x%07X)", FP_SCALE, FP_SCALE);
        $display("DEFAULT_MOVE_SPEED = %d (0x%07X)", DEFAULT_MOVE_SPEED, DEFAULT_MOVE_SPEED);

        if (DEFAULT_MOVE_SPEED == 4096) begin
            $display("✓ DEFAULT_MOVE_SPEED is correct (4096)");
        end else begin
            $display("✗ ERROR: DEFAULT_MOVE_SPEED is %d, expected 4096", DEFAULT_MOVE_SPEED);
        end

        $finish;
    end

endmodule
