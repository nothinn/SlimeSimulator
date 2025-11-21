// Agent Processor
// Processes one agent through sensory and motor stages
// Pipelined design for throughput
//
// Pipeline stages:
// 1. Fetch agent from memory
// 2. Compute sensor positions (trig lookup)
// 3. Sample trail map at sensor positions
// 4. Sensory decision (compare F, FL, FR)
// 5. Update angle
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

    // State machine
    typedef enum logic [3:0] {
        IDLE,
        CALC_SENSORS,
        WAIT_TRIG_F,
        READ_TRAIL_F,
        WAIT_TRAIL_F,
        READ_TRAIL_LR,
        WAIT_TRAIL_L,
        WAIT_TRAIL_R,
        SENSORY_DECISION,
        CALC_MOVE,
        WAIT_TRIG_MOVE,
        UPDATE_POS,
        WRITE_TRAIL,
        DONE_STATE
    } state_t;

    state_t state, next_state;

    // Registered agent data
    logic signed [FP_TOTAL-1:0] x_reg, y_reg, angle_reg;
    logic signed [FP_TOTAL-1:0] new_x, new_y, new_angle;

    // Sensor readings
    logic signed [FP_TOTAL-1:0] trail_forward, trail_left, trail_right;

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
        // Normalize angle to [0, TWO_PI)
        normalized = angle;
        while (normalized < 0) normalized = normalized + TWO_PI_FP;
        while (normalized >= TWO_PI_FP) normalized = normalized - TWO_PI_FP;
        // Scale to table index
        return normalized[TRIG_BITS + FP_FRAC_BITS - 1 : FP_FRAC_BITS];
    endfunction

    // Position to pixel coordinate
    function automatic [9:0] fp_to_pixel_x(input signed [FP_TOTAL-1:0] fp_val);
        logic signed [FP_TOTAL-1:0] pixel;
        pixel = fp_val >>> FP_FRAC_BITS;  // Arithmetic shift for signed
        // Wrap to [0, WIDTH)
        if (pixel < 0) pixel = pixel + WIDTH;
        if (pixel >= WIDTH) pixel = pixel - WIDTH;
        return pixel[9:0];
    endfunction

    function automatic [8:0] fp_to_pixel_y(input signed [FP_TOTAL-1:0] fp_val);
        logic signed [FP_TOTAL-1:0] pixel;
        pixel = fp_val >>> FP_FRAC_BITS;
        if (pixel < 0) pixel = pixel + HEIGHT;
        if (pixel >= HEIGHT) pixel = pixel - HEIGHT;
        return pixel[8:0];
    endfunction

    // Intermediate calculations
    logic signed [FP_TOTAL-1:0] sense_x, sense_y;
    logic signed [FP_TOTAL-1:0] sense_angle;
    logic [1:0] sensor_phase;  // 0=forward, 1=left, 2=right

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
                if (start) next_state = CALC_SENSORS;

            CALC_SENSORS:
                next_state = WAIT_TRIG_F;

            WAIT_TRIG_F:
                next_state = READ_TRAIL_F;

            READ_TRAIL_F:
                next_state = WAIT_TRAIL_F;

            WAIT_TRAIL_F:
                if (trail_read_valid) next_state = READ_TRAIL_LR;

            READ_TRAIL_LR:
                next_state = WAIT_TRAIL_L;

            WAIT_TRAIL_L:
                if (trail_read_valid) next_state = WAIT_TRAIL_R;

            WAIT_TRAIL_R:
                if (trail_read_valid) next_state = SENSORY_DECISION;

            SENSORY_DECISION:
                next_state = CALC_MOVE;

            CALC_MOVE:
                next_state = WAIT_TRIG_MOVE;

            WAIT_TRIG_MOVE:
                next_state = UPDATE_POS;

            UPDATE_POS:
                next_state = WRITE_TRAIL;

            WRITE_TRAIL:
                next_state = DONE_STATE;

            DONE_STATE:
                next_state = IDLE;

            default:
                next_state = IDLE;
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
            trail_forward <= '0;
            trail_left <= '0;
            trail_right <= '0;
            sensor_phase <= '0;
        end
        else begin
            case (state)
                IDLE: begin
                    if (start) begin
                        x_reg <= agent_x_in;
                        y_reg <= agent_y_in;
                        angle_reg <= agent_angle_in;
                        sensor_phase <= 2'd0;
                    end
                end

                WAIT_TRAIL_F: begin
                    if (trail_read_valid) begin
                        trail_forward <= trail_read_data;
                        sensor_phase <= 2'd1;
                    end
                end

                WAIT_TRAIL_L: begin
                    if (trail_read_valid) begin
                        trail_left <= trail_read_data;
                        sensor_phase <= 2'd2;
                    end
                end

                WAIT_TRAIL_R: begin
                    if (trail_read_valid) begin
                        trail_right <= trail_read_data;
                    end
                end

                SENSORY_DECISION: begin
                    // Implement sensory decision logic
                    // Case 1: F > FL and F > FR -> no change
                    // Case 2: F < FL and F < FR -> random turn
                    // Case 3: FL < FR -> turn right
                    // Case 4: FR < FL -> turn left
                    if ((trail_forward > trail_left) && (trail_forward > trail_right)) begin
                        // Stay facing same direction
                        new_angle <= angle_reg;
                    end
                    else if ((trail_forward < trail_left) && (trail_forward < trail_right)) begin
                        // Random turn
                        new_angle <= lfsr_bit ? (angle_reg + turn_speed) : (angle_reg - turn_speed);
                    end
                    else if (trail_left < trail_right) begin
                        // Turn right
                        new_angle <= angle_reg - turn_speed;
                    end
                    else if (trail_right < trail_left) begin
                        // Turn left
                        new_angle <= angle_reg + turn_speed;
                    end
                    else begin
                        new_angle <= angle_reg;
                    end
                end

                UPDATE_POS: begin
                    // new_x = x + cos(angle) * speed
                    // new_y = y + sin(angle) * speed
                    // mult_result has cos*speed or sin*speed
                    new_x <= x_reg + mult_result;  // Will need proper sequencing
                    new_y <= y_reg + mult_result;

                    // Wrap positions
                    if (new_x < 0) new_x <= new_x + WIDTH_FP;
                    else if (new_x >= WIDTH_FP) new_x <= new_x - WIDTH_FP;

                    if (new_y < 0) new_y <= new_y + HEIGHT_FP;
                    else if (new_y >= HEIGHT_FP) new_y <= new_y - HEIGHT_FP;
                end

                default: ;
            endcase
        end
    end

    // Trig angle index selection
    always_comb begin
        case (state)
            CALC_SENSORS, WAIT_TRIG_F: begin
                case (sensor_phase)
                    2'd0: sense_angle = angle_reg;                    // Forward
                    2'd1: sense_angle = angle_reg + sensor_angle;     // Left
                    2'd2: sense_angle = angle_reg - sensor_angle;     // Right
                    default: sense_angle = angle_reg;
                endcase
            end
            CALC_MOVE, WAIT_TRIG_MOVE:
                sense_angle = new_angle;
            default:
                sense_angle = angle_reg;
        endcase
        trig_angle_idx = angle_to_idx(sense_angle);
    end

    // Trail read address
    always_comb begin
        // Sensor position: pos + cos/sin(angle) * distance
        sense_x = x_reg + mult_result;  // Simplified - needs proper calc
        sense_y = y_reg + mult_result;
        trail_read_x = fp_to_pixel_x(sense_x);
        trail_read_y = fp_to_pixel_y(sense_y);
    end

    // Output assignments
    assign busy = (state != IDLE);
    assign done = (state == DONE_STATE);
    assign agent_x_out = new_x;
    assign agent_y_out = new_y;
    assign agent_angle_out = new_angle;
    assign agent_valid_out = (state == DONE_STATE);

    assign trail_read_en = (state == READ_TRAIL_F) || (state == READ_TRAIL_LR);
    assign trail_write_x = fp_to_pixel_x(new_x);
    assign trail_write_y = fp_to_pixel_y(new_y);
    assign trail_write_data = deposit_amount;
    assign trail_write_en = (state == WRITE_TRAIL);

    assign lfsr_en = (state == SENSORY_DECISION);

    // Multiplier input selection
    always_comb begin
        case (state)
            CALC_SENSORS, READ_TRAIL_F, READ_TRAIL_LR: begin
                mult_a = cos_val;  // or sin_val depending on x/y
                mult_b = sensor_distance;
            end
            CALC_MOVE, UPDATE_POS: begin
                mult_a = cos_val;  // or sin_val
                mult_b = move_speed;
            end
            default: begin
                mult_a = '0;
                mult_b = '0;
            end
        endcase
    end

endmodule
