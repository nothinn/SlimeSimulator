// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Tracing implementation internals
#include "verilated_vcd_c.h"
#include "Vslime_top__Syms.h"


VL_ATTR_COLD void Vslime_top___024root__trace_init_sub__TOP__0(Vslime_top___024root* vlSelf, VerilatedVcd* tracep) {
    if (false && vlSelf) {}  // Prevent unused
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root__trace_init_sub__TOP__0\n"); );
    // Init
    const int c = vlSymsp->__Vm_baseCode;
    // Body
    tracep->declBit(c+161,0,"clk_100mhz",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+162,0,"btnc",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+163,0,"btnu",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+164,0,"btnd",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+165,0,"btnl",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+166,0,"btnr",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+167,0,"sw",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 15,0);
    tracep->declBus(c+168,0,"vga_r",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 3,0);
    tracep->declBus(c+169,0,"vga_g",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 3,0);
    tracep->declBus(c+170,0,"vga_b",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 3,0);
    tracep->declBit(c+171,0,"vga_hs",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+172,0,"vga_vs",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+173,0,"led",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 15,0);
    tracep->declBit(c+174,0,"sim_start",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+175,0,"debug_trail_addr",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 18,0);
    tracep->declBus(c+176,0,"debug_trail_data",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 17,0);
    tracep->declBus(c+177,0,"debug_agent_idx",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 9,0);
    tracep->declBus(c+178,0,"debug_agent_sel",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 1,0);
    tracep->declBus(c+179,0,"debug_agent_data",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBit(c+180,0,"debug_agent_write_en",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+181,0,"debug_agent_data_write",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBit(c+182,0,"step_complete_pulse",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->pushPrefix("slime_top", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBus(c+188,0,"NUM_AGENTS",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+189,0,"FP_INT_BITS",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+189,0,"FP_FRAC_BITS",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+190,0,"LFSR_WIDTH",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+188,0,"TRIG_BITS",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+191,0,"WIDTH",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+192,0,"HEIGHT",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+161,0,"clk_100mhz",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+162,0,"btnc",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+163,0,"btnu",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+164,0,"btnd",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+165,0,"btnl",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+166,0,"btnr",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+167,0,"sw",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 15,0);
    tracep->declBus(c+168,0,"vga_r",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 3,0);
    tracep->declBus(c+169,0,"vga_g",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 3,0);
    tracep->declBus(c+170,0,"vga_b",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 3,0);
    tracep->declBit(c+171,0,"vga_hs",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+172,0,"vga_vs",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+173,0,"led",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 15,0);
    tracep->declBit(c+174,0,"sim_start",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+175,0,"debug_trail_addr",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 18,0);
    tracep->declBus(c+176,0,"debug_trail_data",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 17,0);
    tracep->declBus(c+177,0,"debug_agent_idx",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 9,0);
    tracep->declBus(c+178,0,"debug_agent_sel",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 1,0);
    tracep->declBus(c+179,0,"debug_agent_data",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBit(c+180,0,"debug_agent_write_en",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+181,0,"debug_agent_data_write",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBit(c+182,0,"step_complete_pulse",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+193,0,"rst_n",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+194,0,"FP_TOTAL",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+195,0,"FP_SCALE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+196,0,"DEFAULT_MOVE_SPEED",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+197,0,"DEFAULT_TURN_SPEED",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+198,0,"SENSOR_ANGLE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+199,0,"SENSOR_DISTANCE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+200,0,"DEPOSIT_AMOUNT",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+201,0,"DECAY_RATE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBit(c+23,0,"clk_25mhz",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+193,0,"clk_locked",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+24,0,"clk_div",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 1,0);
    tracep->declBus(c+183,0,"btn_raw",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 4,0);
    tracep->declBus(c+25,0,"btn_debounced",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 4,0);
    tracep->declBus(c+26,0,"btn_posedge_pulse",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 4,0);
    tracep->declBit(c+27,0,"btn_start",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+28,0,"btn_speed_up",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+29,0,"btn_speed_dn",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+30,0,"btn_random",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+184,0,"sim_pause",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+31,0,"speed_level",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 3,0);
    tracep->declBus(c+196,0,"current_move_speed",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+32,0,"lfsr_state",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+3,0,"lfsr_enable",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+33,0,"lfsr_load",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+34,0,"lfsr_seed",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+35,0,"coordinator_lfsr_en",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+11,0,"trail_addr_a",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 18,0);
    tracep->declBus(c+4,0,"trail_addr_b",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 18,0);
    tracep->declBus(c+12,0,"trail_data_a",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 17,0);
    tracep->declBus(c+36,0,"trail_data_b_out",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 17,0);
    tracep->declBus(c+5,0,"trail_data_b_in",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 17,0);
    tracep->declBit(c+6,0,"trail_we_b",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+13,0,"pixel_x",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 9,0);
    tracep->declBus(c+14,0,"pixel_y",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 8,0);
    tracep->declBit(c+15,0,"pixel_valid",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+185,0,"frame_start",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+16,0,"frame_count",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+37,0,"sim_state",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 3,0);
    tracep->declBus(c+38,0,"agent_idx",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 16,0);
    tracep->declBit(c+39,0,"sim_running",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+202,0,"FP_DECAY",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+203,0,"trail_val_before_decay",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 17,0);
    tracep->declQuad(c+204,0,"trail_val_after_mult",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 35,0);
    tracep->declBus(c+206,0,"trail_val_decayed",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 17,0);
    tracep->declBus(c+40,0,"orch_trail_addr",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 18,0);
    tracep->declBus(c+41,0,"orch_trail_data",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 17,0);
    tracep->declBit(c+42,0,"orch_trail_we",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+207,0,"orch_trail_read_data",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 17,0);
    tracep->declBus(c+208,0,"pattern_trail_addr",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 18,0);
    tracep->declBus(c+209,0,"pattern_trail_data",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBit(c+7,0,"pattern_trail_we",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+208,0,"sim_trail_addr",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 18,0);
    tracep->declBus(c+209,0,"sim_trail_data",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBit(c+7,0,"sim_trail_we",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+7,0,"use_orchestrator",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+186,0,"coordinator_start",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->pushPrefix("u_coordinator", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBus(c+188,0,"NUM_AGENTS",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+189,0,"FP_INT_BITS",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+189,0,"FP_FRAC_BITS",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+194,0,"FP_TOTAL",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+188,0,"TRIG_BITS",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+191,0,"WIDTH",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+192,0,"HEIGHT",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+161,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+193,0,"rst_n",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+186,0,"start",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+184,0,"pause",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+32,0,"lfsr_state",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+210,0,"sensor_angle",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+211,0,"sensor_distance",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+212,0,"turn_speed",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+213,0,"move_speed",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+214,0,"deposit_amount",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+207,0,"trail_data_b_out",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 17,0);
    tracep->declBus(c+40,0,"trail_addr_b",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 18,0);
    tracep->declBus(c+41,0,"trail_data_b_in",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 17,0);
    tracep->declBit(c+42,0,"trail_we_b",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+35,0,"lfsr_en_request",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+43,0,"done",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+182,0,"step_complete_pulse",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+177,0,"debug_agent_idx",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 9,0);
    tracep->declBus(c+178,0,"debug_agent_sel",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 1,0);
    tracep->declBus(c+179,0,"debug_agent_data",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBit(c+180,0,"debug_agent_write_en",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+181,0,"debug_agent_data_write",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+195,0,"FP_SCALE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+215,0,"AGENT_COUNT_LOG",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->pushPrefix("agent_x", VerilatedTracePrefixType::ARRAY_UNPACKED);
    for (int i = 0; i < 10; ++i) {
        tracep->declBus(c+44+i*1,0,"",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, true,(i+0), 24,0);
    }
    tracep->popPrefix();
    tracep->pushPrefix("agent_y", VerilatedTracePrefixType::ARRAY_UNPACKED);
    for (int i = 0; i < 10; ++i) {
        tracep->declBus(c+54+i*1,0,"",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, true,(i+0), 24,0);
    }
    tracep->popPrefix();
    tracep->pushPrefix("agent_angle", VerilatedTracePrefixType::ARRAY_UNPACKED);
    for (int i = 0; i < 10; ++i) {
        tracep->declBus(c+64+i*1,0,"",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, true,(i+0), 24,0);
    }
    tracep->popPrefix();
    tracep->declBus(c+74,0,"state",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 2,0);
    tracep->declBus(c+8,0,"next_state",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 2,0);
    tracep->declBus(c+75,0,"current_agent_idx",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 3,0);
    tracep->declBus(c+76,0,"step_counter",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+9,0,"proc_start",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+77,0,"proc_busy",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+78,0,"proc_done",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+79,0,"proc_x_in",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+80,0,"proc_y_in",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+81,0,"proc_angle_in",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+82,0,"proc_x_out",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+83,0,"proc_y_out",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+84,0,"proc_angle_out",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBit(c+78,0,"proc_valid_out",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+85,0,"proc_trail_read_x",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 9,0);
    tracep->declBus(c+86,0,"proc_trail_write_x",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 9,0);
    tracep->declBus(c+87,0,"proc_trail_read_y",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 8,0);
    tracep->declBus(c+88,0,"proc_trail_write_y",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 8,0);
    tracep->declBus(c+214,0,"proc_trail_write_data",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBit(c+89,0,"proc_trail_read_en",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+42,0,"proc_trail_write_en",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+35,0,"proc_lfsr_en",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+90,0,"latched_x_out",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+91,0,"latched_y_out",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+92,0,"latched_angle_out",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBit(c+93,0,"latched_valid",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+94,0,"prev_idx",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 3,0);
    tracep->declBit(c+95,0,"step_just_completed",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+96,0,"step_freeze_cycle",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+97,0,"step_writeback_cycle",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+98,0,"lfsr_bit",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+85,0,"read_x",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 9,0);
    tracep->declBus(c+86,0,"write_x",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 9,0);
    tracep->declBus(c+87,0,"read_y",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 8,0);
    tracep->declBus(c+88,0,"write_y",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 8,0);
    tracep->declBus(c+99,0,"read_addr",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 18,0);
    tracep->declBus(c+100,0,"write_addr",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 18,0);
    tracep->declBus(c+216,0,"trail_write_fp",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 17,0);
    tracep->declBus(c+187,0,"debug_idx_safe",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 3,0);
    tracep->pushPrefix("u_processor", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBus(c+189,0,"FP_INT_BITS",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+189,0,"FP_FRAC_BITS",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+194,0,"FP_TOTAL",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+188,0,"TRIG_BITS",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+191,0,"WIDTH",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+192,0,"HEIGHT",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+161,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+193,0,"rst_n",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+9,0,"start",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+210,0,"sensor_angle",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+211,0,"sensor_distance",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+212,0,"turn_speed",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+213,0,"move_speed",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+214,0,"deposit_amount",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBit(c+77,0,"busy",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+78,0,"done",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+79,0,"agent_x_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+80,0,"agent_y_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+81,0,"agent_angle_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+82,0,"agent_x_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+83,0,"agent_y_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+84,0,"agent_angle_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBit(c+78,0,"agent_valid_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+85,0,"trail_read_x",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 9,0);
    tracep->declBus(c+87,0,"trail_read_y",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 8,0);
    tracep->declBit(c+89,0,"trail_read_en",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+217,0,"trail_read_data",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBit(c+193,0,"trail_read_valid",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+86,0,"trail_write_x",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 9,0);
    tracep->declBus(c+88,0,"trail_write_y",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 8,0);
    tracep->declBus(c+214,0,"trail_write_data",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBit(c+42,0,"trail_write_en",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+35,0,"lfsr_en",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+98,0,"lfsr_bit",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+195,0,"FP_SCALE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+218,0,"TWO_PI_FP",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+219,0,"WIDTH_FP",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+220,0,"HEIGHT_FP",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+101,0,"state",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 4,0);
    tracep->declBus(c+10,0,"next_state",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 4,0);
    tracep->declBus(c+102,0,"x_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+103,0,"y_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+104,0,"angle_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+82,0,"new_x",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+83,0,"new_y",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+84,0,"new_angle",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+105,0,"dx",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+106,0,"dy",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+107,0,"sensor_x",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+108,0,"sensor_y",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+109,0,"trail_forward",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+110,0,"trail_left",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+111,0,"trail_right",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+112,0,"trig_angle_idx",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 9,0);
    tracep->declBus(c+113,0,"sin_val",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+114,0,"cos_val",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+115,0,"mult_a",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+116,0,"mult_b",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+117,0,"mult_result",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+118,0,"current_sense_angle",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->pushPrefix("u_mult", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBus(c+189,0,"INT_BITS",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+189,0,"FRAC_BITS",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+194,0,"TOTAL_BITS",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+115,0,"a",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+116,0,"b",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+117,0,"result",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declQuad(c+119,0,"full_product",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 49,0);
    tracep->popPrefix();
    tracep->pushPrefix("u_trig_lut", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBus(c+188,0,"ADDR_BITS",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+194,0,"DATA_BITS",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+189,0,"FRAC_BITS",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declArray(c+221,0,"SIN_FILE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 87,0);
    tracep->declArray(c+224,0,"COS_FILE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 87,0);
    tracep->declBit(c+161,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+112,0,"angle_idx",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 9,0);
    tracep->declBus(c+113,0,"sin_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+114,0,"cos_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+227,0,"TABLE_SIZE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->popPrefix();
    tracep->pushPrefix("unnamedblk1", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBus(c+121,0,"sum_x",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+122,0,"sum_y",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+123,0,"wrapped_x",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->declBus(c+124,0,"wrapped_y",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 24,0);
    tracep->popPrefix();
    tracep->popPrefix();
    tracep->pushPrefix("unnamedblk1", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBus(c+1,0,"i",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::INT, false,-1, 31,0);
    tracep->popPrefix();
    tracep->popPrefix();
    tracep->pushPrefix("u_debouncer", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBus(c+228,0,"NUM_BUTTONS",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+229,0,"CLK_FREQ",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+230,0,"DEBOUNCE_MS",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+161,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+193,0,"rst_n",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+183,0,"btn_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 4,0);
    tracep->declBus(c+25,0,"btn_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 4,0);
    tracep->declBus(c+26,0,"btn_posedge",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 4,0);
    tracep->declBus(c+125,0,"btn_negedge",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 4,0);
    tracep->pushPrefix("gen_debouncer[0]", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->pushPrefix("u_debouncer", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBus(c+229,0,"CLK_FREQ",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+230,0,"DEBOUNCE_MS",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+161,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+193,0,"rst_n",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+162,0,"btn_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+126,0,"btn_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+27,0,"btn_posedge",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+127,0,"btn_negedge",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+231,0,"DEBOUNCE_CYCLES",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+232,0,"COUNTER_BITS",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+128,0,"counter",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 20,0);
    tracep->declBit(c+129,0,"btn_sync_0",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+130,0,"btn_sync_1",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+126,0,"btn_stable",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+131,0,"btn_stable_prev",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->popPrefix();
    tracep->popPrefix();
    tracep->pushPrefix("gen_debouncer[1]", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->pushPrefix("u_debouncer", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBus(c+229,0,"CLK_FREQ",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+230,0,"DEBOUNCE_MS",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+161,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+193,0,"rst_n",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+163,0,"btn_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+132,0,"btn_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+28,0,"btn_posedge",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+133,0,"btn_negedge",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+231,0,"DEBOUNCE_CYCLES",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+232,0,"COUNTER_BITS",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+134,0,"counter",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 20,0);
    tracep->declBit(c+135,0,"btn_sync_0",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+136,0,"btn_sync_1",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+132,0,"btn_stable",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+137,0,"btn_stable_prev",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->popPrefix();
    tracep->popPrefix();
    tracep->pushPrefix("gen_debouncer[2]", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->pushPrefix("u_debouncer", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBus(c+229,0,"CLK_FREQ",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+230,0,"DEBOUNCE_MS",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+161,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+193,0,"rst_n",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+164,0,"btn_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+138,0,"btn_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+29,0,"btn_posedge",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+139,0,"btn_negedge",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+231,0,"DEBOUNCE_CYCLES",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+232,0,"COUNTER_BITS",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+140,0,"counter",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 20,0);
    tracep->declBit(c+141,0,"btn_sync_0",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+142,0,"btn_sync_1",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+138,0,"btn_stable",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+143,0,"btn_stable_prev",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->popPrefix();
    tracep->popPrefix();
    tracep->pushPrefix("gen_debouncer[3]", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->pushPrefix("u_debouncer", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBus(c+229,0,"CLK_FREQ",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+230,0,"DEBOUNCE_MS",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+161,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+193,0,"rst_n",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+165,0,"btn_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+144,0,"btn_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+30,0,"btn_posedge",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+145,0,"btn_negedge",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+231,0,"DEBOUNCE_CYCLES",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+232,0,"COUNTER_BITS",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+146,0,"counter",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 20,0);
    tracep->declBit(c+147,0,"btn_sync_0",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+148,0,"btn_sync_1",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+144,0,"btn_stable",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+149,0,"btn_stable_prev",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->popPrefix();
    tracep->popPrefix();
    tracep->pushPrefix("gen_debouncer[4]", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->pushPrefix("u_debouncer", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBus(c+229,0,"CLK_FREQ",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+230,0,"DEBOUNCE_MS",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+161,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+193,0,"rst_n",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+166,0,"btn_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+150,0,"btn_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+151,0,"btn_posedge",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+152,0,"btn_negedge",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+231,0,"DEBOUNCE_CYCLES",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+232,0,"COUNTER_BITS",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+153,0,"counter",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 20,0);
    tracep->declBit(c+154,0,"btn_sync_0",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+155,0,"btn_sync_1",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+150,0,"btn_stable",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+156,0,"btn_stable_prev",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->popPrefix();
    tracep->popPrefix();
    tracep->popPrefix();
    tracep->pushPrefix("u_lfsr", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBus(c+190,0,"WIDTH",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+233,0,"SEED",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+161,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+193,0,"rst_n",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+3,0,"enable",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+33,0,"load",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+34,0,"seed_val",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+32,0,"lfsr_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+157,0,"valid",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+32,0,"lfsr_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+158,0,"feedback",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->popPrefix();
    tracep->pushPrefix("u_trail_ram", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBus(c+191,0,"WIDTH",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+192,0,"HEIGHT",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+234,0,"DATA_WIDTH",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+235,0,"PIPELINE_STAGES",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+23,0,"clk_a",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+193,0,"en_a",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+11,0,"addr_a",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 18,0);
    tracep->declBus(c+12,0,"data_a",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 17,0);
    tracep->declBit(c+161,0,"clk_b",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+193,0,"en_b",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+4,0,"addr_b",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 18,0);
    tracep->declBus(c+5,0,"data_b_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 17,0);
    tracep->declBit(c+6,0,"we_b",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+36,0,"data_b_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 17,0);
    tracep->declBus(c+12,0,"mem_out_a",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 17,0);
    tracep->declBus(c+36,0,"mem_out_b",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 17,0);
    tracep->pushPrefix("pipe_a", VerilatedTracePrefixType::ARRAY_UNPACKED);
    for (int i = 0; i < 2; ++i) {
        tracep->declBus(c+17+i*1,0,"",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, true,(i+0), 17,0);
    }
    tracep->popPrefix();
    tracep->pushPrefix("pipe_b", VerilatedTracePrefixType::ARRAY_UNPACKED);
    for (int i = 0; i < 2; ++i) {
        tracep->declBus(c+159+i*1,0,"",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, true,(i+0), 17,0);
    }
    tracep->popPrefix();
    tracep->pushPrefix("unnamedblk1", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBus(c+2,0,"i",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::INT, false,-1, 31,0);
    tracep->popPrefix();
    tracep->popPrefix();
    tracep->pushPrefix("u_vga", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBus(c+236,0,"H_VISIBLE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+237,0,"H_FRONT",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+238,0,"H_SYNC",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+239,0,"H_BACK",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+240,0,"V_VISIBLE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+188,0,"V_FRONT",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+241,0,"V_SYNC",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+242,0,"V_BACK",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+23,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+193,0,"rst_n",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+171,0,"hsync",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+172,0,"vsync",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+168,0,"vga_r",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 3,0);
    tracep->declBus(c+169,0,"vga_g",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 3,0);
    tracep->declBus(c+170,0,"vga_b",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 3,0);
    tracep->declBus(c+13,0,"pixel_x",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 9,0);
    tracep->declBus(c+14,0,"pixel_y",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 8,0);
    tracep->declBit(c+15,0,"pixel_valid",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+185,0,"frame_start",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+19,0,"pixel_data",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+243,0,"H_TOTAL",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+244,0,"V_TOTAL",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+13,0,"h_count",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 9,0);
    tracep->declBus(c+20,0,"v_count",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 9,0);
    tracep->declBit(c+21,0,"h_visible",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+22,0,"v_visible",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+15,0,"visible",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->popPrefix();
    tracep->popPrefix();
}

VL_ATTR_COLD void Vslime_top___024root__trace_init_top(Vslime_top___024root* vlSelf, VerilatedVcd* tracep) {
    if (false && vlSelf) {}  // Prevent unused
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root__trace_init_top\n"); );
    // Body
    Vslime_top___024root__trace_init_sub__TOP__0(vlSelf, tracep);
}

VL_ATTR_COLD void Vslime_top___024root__trace_const_0(void* voidSelf, VerilatedVcd::Buffer* bufp);
VL_ATTR_COLD void Vslime_top___024root__trace_full_0(void* voidSelf, VerilatedVcd::Buffer* bufp);
void Vslime_top___024root__trace_chg_0(void* voidSelf, VerilatedVcd::Buffer* bufp);
void Vslime_top___024root__trace_cleanup(void* voidSelf, VerilatedVcd* /*unused*/);

VL_ATTR_COLD void Vslime_top___024root__trace_register(Vslime_top___024root* vlSelf, VerilatedVcd* tracep) {
    if (false && vlSelf) {}  // Prevent unused
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root__trace_register\n"); );
    // Body
    tracep->addConstCb(&Vslime_top___024root__trace_const_0, 0U, vlSelf);
    tracep->addFullCb(&Vslime_top___024root__trace_full_0, 0U, vlSelf);
    tracep->addChgCb(&Vslime_top___024root__trace_chg_0, 0U, vlSelf);
    tracep->addCleanupCb(&Vslime_top___024root__trace_cleanup, vlSelf);
}

VL_ATTR_COLD void Vslime_top___024root__trace_const_0_sub_0(Vslime_top___024root* vlSelf, VerilatedVcd::Buffer* bufp);

VL_ATTR_COLD void Vslime_top___024root__trace_const_0(void* voidSelf, VerilatedVcd::Buffer* bufp) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root__trace_const_0\n"); );
    // Init
    Vslime_top___024root* const __restrict vlSelf VL_ATTR_UNUSED = static_cast<Vslime_top___024root*>(voidSelf);
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    // Body
    Vslime_top___024root__trace_const_0_sub_0((&vlSymsp->TOP), bufp);
}

VL_ATTR_COLD void Vslime_top___024root__trace_const_0_sub_0(Vslime_top___024root* vlSelf, VerilatedVcd::Buffer* bufp) {
    if (false && vlSelf) {}  // Prevent unused
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root__trace_const_0_sub_0\n"); );
    // Init
    uint32_t* const oldp VL_ATTR_UNUSED = bufp->oldp(vlSymsp->__Vm_baseCode);
    VlWide<3>/*95:0*/ __Vtemp_1;
    VlWide<3>/*95:0*/ __Vtemp_2;
    // Body
    bufp->fullIData(oldp+188,(0xaU),32);
    bufp->fullIData(oldp+189,(0xcU),32);
    bufp->fullIData(oldp+190,(0x20U),32);
    bufp->fullIData(oldp+191,(0x140U),32);
    bufp->fullIData(oldp+192,(0xf0U),32);
    bufp->fullBit(oldp+193,(1U));
    bufp->fullIData(oldp+194,(0x19U),32);
    bufp->fullIData(oldp+195,(0x1000U),32);
    bufp->fullIData(oldp+196,(0x1000U),25);
    bufp->fullIData(oldp+197,(0x4ccU),25);
    bufp->fullIData(oldp+198,(0x800U),25);
    bufp->fullIData(oldp+199,(0x9000U),25);
    bufp->fullIData(oldp+200,(0x5000U),25);
    bufp->fullIData(oldp+201,(0xf33U),25);
    bufp->fullIData(oldp+202,(0xf33U),25);
    bufp->fullIData(oldp+203,(vlSelf->slime_top__DOT__trail_val_before_decay),18);
    bufp->fullQData(oldp+204,(vlSelf->slime_top__DOT__trail_val_after_mult),36);
    bufp->fullIData(oldp+206,(vlSelf->slime_top__DOT__trail_val_decayed),18);
    bufp->fullIData(oldp+207,(vlSelf->slime_top__DOT__orch_trail_read_data),18);
    bufp->fullIData(oldp+208,(vlSelf->slime_top__DOT__sim_trail_addr),19);
    bufp->fullCData(oldp+209,(vlSelf->slime_top__DOT__sim_trail_data),8);
    bufp->fullIData(oldp+210,(0x800U),25);
    bufp->fullIData(oldp+211,(0x9000U),25);
    bufp->fullIData(oldp+212,(0x4ccU),25);
    bufp->fullIData(oldp+213,(0x1000U),25);
    bufp->fullIData(oldp+214,(0x5000U),25);
    bufp->fullIData(oldp+215,(4U),32);
    bufp->fullIData(oldp+216,(0x5000U),18);
    bufp->fullIData(oldp+217,(vlSelf->slime_top__DOT__orch_trail_read_data),25);
    bufp->fullIData(oldp+218,(0x6487U),25);
    bufp->fullIData(oldp+219,(0x140000U),25);
    bufp->fullIData(oldp+220,(0xf0000U),25);
    __Vtemp_1[0U] = 0x2e686578U;
    __Vtemp_1[1U] = 0x5f6c7574U;
    __Vtemp_1[2U] = 0x73696eU;
    bufp->fullWData(oldp+221,(__Vtemp_1),88);
    __Vtemp_2[0U] = 0x2e686578U;
    __Vtemp_2[1U] = 0x5f6c7574U;
    __Vtemp_2[2U] = 0x636f73U;
    bufp->fullWData(oldp+224,(__Vtemp_2),88);
    bufp->fullIData(oldp+227,(0x400U),32);
    bufp->fullIData(oldp+228,(5U),32);
    bufp->fullIData(oldp+229,(0x5f5e100U),32);
    bufp->fullIData(oldp+230,(0x14U),32);
    bufp->fullIData(oldp+231,(0x1e8480U),32);
    bufp->fullIData(oldp+232,(0x15U),32);
    bufp->fullIData(oldp+233,(0xdeadbeefU),32);
    bufp->fullIData(oldp+234,(0x12U),32);
    bufp->fullIData(oldp+235,(0U),32);
    bufp->fullIData(oldp+236,(0x280U),32);
    bufp->fullIData(oldp+237,(0x10U),32);
    bufp->fullIData(oldp+238,(0x60U),32);
    bufp->fullIData(oldp+239,(0x30U),32);
    bufp->fullIData(oldp+240,(0x1e0U),32);
    bufp->fullIData(oldp+241,(2U),32);
    bufp->fullIData(oldp+242,(0x21U),32);
    bufp->fullIData(oldp+243,(0x320U),32);
    bufp->fullIData(oldp+244,(0x20dU),32);
}

VL_ATTR_COLD void Vslime_top___024root__trace_full_0_sub_0(Vslime_top___024root* vlSelf, VerilatedVcd::Buffer* bufp);

VL_ATTR_COLD void Vslime_top___024root__trace_full_0(void* voidSelf, VerilatedVcd::Buffer* bufp) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root__trace_full_0\n"); );
    // Init
    Vslime_top___024root* const __restrict vlSelf VL_ATTR_UNUSED = static_cast<Vslime_top___024root*>(voidSelf);
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    // Body
    Vslime_top___024root__trace_full_0_sub_0((&vlSymsp->TOP), bufp);
}

VL_ATTR_COLD void Vslime_top___024root__trace_full_0_sub_0(Vslime_top___024root* vlSelf, VerilatedVcd::Buffer* bufp) {
    if (false && vlSelf) {}  // Prevent unused
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root__trace_full_0_sub_0\n"); );
    // Init
    uint32_t* const oldp VL_ATTR_UNUSED = bufp->oldp(vlSymsp->__Vm_baseCode);
    // Body
    bufp->fullIData(oldp+1,(vlSelf->slime_top__DOT__u_coordinator__DOT__unnamedblk1__DOT__i),32);
    bufp->fullIData(oldp+2,(vlSelf->slime_top__DOT__u_trail_ram__DOT__unnamedblk1__DOT__i),32);
    bufp->fullBit(oldp+3,(vlSelf->slime_top__DOT__lfsr_enable));
    bufp->fullIData(oldp+4,(vlSelf->slime_top__DOT__trail_addr_b),19);
    bufp->fullIData(oldp+5,(vlSelf->slime_top__DOT__trail_data_b_in),18);
    bufp->fullBit(oldp+6,(vlSelf->slime_top__DOT__trail_we_b));
    bufp->fullBit(oldp+7,(vlSelf->slime_top__DOT__pattern_trail_we));
    bufp->fullCData(oldp+8,(vlSelf->slime_top__DOT__u_coordinator__DOT__next_state),3);
    bufp->fullBit(oldp+9,(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_start));
    bufp->fullCData(oldp+10,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__next_state),5);
    bufp->fullIData(oldp+11,(vlSelf->slime_top__DOT__trail_addr_a),19);
    bufp->fullIData(oldp+12,(vlSelf->slime_top__DOT__u_trail_ram__DOT__mem_out_a),18);
    bufp->fullSData(oldp+13,(vlSelf->slime_top__DOT__u_vga__DOT__h_count),10);
    bufp->fullSData(oldp+14,((0x1ffU & (IData)(vlSelf->slime_top__DOT__u_vga__DOT__v_count))),9);
    bufp->fullBit(oldp+15,(vlSelf->slime_top__DOT__pixel_valid));
    bufp->fullIData(oldp+16,(vlSelf->slime_top__DOT__frame_count),32);
    bufp->fullIData(oldp+17,(vlSelf->slime_top__DOT__u_trail_ram__DOT__pipe_a[0]),18);
    bufp->fullIData(oldp+18,(vlSelf->slime_top__DOT__u_trail_ram__DOT__pipe_a[1]),18);
    bufp->fullCData(oldp+19,((0xffU & vlSelf->slime_top__DOT__u_trail_ram__DOT__mem_out_a)),8);
    bufp->fullSData(oldp+20,(vlSelf->slime_top__DOT__u_vga__DOT__v_count),10);
    bufp->fullBit(oldp+21,((0x280U > (IData)(vlSelf->slime_top__DOT__u_vga__DOT__h_count))));
    bufp->fullBit(oldp+22,((0x1e0U > (IData)(vlSelf->slime_top__DOT__u_vga__DOT__v_count))));
    bufp->fullBit(oldp+23,(vlSelf->slime_top__DOT__clk_25mhz));
    bufp->fullCData(oldp+24,(vlSelf->slime_top__DOT__clk_div),2);
    bufp->fullCData(oldp+25,((((IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_stable) 
                               << 4U) | (((IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_stable) 
                                          << 3U) | 
                                         (((IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable) 
                                           << 2U) | 
                                          (((IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable) 
                                            << 1U) 
                                           | (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_stable)))))),5);
    bufp->fullCData(oldp+26,(((((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_stable_prev)) 
                                & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_stable)) 
                               << 4U) | (((IData)(vlSelf->slime_top__DOT__btn_random) 
                                          << 3U) | 
                                         ((((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable_prev)) 
                                            & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable)) 
                                           << 2U) | 
                                          ((((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable_prev)) 
                                             & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable)) 
                                            << 1U) 
                                           | (IData)(vlSelf->slime_top__DOT__btn_start)))))),5);
    bufp->fullBit(oldp+27,(vlSelf->slime_top__DOT__btn_start));
    bufp->fullBit(oldp+28,(((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable_prev)) 
                            & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable))));
    bufp->fullBit(oldp+29,(((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable_prev)) 
                            & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable))));
    bufp->fullBit(oldp+30,(vlSelf->slime_top__DOT__btn_random));
    bufp->fullCData(oldp+31,(vlSelf->slime_top__DOT__speed_level),4);
    bufp->fullIData(oldp+32,(vlSelf->slime_top__DOT__u_lfsr__DOT__lfsr_reg),32);
    bufp->fullBit(oldp+33,(vlSelf->slime_top__DOT__lfsr_load));
    bufp->fullIData(oldp+34,(vlSelf->slime_top__DOT__lfsr_seed),32);
    bufp->fullBit(oldp+35,((0xdU == (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))));
    bufp->fullIData(oldp+36,(vlSelf->slime_top__DOT__u_trail_ram__DOT__mem_out_b),18);
    bufp->fullCData(oldp+37,(vlSelf->slime_top__DOT__sim_state),4);
    bufp->fullIData(oldp+38,(vlSelf->slime_top__DOT__agent_idx),17);
    bufp->fullBit(oldp+39,(vlSelf->slime_top__DOT__sim_running));
    bufp->fullIData(oldp+40,((0x7ffffU & ((0x12U == (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))
                                           ? (((IData)(0x140U) 
                                               * (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_write_y)) 
                                              + (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_write_x))
                                           : (((IData)(0x140U) 
                                               * (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_read_y)) 
                                              + (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_read_x))))),19);
    bufp->fullIData(oldp+41,(((0x12U == (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))
                               ? 0x5000U : 0U)),18);
    bufp->fullBit(oldp+42,((0x12U == (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))));
    bufp->fullBit(oldp+43,((3U == (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__state))));
    bufp->fullIData(oldp+44,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x[0]),25);
    bufp->fullIData(oldp+45,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x[1]),25);
    bufp->fullIData(oldp+46,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x[2]),25);
    bufp->fullIData(oldp+47,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x[3]),25);
    bufp->fullIData(oldp+48,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x[4]),25);
    bufp->fullIData(oldp+49,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x[5]),25);
    bufp->fullIData(oldp+50,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x[6]),25);
    bufp->fullIData(oldp+51,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x[7]),25);
    bufp->fullIData(oldp+52,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x[8]),25);
    bufp->fullIData(oldp+53,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x[9]),25);
    bufp->fullIData(oldp+54,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y[0]),25);
    bufp->fullIData(oldp+55,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y[1]),25);
    bufp->fullIData(oldp+56,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y[2]),25);
    bufp->fullIData(oldp+57,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y[3]),25);
    bufp->fullIData(oldp+58,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y[4]),25);
    bufp->fullIData(oldp+59,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y[5]),25);
    bufp->fullIData(oldp+60,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y[6]),25);
    bufp->fullIData(oldp+61,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y[7]),25);
    bufp->fullIData(oldp+62,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y[8]),25);
    bufp->fullIData(oldp+63,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y[9]),25);
    bufp->fullIData(oldp+64,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle[0]),25);
    bufp->fullIData(oldp+65,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle[1]),25);
    bufp->fullIData(oldp+66,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle[2]),25);
    bufp->fullIData(oldp+67,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle[3]),25);
    bufp->fullIData(oldp+68,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle[4]),25);
    bufp->fullIData(oldp+69,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle[5]),25);
    bufp->fullIData(oldp+70,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle[6]),25);
    bufp->fullIData(oldp+71,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle[7]),25);
    bufp->fullIData(oldp+72,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle[8]),25);
    bufp->fullIData(oldp+73,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle[9]),25);
    bufp->fullCData(oldp+74,(vlSelf->slime_top__DOT__u_coordinator__DOT__state),3);
    bufp->fullCData(oldp+75,(vlSelf->slime_top__DOT__u_coordinator__DOT__current_agent_idx),4);
    bufp->fullIData(oldp+76,(vlSelf->slime_top__DOT__u_coordinator__DOT__step_counter),32);
    bufp->fullBit(oldp+77,((0U != (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))));
    bufp->fullBit(oldp+78,((0x13U == (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))));
    bufp->fullIData(oldp+79,(((9U >= (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__current_agent_idx))
                               ? vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x
                              [vlSelf->slime_top__DOT__u_coordinator__DOT__current_agent_idx]
                               : 0U)),25);
    bufp->fullIData(oldp+80,(((9U >= (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__current_agent_idx))
                               ? vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y
                              [vlSelf->slime_top__DOT__u_coordinator__DOT__current_agent_idx]
                               : 0U)),25);
    bufp->fullIData(oldp+81,(((9U >= (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__current_agent_idx))
                               ? vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle
                              [vlSelf->slime_top__DOT__u_coordinator__DOT__current_agent_idx]
                               : 0U)),25);
    bufp->fullIData(oldp+82,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__new_x),25);
    bufp->fullIData(oldp+83,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__new_y),25);
    bufp->fullIData(oldp+84,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__new_angle),25);
    bufp->fullSData(oldp+85,(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_read_x),10);
    bufp->fullSData(oldp+86,(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_write_x),10);
    bufp->fullSData(oldp+87,(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_read_y),9);
    bufp->fullSData(oldp+88,(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_write_y),9);
    bufp->fullBit(oldp+89,(((3U == (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state)) 
                            | ((7U == (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state)) 
                               | (0xbU == (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))))));
    bufp->fullIData(oldp+90,(vlSelf->slime_top__DOT__u_coordinator__DOT__latched_x_out),25);
    bufp->fullIData(oldp+91,(vlSelf->slime_top__DOT__u_coordinator__DOT__latched_y_out),25);
    bufp->fullIData(oldp+92,(vlSelf->slime_top__DOT__u_coordinator__DOT__latched_angle_out),25);
    bufp->fullBit(oldp+93,(vlSelf->slime_top__DOT__u_coordinator__DOT__latched_valid));
    bufp->fullCData(oldp+94,(vlSelf->slime_top__DOT__u_coordinator__DOT__prev_idx),4);
    bufp->fullBit(oldp+95,(vlSelf->slime_top__DOT__u_coordinator__DOT__step_just_completed));
    bufp->fullBit(oldp+96,(vlSelf->slime_top__DOT__u_coordinator__DOT__step_freeze_cycle));
    bufp->fullBit(oldp+97,(vlSelf->slime_top__DOT__u_coordinator__DOT__step_writeback_cycle));
    bufp->fullBit(oldp+98,((1U & vlSelf->slime_top__DOT__u_lfsr__DOT__lfsr_reg)));
    bufp->fullIData(oldp+99,((0x7ffffU & (((IData)(0x140U) 
                                           * (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_read_y)) 
                                          + (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_read_x)))),19);
    bufp->fullIData(oldp+100,((0x7ffffU & (((IData)(0x140U) 
                                            * (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_write_y)) 
                                           + (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_write_x)))),19);
    bufp->fullCData(oldp+101,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state),5);
    bufp->fullIData(oldp+102,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__x_reg),25);
    bufp->fullIData(oldp+103,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__y_reg),25);
    bufp->fullIData(oldp+104,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_reg),25);
    bufp->fullIData(oldp+105,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__dx),25);
    bufp->fullIData(oldp+106,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__dy),25);
    bufp->fullIData(oldp+107,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__sensor_x),25);
    bufp->fullIData(oldp+108,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__sensor_y),25);
    bufp->fullCData(oldp+109,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__trail_forward),8);
    bufp->fullCData(oldp+110,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__trail_left),8);
    bufp->fullCData(oldp+111,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__trail_right),8);
    bufp->fullSData(oldp+112,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__trig_angle_idx),10);
    bufp->fullIData(oldp+113,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__sin_val),25);
    bufp->fullIData(oldp+114,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__cos_val),25);
    bufp->fullIData(oldp+115,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_a),25);
    bufp->fullIData(oldp+116,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_b),25);
    bufp->fullIData(oldp+117,((0x1ffffffU & (IData)(
                                                    (vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__u_mult__DOT__full_product 
                                                     >> 0xcU)))),25);
    bufp->fullIData(oldp+118,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__current_sense_angle),25);
    bufp->fullQData(oldp+119,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__u_mult__DOT__full_product),50);
    bufp->fullIData(oldp+121,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__unnamedblk1__DOT__sum_x),25);
    bufp->fullIData(oldp+122,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__unnamedblk1__DOT__sum_y),25);
    bufp->fullIData(oldp+123,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__unnamedblk1__DOT__wrapped_x),25);
    bufp->fullIData(oldp+124,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__unnamedblk1__DOT__wrapped_y),25);
    bufp->fullCData(oldp+125,(((((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_stable)) 
                                 & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_stable_prev)) 
                                << 4U) | ((((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_stable)) 
                                            & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_stable_prev)) 
                                           << 3U) | 
                                          ((((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable)) 
                                             & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable_prev)) 
                                            << 2U) 
                                           | ((((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable)) 
                                                & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable_prev)) 
                                               << 1U) 
                                              | ((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_stable)) 
                                                 & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_stable_prev))))))),5);
    bufp->fullBit(oldp+126,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_stable));
    bufp->fullBit(oldp+127,(((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_stable)) 
                             & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_stable_prev))));
    bufp->fullIData(oldp+128,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__counter),21);
    bufp->fullBit(oldp+129,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_sync_0));
    bufp->fullBit(oldp+130,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_sync_1));
    bufp->fullBit(oldp+131,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_stable_prev));
    bufp->fullBit(oldp+132,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable));
    bufp->fullBit(oldp+133,(((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable)) 
                             & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable_prev))));
    bufp->fullIData(oldp+134,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__counter),21);
    bufp->fullBit(oldp+135,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_sync_0));
    bufp->fullBit(oldp+136,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_sync_1));
    bufp->fullBit(oldp+137,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable_prev));
    bufp->fullBit(oldp+138,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable));
    bufp->fullBit(oldp+139,(((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable)) 
                             & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable_prev))));
    bufp->fullIData(oldp+140,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__counter),21);
    bufp->fullBit(oldp+141,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_sync_0));
    bufp->fullBit(oldp+142,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_sync_1));
    bufp->fullBit(oldp+143,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable_prev));
    bufp->fullBit(oldp+144,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_stable));
    bufp->fullBit(oldp+145,(((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_stable)) 
                             & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_stable_prev))));
    bufp->fullIData(oldp+146,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__counter),21);
    bufp->fullBit(oldp+147,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_sync_0));
    bufp->fullBit(oldp+148,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_sync_1));
    bufp->fullBit(oldp+149,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_stable_prev));
    bufp->fullBit(oldp+150,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_stable));
    bufp->fullBit(oldp+151,(((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_stable_prev)) 
                             & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_stable))));
    bufp->fullBit(oldp+152,(((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_stable)) 
                             & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_stable_prev))));
    bufp->fullIData(oldp+153,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__counter),21);
    bufp->fullBit(oldp+154,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_sync_0));
    bufp->fullBit(oldp+155,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_sync_1));
    bufp->fullBit(oldp+156,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_stable_prev));
    bufp->fullBit(oldp+157,(vlSelf->slime_top__DOT__u_lfsr__DOT__valid));
    bufp->fullBit(oldp+158,((1U & VL_REDXOR_32((0xc0000401U 
                                                & vlSelf->slime_top__DOT__u_lfsr__DOT__lfsr_reg)))));
    bufp->fullIData(oldp+159,(vlSelf->slime_top__DOT__u_trail_ram__DOT__pipe_b[0]),18);
    bufp->fullIData(oldp+160,(vlSelf->slime_top__DOT__u_trail_ram__DOT__pipe_b[1]),18);
    bufp->fullBit(oldp+161,(vlSelf->clk_100mhz));
    bufp->fullBit(oldp+162,(vlSelf->btnc));
    bufp->fullBit(oldp+163,(vlSelf->btnu));
    bufp->fullBit(oldp+164,(vlSelf->btnd));
    bufp->fullBit(oldp+165,(vlSelf->btnl));
    bufp->fullBit(oldp+166,(vlSelf->btnr));
    bufp->fullSData(oldp+167,(vlSelf->sw),16);
    bufp->fullCData(oldp+168,(vlSelf->vga_r),4);
    bufp->fullCData(oldp+169,(vlSelf->vga_g),4);
    bufp->fullCData(oldp+170,(vlSelf->vga_b),4);
    bufp->fullBit(oldp+171,(vlSelf->vga_hs));
    bufp->fullBit(oldp+172,(vlSelf->vga_vs));
    bufp->fullSData(oldp+173,(vlSelf->led),16);
    bufp->fullBit(oldp+174,(vlSelf->sim_start));
    bufp->fullIData(oldp+175,(vlSelf->debug_trail_addr),19);
    bufp->fullIData(oldp+176,(vlSelf->debug_trail_data),18);
    bufp->fullSData(oldp+177,(vlSelf->debug_agent_idx),10);
    bufp->fullCData(oldp+178,(vlSelf->debug_agent_sel),2);
    bufp->fullIData(oldp+179,(vlSelf->debug_agent_data),25);
    bufp->fullBit(oldp+180,(vlSelf->debug_agent_write_en));
    bufp->fullIData(oldp+181,(vlSelf->debug_agent_data_write),25);
    bufp->fullBit(oldp+182,(vlSelf->step_complete_pulse));
    bufp->fullCData(oldp+183,((((IData)(vlSelf->btnr) 
                                << 4U) | (((IData)(vlSelf->btnl) 
                                           << 3U) | 
                                          (((IData)(vlSelf->btnd) 
                                            << 2U) 
                                           | (((IData)(vlSelf->btnu) 
                                               << 1U) 
                                              | (IData)(vlSelf->btnc)))))),5);
    bufp->fullBit(oldp+184,((1U & (IData)(vlSelf->sw))));
    bufp->fullBit(oldp+185,(vlSelf->slime_top__DOT__frame_start));
    bufp->fullBit(oldp+186,(((IData)(vlSelf->sim_start) 
                             | (IData)(vlSelf->slime_top__DOT__btn_start))));
    bufp->fullCData(oldp+187,(vlSelf->slime_top__DOT__u_coordinator__DOT__debug_idx_safe),4);
}
