// Agent Processor
// Processes one agent through sensory and motor stages
// Pipelined design for throughput
//
// Pipeline stages:
// 1. Fetch agent from memory
// 2. Compute sensor positions (trig lookup)
// 3. Sample trail map at sensor positions
// 4. Sensory decision (compare F, FL, FR)
// 5. Wait for new angle trig lookup (latency compensation)
// 6. Compute new position (trig lookup)
// 7. Write back agent and deposit trail

module agent_processor #(
    parameter FP_INT_BITS  = 12,
    parameter FP_FRAC_BITS = 12,
    parameter FP_TOTAL     = FP_INT_BITS + FP_FRAC_BITS + 1,  // 25 bits
    parameter TRIG_BITS    = 10,                               // 1024 entry LUT
    parameter WIDTH        = 640,
    parameter HEIGHT       = 480
) (
    input  logic clk,
    input  logic rst_n,

    // Control
    input  logic start,
    input  logic [FP_TOTAL-1:0] sensor_angle,    // Fixed-point sensor angle offset
    input  logic [FP_TOTAL-1:0] sensor_distance, // Fixed-point sensor distance
    input  logic [FP_TOTAL-1:0] turn_speed,      // Fixed-point turn amount
    input  logic [FP_TOTAL-1:0] move_speed,      // Fixed-point move speed
    input  logic [FP_TOTAL-1:0] deposit_amount,  // Trail deposit amount
    output logic busy,
    output logic done,

    // Agent input (from memory)
    input  logic signed [FP_TOTAL-1:0] agent_x_in,
    input  logic signed [FP_TOTAL-1:0] agent_y_in,
    input  logic signed [FP_TOTAL-1:0] agent_angle_in,

    // Agent output (to memory)
    output logic signed [FP_TOTAL-1:0] agent_x_out,
    output logic signed [FP_TOTAL-1:0] agent_y_out,
    output logic signed [FP_TOTAL-1:0] agent_angle_out,
    output logic agent_valid_out,

    // Trail map read interface
    output logic [9:0] trail_read_x,
    output logic [8:0] trail_read_y,
    output logic trail_read_en,
    input  logic [FP_TOTAL-1:0] trail_read_data,
    input  logic trail_read_valid,

    // Trail map write interface (deposit)
    output logic [9:0] trail_write_x,
    output logic [8:0] trail_write_y,
    output logic [FP_TOTAL-1:0] trail_write_data,
    output logic trail_write_en,

    // LFSR interface (for random decisions)
    output logic lfsr_en,
    input  logic lfsr_bit  // LSB of LFSR for random turn direction
);

    // Fixed-point constants
    localparam FP_SCALE = 1 << FP_FRAC_BITS;
    localparam signed [FP_TOTAL-1:0] TWO_PI_FP = FP_TOTAL'($rtoi(2.0 * 3.14159265358979 * FP_SCALE));
    localparam signed [FP_TOTAL-1:0] WIDTH_FP = FP_TOTAL'(WIDTH * FP_SCALE);
    localparam signed [FP_TOTAL-1:0] HEIGHT_FP = FP_TOTAL'(HEIGHT * FP_SCALE);

    // State machine (20 states needs 5 bits)
    typedef enum logic [4:0] {
        IDLE,
        CALC_SENSOR_F_X,      // Calculate forward sensor X component
        CALC_SENSOR_F_Y,      // Calculate forward sensor Y component
        READ_TRAIL_F,
        WAIT_TRAIL_F,
        CALC_SENSOR_L_X,      // Calculate left sensor X
        CALC_SENSOR_L_Y,      // Calculate left sensor Y
        READ_TRAIL_L,
        WAIT_TRAIL_L,
        CALC_SENSOR_R_X,      // Calculate right sensor X
        CALC_SENSOR_R_Y,      // Calculate right sensor Y
        READ_TRAIL_R,
        WAIT_TRAIL_R,
        SENSORY_DECISION,
        WAIT_NEW_ANGLE_TRIG,  // Wait for sin/cos(new_angle) to be valid
        CALC_MOVE_X,          // Calculate dx = cos * speed
        CALC_MOVE_Y,          // Calculate dy = sin * speed
        UPDATE_POS,           // Apply dx, dy and wrap
        WRITE_TRAIL,
        DONE_STATE
    } state_t;

    state_t state, next_state;

    // Registered agent data
    logic signed [FP_TOTAL-1:0] x_reg, y_reg, angle_reg;
    logic signed [FP_TOTAL-1:0] new_x, new_y, new_angle;
    logic signed [FP_TOTAL-1:0] dx, dy;  // Movement deltas

    // Sensor positions and readings
    logic signed [FP_TOTAL-1:0] sensor_x, sensor_y;
    logic [7:0] trail_forward, trail_left, trail_right;

    // Trig LUT interface
    logic [TRIG_BITS-1:0] trig_angle_idx;
    logic signed [FP_TOTAL-1:0] sin_val, cos_val;

    // Trig LUT instance
    trig_lut #(
        .ADDR_BITS(TRIG_BITS),
        .DATA_BITS(FP_TOTAL),
        .FRAC_BITS(FP_FRAC_BITS)
    ) u_trig_lut (
        .clk(clk),
        .angle_idx(trig_angle_idx),
        .sin_out(sin_val),
        .cos_out(cos_val)
    );

    // Fixed-point multiplier
    logic signed [FP_TOTAL-1:0] mult_a, mult_b, mult_result;

    fixed_point_mult #(
        .INT_BITS(FP_INT_BITS),
        .FRAC_BITS(FP_FRAC_BITS)
    ) u_mult (
        .a(mult_a),
        .b(mult_b),
        .result(mult_result)
    );

    // Angle to LUT index conversion
    // idx = (angle * TABLE_SIZE) / TWO_PI
    // Simplified: idx = angle[TRIG_BITS+FRAC_BITS-1:FRAC_BITS] when TWO_PI maps to TABLE_SIZE
    function automatic [TRIG_BITS-1:0] angle_to_idx(input signed [FP_TOTAL-1:0] angle);
        logic signed [FP_TOTAL-1:0] normalized;
        logic [24:0] scaled;  // Need enough bits for (normalized << 10)
        // Normalize angle to [0, TWO_PI) using bounded operations
        normalized = angle;
        // Handle negative angles (max 2 iterations needed for typical angles)
        if (normalized < 0) normalized = normalized + TWO_PI_FP;
        if (normalized < 0) normalized = normalized + TWO_PI_FP;
        // Handle angles >= TWO_PI (max 2 iterations needed for typical angles)
        if (normalized >= TWO_PI_FP) normalized = normalized - TWO_PI_FP;
        if (normalized >= TWO_PI_FP) normalized = normalized - TWO_PI_FP;
        // Scale from [0, TWO_PI) to [0, 1024) by multiplying by 1024 and dividing by TWO_PI_FP
        // Formula: idx = (angle * 1024) / (2π in FP) = (angle << 10) / 25737
        // Use truncation (not rounding) to match Python's int() behavior
        scaled = (normalized << 10) / 25737;
        return scaled[TRIG_BITS-1:0];
    endfunction

    // Position to pixel coordinate
    // FIX #2: Truncate toward zero (Python semantics), not toward -∞ (arithmetic shift)
    function automatic [9:0] fp_to_pixel_x(input signed [FP_TOTAL-1:0] fp_val);
        logic signed [FP_TOTAL-1:0] pixel;
        if (fp_val >= 0) begin
            pixel = fp_val >> FP_FRAC_BITS;  // Logical shift for positive
        end else begin
            // For negative: truncate toward zero by negating, shifting, negating back
            pixel = -((-fp_val - 1) >> FP_FRAC_BITS) - 1;
        end
        // Wrap to [0, WIDTH)
        if (pixel < 0) pixel = pixel + WIDTH;
        if (pixel >= WIDTH) pixel = pixel - WIDTH;
        return pixel[9:0];
    endfunction

    function automatic [8:0] fp_to_pixel_y(input signed [FP_TOTAL-1:0] fp_val);
        logic signed [FP_TOTAL-1:0] pixel;
        if (fp_val >= 0) begin
            pixel = fp_val >> FP_FRAC_BITS;
        end else begin
            pixel = -((-fp_val - 1) >> FP_FRAC_BITS) - 1;
        end
        if (pixel < 0) pixel = pixel + HEIGHT;
        if (pixel >= HEIGHT) pixel = pixel - HEIGHT;
        return pixel[8:0];
    endfunction

    // Intermediate calculations
    logic signed [FP_TOTAL-1:0] current_sense_angle;

    // State register
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
        end
        else begin
            state <= next_state;
        end
    end

    // Next state logic
    always_comb begin
        next_state = state;
        case (state)
            IDLE:
                if (start) next_state = CALC_SENSOR_F_X;

            // Forward sensor
            CALC_SENSOR_F_X: next_state = CALC_SENSOR_F_Y;
            CALC_SENSOR_F_Y: next_state = READ_TRAIL_F;
            READ_TRAIL_F:    next_state = WAIT_TRAIL_F;
            WAIT_TRAIL_F:
                if (trail_read_valid) next_state = CALC_SENSOR_L_X;

            // Left sensor
            CALC_SENSOR_L_X: next_state = CALC_SENSOR_L_Y;
            CALC_SENSOR_L_Y: next_state = READ_TRAIL_L;
            READ_TRAIL_L:    next_state = WAIT_TRAIL_L;
            WAIT_TRAIL_L:
                if (trail_read_valid) next_state = CALC_SENSOR_R_X;

            // Right sensor
            CALC_SENSOR_R_X: next_state = CALC_SENSOR_R_Y;
            CALC_SENSOR_R_Y: next_state = READ_TRAIL_R;
            READ_TRAIL_R:    next_state = WAIT_TRAIL_R;
            WAIT_TRAIL_R:
                if (trail_read_valid) next_state = SENSORY_DECISION;

            // Decision and movement
            SENSORY_DECISION: next_state = WAIT_NEW_ANGLE_TRIG;
            WAIT_NEW_ANGLE_TRIG: next_state = CALC_MOVE_X;
            CALC_MOVE_X:      next_state = CALC_MOVE_Y;
            CALC_MOVE_Y:      next_state = UPDATE_POS;
            UPDATE_POS:       next_state = WRITE_TRAIL;
            WRITE_TRAIL:      next_state = DONE_STATE;
            DONE_STATE:       next_state = IDLE;

            default: next_state = IDLE;
        endcase
    end

    // Datapath
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            x_reg <= '0;
            y_reg <= '0;
            angle_reg <= '0;
            new_angle <= '0;
            new_x <= '0;
            new_y <= '0;
            dx <= '0;
            dy <= '0;
            sensor_x <= '0;
            sensor_y <= '0;
            trail_forward <= '0;
            trail_left <= '0;
            trail_right <= '0;
        end
        else begin
            case (state)
                IDLE: begin
                    if (start) begin
                        x_reg <= agent_x_in;
                        y_reg <= agent_y_in;
                        angle_reg <= agent_angle_in;
                    end
                end

                // Forward sensor calculation
                CALC_SENSOR_F_X: begin
                    // dx = cos(angle) * sensor_distance (mult_result)
                    sensor_x <= x_reg + mult_result;
                end

                CALC_SENSOR_F_Y: begin
                    // dy = sin(angle) * sensor_distance
                    sensor_y <= y_reg + mult_result;
                end

                WAIT_TRAIL_F: begin
                    if (trail_read_valid) begin
                        trail_forward <= trail_read_data[7:0];
                    end
                end

                // Left sensor calculation
                CALC_SENSOR_L_X: begin
                    sensor_x <= x_reg + mult_result;
                end

                CALC_SENSOR_L_Y: begin
                    sensor_y <= y_reg + mult_result;
                end

                WAIT_TRAIL_L: begin
                    if (trail_read_valid) begin
                        trail_left <= trail_read_data[7:0];
                    end
                end

                // Right sensor calculation
                CALC_SENSOR_R_X: begin
                    sensor_x <= x_reg + mult_result;
                end

                CALC_SENSOR_R_Y: begin
                    sensor_y <= y_reg + mult_result;
                end

                WAIT_TRAIL_R: begin
                    if (trail_read_valid) begin
                        trail_right <= trail_read_data[7:0];
                    end
                end

                SENSORY_DECISION: begin
                    // Sensory decision logic (EXACTLY matches Python slime_simulator.py)
                    // case1: F > FL AND F > FR -> no change
                    if ((trail_forward > trail_left) && (trail_forward > trail_right)) begin
                        new_angle <= angle_reg;
                    end
                    // case2: F < FL AND F < FR -> random turn
                    else if ((trail_forward < trail_left) && (trail_forward < trail_right)) begin
                        new_angle <= lfsr_bit ? (angle_reg + turn_speed) : (angle_reg - turn_speed);
                    end
                    // case3: FL < FR AND NOT case1 AND NOT case2 -> turn right
                    else if ((trail_left < trail_right)) begin
                        new_angle <= angle_reg - turn_speed;
                    end
                    // case4: FR < FL AND NOT case1 AND NOT case2 AND NOT case3 -> turn left
                    // (only executed if FL >= FR after case3 check)
                    else if ((trail_right < trail_left)) begin
                        new_angle <= angle_reg + turn_speed;
                    end
                    // Fallback: all equal (or FL == FR), no change
                    else begin
                        new_angle <= angle_reg;
                    end
                end

                CALC_MOVE_X: begin
                    // dx = cos(new_angle) * move_speed
                    dx <= mult_result;
                end

                CALC_MOVE_Y: begin
                    // dy = sin(new_angle) * move_speed
                    dy <= mult_result;
                end

                UPDATE_POS: begin
                    // FIX #4: Complete wrapping for multiple boundary crossings
                    // Use proper modulo wrapping, not just single-wrap if-else
                    logic signed [FP_TOTAL-1:0] sum_x, sum_y;
                    logic signed [FP_TOTAL-1:0] wrapped_x, wrapped_y;

                    sum_x = x_reg + dx;
                    sum_y = y_reg + dy;

                    // Wrap with proper modulo: ((val % range) + range) % range
                    // This handles multiple boundary crossings
                    wrapped_x = ((sum_x % WIDTH_FP) + WIDTH_FP) % WIDTH_FP;
                    wrapped_y = ((sum_y % HEIGHT_FP) + HEIGHT_FP) % HEIGHT_FP;

                    new_x <= wrapped_x;
                    new_y <= wrapped_y;
                end

                default: ;
            endcase
        end
    end

    // Trig angle index selection
    always_comb begin
        case (state)
            CALC_SENSOR_F_X, CALC_SENSOR_F_Y:
                current_sense_angle = angle_reg;
            CALC_SENSOR_L_X, CALC_SENSOR_L_Y:
                current_sense_angle = angle_reg + sensor_angle;
            CALC_SENSOR_R_X, CALC_SENSOR_R_Y:
                current_sense_angle = angle_reg - sensor_angle;
            CALC_MOVE_X, CALC_MOVE_Y:
                current_sense_angle = new_angle;
            default:
                current_sense_angle = angle_reg;
        endcase
        trig_angle_idx = angle_to_idx(current_sense_angle);
    end

    // Trail read address
    always_comb begin
        trail_read_x = fp_to_pixel_x(sensor_x);
        trail_read_y = fp_to_pixel_y(sensor_y);
    end

    // Output assignments
    assign busy = (state != IDLE);
    assign done = (state == DONE_STATE);
    assign agent_x_out = new_x;
    assign agent_y_out = new_y;
    assign agent_angle_out = new_angle;
    assign agent_valid_out = (state == DONE_STATE);

    assign trail_read_en = (state == READ_TRAIL_F) || (state == READ_TRAIL_L) || (state == READ_TRAIL_R);
    assign trail_write_x = fp_to_pixel_x(new_x);
    assign trail_write_y = fp_to_pixel_y(new_y);
    assign trail_write_data = deposit_amount;
    assign trail_write_en = (state == WRITE_TRAIL);

    assign lfsr_en = (state == SENSORY_DECISION);

    // Multiplier input selection
    always_comb begin
        mult_b = '0;
        case (state)
            // Sensor calculations
            CALC_SENSOR_F_X, CALC_SENSOR_L_X, CALC_SENSOR_R_X: begin
                mult_a = cos_val;
                mult_b = sensor_distance;
            end
            CALC_SENSOR_F_Y, CALC_SENSOR_L_Y, CALC_SENSOR_R_Y: begin
                mult_a = sin_val;
                mult_b = sensor_distance;
            end
            // Movement calculations
            CALC_MOVE_X: begin
                mult_a = cos_val;
                mult_b = move_speed;
            end
            CALC_MOVE_Y: begin
                mult_a = sin_val;
                mult_b = move_speed;
            end
            default: begin
                mult_a = '0;
                mult_b = '0;
            end
        endcase
    end

endmodule
