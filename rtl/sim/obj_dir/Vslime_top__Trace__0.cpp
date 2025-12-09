// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Tracing implementation internals
#include "verilated_vcd_c.h"
#include "Vslime_top__Syms.h"


void Vslime_top___024root__trace_chg_0_sub_0(Vslime_top___024root* vlSelf, VerilatedVcd::Buffer* bufp);

void Vslime_top___024root__trace_chg_0(void* voidSelf, VerilatedVcd::Buffer* bufp) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root__trace_chg_0\n"); );
    // Init
    Vslime_top___024root* const __restrict vlSelf VL_ATTR_UNUSED = static_cast<Vslime_top___024root*>(voidSelf);
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    if (VL_UNLIKELY(!vlSymsp->__Vm_activity)) return;
    // Body
    Vslime_top___024root__trace_chg_0_sub_0((&vlSymsp->TOP), bufp);
}

void Vslime_top___024root__trace_chg_0_sub_0(Vslime_top___024root* vlSelf, VerilatedVcd::Buffer* bufp) {
    if (false && vlSelf) {}  // Prevent unused
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root__trace_chg_0_sub_0\n"); );
    // Init
    uint32_t* const oldp VL_ATTR_UNUSED = bufp->oldp(vlSymsp->__Vm_baseCode + 1);
    // Body
    if (VL_UNLIKELY(vlSelf->__Vm_traceActivity[0U])) {
        bufp->chgIData(oldp+0,(vlSelf->slime_top__DOT__u_coordinator__DOT__unnamedblk1__DOT__i),32);
        bufp->chgIData(oldp+1,(vlSelf->slime_top__DOT__u_trail_ram__DOT__unnamedblk1__DOT__i),32);
    }
    if (VL_UNLIKELY((vlSelf->__Vm_traceActivity[1U] 
                     | vlSelf->__Vm_traceActivity[3U]))) {
        bufp->chgBit(oldp+2,(vlSelf->slime_top__DOT__lfsr_enable));
        bufp->chgIData(oldp+3,(vlSelf->slime_top__DOT__trail_addr_b),19);
        bufp->chgIData(oldp+4,(vlSelf->slime_top__DOT__trail_data_b_in),18);
        bufp->chgBit(oldp+5,(vlSelf->slime_top__DOT__trail_we_b));
        bufp->chgBit(oldp+6,(vlSelf->slime_top__DOT__pattern_trail_we));
        bufp->chgCData(oldp+7,(vlSelf->slime_top__DOT__u_coordinator__DOT__next_state),3);
        bufp->chgBit(oldp+8,(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_start));
        bufp->chgCData(oldp+9,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__next_state),5);
    }
    if (VL_UNLIKELY(vlSelf->__Vm_traceActivity[2U])) {
        bufp->chgIData(oldp+10,(vlSelf->slime_top__DOT__trail_addr_a),19);
        bufp->chgIData(oldp+11,(vlSelf->slime_top__DOT__u_trail_ram__DOT__mem_out_a),18);
        bufp->chgSData(oldp+12,(vlSelf->slime_top__DOT__u_vga__DOT__h_count),10);
        bufp->chgSData(oldp+13,((0x1ffU & (IData)(vlSelf->slime_top__DOT__u_vga__DOT__v_count))),9);
        bufp->chgBit(oldp+14,(vlSelf->slime_top__DOT__pixel_valid));
        bufp->chgIData(oldp+15,(vlSelf->slime_top__DOT__frame_count),32);
        bufp->chgIData(oldp+16,(vlSelf->slime_top__DOT__u_trail_ram__DOT__pipe_a[0]),18);
        bufp->chgIData(oldp+17,(vlSelf->slime_top__DOT__u_trail_ram__DOT__pipe_a[1]),18);
        bufp->chgCData(oldp+18,((0xffU & vlSelf->slime_top__DOT__u_trail_ram__DOT__mem_out_a)),8);
        bufp->chgSData(oldp+19,(vlSelf->slime_top__DOT__u_vga__DOT__v_count),10);
        bufp->chgBit(oldp+20,((0x280U > (IData)(vlSelf->slime_top__DOT__u_vga__DOT__h_count))));
        bufp->chgBit(oldp+21,((0x1e0U > (IData)(vlSelf->slime_top__DOT__u_vga__DOT__v_count))));
    }
    if (VL_UNLIKELY(vlSelf->__Vm_traceActivity[3U])) {
        bufp->chgBit(oldp+22,(vlSelf->slime_top__DOT__clk_25mhz));
        bufp->chgCData(oldp+23,(vlSelf->slime_top__DOT__clk_div),2);
        bufp->chgCData(oldp+24,((((IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_stable) 
                                  << 4U) | (((IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_stable) 
                                             << 3U) 
                                            | (((IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable) 
                                                << 2U) 
                                               | (((IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable) 
                                                   << 1U) 
                                                  | (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_stable)))))),5);
        bufp->chgCData(oldp+25,(((((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_stable_prev)) 
                                   & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_stable)) 
                                  << 4U) | (((IData)(vlSelf->slime_top__DOT__btn_random) 
                                             << 3U) 
                                            | ((((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable_prev)) 
                                                 & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable)) 
                                                << 2U) 
                                               | ((((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable_prev)) 
                                                    & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable)) 
                                                   << 1U) 
                                                  | (IData)(vlSelf->slime_top__DOT__btn_start)))))),5);
        bufp->chgBit(oldp+26,(vlSelf->slime_top__DOT__btn_start));
        bufp->chgBit(oldp+27,(((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable_prev)) 
                               & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable))));
        bufp->chgBit(oldp+28,(((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable_prev)) 
                               & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable))));
        bufp->chgBit(oldp+29,(vlSelf->slime_top__DOT__btn_random));
        bufp->chgCData(oldp+30,(vlSelf->slime_top__DOT__speed_level),4);
        bufp->chgIData(oldp+31,(vlSelf->slime_top__DOT__u_lfsr__DOT__lfsr_reg),32);
        bufp->chgBit(oldp+32,(vlSelf->slime_top__DOT__lfsr_load));
        bufp->chgIData(oldp+33,(vlSelf->slime_top__DOT__lfsr_seed),32);
        bufp->chgBit(oldp+34,((0xdU == (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))));
        bufp->chgIData(oldp+35,(vlSelf->slime_top__DOT__u_trail_ram__DOT__mem_out_b),18);
        bufp->chgCData(oldp+36,(vlSelf->slime_top__DOT__sim_state),4);
        bufp->chgIData(oldp+37,(vlSelf->slime_top__DOT__agent_idx),17);
        bufp->chgBit(oldp+38,(vlSelf->slime_top__DOT__sim_running));
        bufp->chgIData(oldp+39,((0x7ffffU & ((0x12U 
                                              == (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))
                                              ? (((IData)(0x140U) 
                                                  * (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_write_y)) 
                                                 + (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_write_x))
                                              : (((IData)(0x140U) 
                                                  * (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_read_y)) 
                                                 + (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_read_x))))),19);
        bufp->chgIData(oldp+40,(((0x12U == (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))
                                  ? 0x5000U : 0U)),18);
        bufp->chgBit(oldp+41,((0x12U == (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))));
        bufp->chgBit(oldp+42,((3U == (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__state))));
        bufp->chgIData(oldp+43,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x[0]),25);
        bufp->chgIData(oldp+44,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x[1]),25);
        bufp->chgIData(oldp+45,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x[2]),25);
        bufp->chgIData(oldp+46,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x[3]),25);
        bufp->chgIData(oldp+47,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x[4]),25);
        bufp->chgIData(oldp+48,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x[5]),25);
        bufp->chgIData(oldp+49,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x[6]),25);
        bufp->chgIData(oldp+50,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x[7]),25);
        bufp->chgIData(oldp+51,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x[8]),25);
        bufp->chgIData(oldp+52,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x[9]),25);
        bufp->chgIData(oldp+53,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y[0]),25);
        bufp->chgIData(oldp+54,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y[1]),25);
        bufp->chgIData(oldp+55,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y[2]),25);
        bufp->chgIData(oldp+56,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y[3]),25);
        bufp->chgIData(oldp+57,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y[4]),25);
        bufp->chgIData(oldp+58,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y[5]),25);
        bufp->chgIData(oldp+59,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y[6]),25);
        bufp->chgIData(oldp+60,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y[7]),25);
        bufp->chgIData(oldp+61,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y[8]),25);
        bufp->chgIData(oldp+62,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y[9]),25);
        bufp->chgIData(oldp+63,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle[0]),25);
        bufp->chgIData(oldp+64,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle[1]),25);
        bufp->chgIData(oldp+65,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle[2]),25);
        bufp->chgIData(oldp+66,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle[3]),25);
        bufp->chgIData(oldp+67,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle[4]),25);
        bufp->chgIData(oldp+68,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle[5]),25);
        bufp->chgIData(oldp+69,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle[6]),25);
        bufp->chgIData(oldp+70,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle[7]),25);
        bufp->chgIData(oldp+71,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle[8]),25);
        bufp->chgIData(oldp+72,(vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle[9]),25);
        bufp->chgCData(oldp+73,(vlSelf->slime_top__DOT__u_coordinator__DOT__state),3);
        bufp->chgCData(oldp+74,(vlSelf->slime_top__DOT__u_coordinator__DOT__current_agent_idx),4);
        bufp->chgIData(oldp+75,(vlSelf->slime_top__DOT__u_coordinator__DOT__step_counter),32);
        bufp->chgBit(oldp+76,((0U != (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))));
        bufp->chgBit(oldp+77,((0x13U == (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))));
        bufp->chgIData(oldp+78,(((9U >= (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__current_agent_idx))
                                  ? vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x
                                 [vlSelf->slime_top__DOT__u_coordinator__DOT__current_agent_idx]
                                  : 0U)),25);
        bufp->chgIData(oldp+79,(((9U >= (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__current_agent_idx))
                                  ? vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y
                                 [vlSelf->slime_top__DOT__u_coordinator__DOT__current_agent_idx]
                                  : 0U)),25);
        bufp->chgIData(oldp+80,(((9U >= (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__current_agent_idx))
                                  ? vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle
                                 [vlSelf->slime_top__DOT__u_coordinator__DOT__current_agent_idx]
                                  : 0U)),25);
        bufp->chgIData(oldp+81,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__new_x),25);
        bufp->chgIData(oldp+82,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__new_y),25);
        bufp->chgIData(oldp+83,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__new_angle),25);
        bufp->chgSData(oldp+84,(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_read_x),10);
        bufp->chgSData(oldp+85,(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_write_x),10);
        bufp->chgSData(oldp+86,(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_read_y),9);
        bufp->chgSData(oldp+87,(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_write_y),9);
        bufp->chgBit(oldp+88,(((3U == (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state)) 
                               | ((7U == (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state)) 
                                  | (0xbU == (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))))));
        bufp->chgIData(oldp+89,(vlSelf->slime_top__DOT__u_coordinator__DOT__latched_x_out),25);
        bufp->chgIData(oldp+90,(vlSelf->slime_top__DOT__u_coordinator__DOT__latched_y_out),25);
        bufp->chgIData(oldp+91,(vlSelf->slime_top__DOT__u_coordinator__DOT__latched_angle_out),25);
        bufp->chgBit(oldp+92,(vlSelf->slime_top__DOT__u_coordinator__DOT__latched_valid));
        bufp->chgCData(oldp+93,(vlSelf->slime_top__DOT__u_coordinator__DOT__prev_idx),4);
        bufp->chgBit(oldp+94,(vlSelf->slime_top__DOT__u_coordinator__DOT__step_just_completed));
        bufp->chgBit(oldp+95,(vlSelf->slime_top__DOT__u_coordinator__DOT__step_freeze_cycle));
        bufp->chgBit(oldp+96,(vlSelf->slime_top__DOT__u_coordinator__DOT__step_writeback_cycle));
        bufp->chgBit(oldp+97,((1U & vlSelf->slime_top__DOT__u_lfsr__DOT__lfsr_reg)));
        bufp->chgIData(oldp+98,((0x7ffffU & (((IData)(0x140U) 
                                              * (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_read_y)) 
                                             + (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_read_x)))),19);
        bufp->chgIData(oldp+99,((0x7ffffU & (((IData)(0x140U) 
                                              * (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_write_y)) 
                                             + (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_write_x)))),19);
        bufp->chgCData(oldp+100,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state),5);
        bufp->chgIData(oldp+101,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__x_reg),25);
        bufp->chgIData(oldp+102,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__y_reg),25);
        bufp->chgIData(oldp+103,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_reg),25);
        bufp->chgIData(oldp+104,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__dx),25);
        bufp->chgIData(oldp+105,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__dy),25);
        bufp->chgIData(oldp+106,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__sensor_x),25);
        bufp->chgIData(oldp+107,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__sensor_y),25);
        bufp->chgCData(oldp+108,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__trail_forward),8);
        bufp->chgCData(oldp+109,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__trail_left),8);
        bufp->chgCData(oldp+110,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__trail_right),8);
        bufp->chgSData(oldp+111,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__trig_angle_idx),10);
        bufp->chgIData(oldp+112,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__sin_val),25);
        bufp->chgIData(oldp+113,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__cos_val),25);
        bufp->chgIData(oldp+114,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_a),25);
        bufp->chgIData(oldp+115,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_b),25);
        bufp->chgIData(oldp+116,((0x1ffffffU & (IData)(
                                                       (vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__u_mult__DOT__full_product 
                                                        >> 0xcU)))),25);
        bufp->chgIData(oldp+117,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__current_sense_angle),25);
        bufp->chgQData(oldp+118,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__u_mult__DOT__full_product),50);
        bufp->chgIData(oldp+120,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__unnamedblk1__DOT__sum_x),25);
        bufp->chgIData(oldp+121,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__unnamedblk1__DOT__sum_y),25);
        bufp->chgIData(oldp+122,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__unnamedblk1__DOT__wrapped_x),25);
        bufp->chgIData(oldp+123,(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__unnamedblk1__DOT__wrapped_y),25);
        bufp->chgCData(oldp+124,(((((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_stable)) 
                                    & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_stable_prev)) 
                                   << 4U) | ((((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_stable)) 
                                               & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_stable_prev)) 
                                              << 3U) 
                                             | ((((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable)) 
                                                  & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable_prev)) 
                                                 << 2U) 
                                                | ((((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable)) 
                                                     & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable_prev)) 
                                                    << 1U) 
                                                   | ((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_stable)) 
                                                      & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_stable_prev))))))),5);
        bufp->chgBit(oldp+125,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_stable));
        bufp->chgBit(oldp+126,(((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_stable)) 
                                & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_stable_prev))));
        bufp->chgIData(oldp+127,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__counter),21);
        bufp->chgBit(oldp+128,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_sync_0));
        bufp->chgBit(oldp+129,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_sync_1));
        bufp->chgBit(oldp+130,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_stable_prev));
        bufp->chgBit(oldp+131,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable));
        bufp->chgBit(oldp+132,(((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable)) 
                                & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable_prev))));
        bufp->chgIData(oldp+133,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__counter),21);
        bufp->chgBit(oldp+134,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_sync_0));
        bufp->chgBit(oldp+135,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_sync_1));
        bufp->chgBit(oldp+136,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable_prev));
        bufp->chgBit(oldp+137,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable));
        bufp->chgBit(oldp+138,(((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable)) 
                                & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable_prev))));
        bufp->chgIData(oldp+139,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__counter),21);
        bufp->chgBit(oldp+140,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_sync_0));
        bufp->chgBit(oldp+141,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_sync_1));
        bufp->chgBit(oldp+142,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable_prev));
        bufp->chgBit(oldp+143,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_stable));
        bufp->chgBit(oldp+144,(((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_stable)) 
                                & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_stable_prev))));
        bufp->chgIData(oldp+145,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__counter),21);
        bufp->chgBit(oldp+146,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_sync_0));
        bufp->chgBit(oldp+147,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_sync_1));
        bufp->chgBit(oldp+148,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_stable_prev));
        bufp->chgBit(oldp+149,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_stable));
        bufp->chgBit(oldp+150,(((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_stable_prev)) 
                                & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_stable))));
        bufp->chgBit(oldp+151,(((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_stable)) 
                                & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_stable_prev))));
        bufp->chgIData(oldp+152,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__counter),21);
        bufp->chgBit(oldp+153,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_sync_0));
        bufp->chgBit(oldp+154,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_sync_1));
        bufp->chgBit(oldp+155,(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_stable_prev));
        bufp->chgBit(oldp+156,(vlSelf->slime_top__DOT__u_lfsr__DOT__valid));
        bufp->chgBit(oldp+157,((1U & VL_REDXOR_32((0xc0000401U 
                                                   & vlSelf->slime_top__DOT__u_lfsr__DOT__lfsr_reg)))));
        bufp->chgIData(oldp+158,(vlSelf->slime_top__DOT__u_trail_ram__DOT__pipe_b[0]),18);
        bufp->chgIData(oldp+159,(vlSelf->slime_top__DOT__u_trail_ram__DOT__pipe_b[1]),18);
    }
    bufp->chgBit(oldp+160,(vlSelf->clk_100mhz));
    bufp->chgBit(oldp+161,(vlSelf->btnc));
    bufp->chgBit(oldp+162,(vlSelf->btnu));
    bufp->chgBit(oldp+163,(vlSelf->btnd));
    bufp->chgBit(oldp+164,(vlSelf->btnl));
    bufp->chgBit(oldp+165,(vlSelf->btnr));
    bufp->chgSData(oldp+166,(vlSelf->sw),16);
    bufp->chgCData(oldp+167,(vlSelf->vga_r),4);
    bufp->chgCData(oldp+168,(vlSelf->vga_g),4);
    bufp->chgCData(oldp+169,(vlSelf->vga_b),4);
    bufp->chgBit(oldp+170,(vlSelf->vga_hs));
    bufp->chgBit(oldp+171,(vlSelf->vga_vs));
    bufp->chgSData(oldp+172,(vlSelf->led),16);
    bufp->chgBit(oldp+173,(vlSelf->sim_start));
    bufp->chgIData(oldp+174,(vlSelf->debug_trail_addr),19);
    bufp->chgIData(oldp+175,(vlSelf->debug_trail_data),18);
    bufp->chgSData(oldp+176,(vlSelf->debug_agent_idx),10);
    bufp->chgCData(oldp+177,(vlSelf->debug_agent_sel),2);
    bufp->chgIData(oldp+178,(vlSelf->debug_agent_data),25);
    bufp->chgBit(oldp+179,(vlSelf->debug_agent_write_en));
    bufp->chgIData(oldp+180,(vlSelf->debug_agent_data_write),25);
    bufp->chgBit(oldp+181,(vlSelf->step_complete_pulse));
    bufp->chgCData(oldp+182,((((IData)(vlSelf->btnr) 
                               << 4U) | (((IData)(vlSelf->btnl) 
                                          << 3U) | 
                                         (((IData)(vlSelf->btnd) 
                                           << 2U) | 
                                          (((IData)(vlSelf->btnu) 
                                            << 1U) 
                                           | (IData)(vlSelf->btnc)))))),5);
    bufp->chgBit(oldp+183,((1U & (IData)(vlSelf->sw))));
    bufp->chgBit(oldp+184,(vlSelf->slime_top__DOT__frame_start));
    bufp->chgBit(oldp+185,(((IData)(vlSelf->sim_start) 
                            | (IData)(vlSelf->slime_top__DOT__btn_start))));
    bufp->chgCData(oldp+186,(vlSelf->slime_top__DOT__u_coordinator__DOT__debug_idx_safe),4);
}

void Vslime_top___024root__trace_cleanup(void* voidSelf, VerilatedVcd* /*unused*/) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root__trace_cleanup\n"); );
    // Init
    Vslime_top___024root* const __restrict vlSelf VL_ATTR_UNUSED = static_cast<Vslime_top___024root*>(voidSelf);
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    // Body
    vlSymsp->__Vm_activity = false;
    vlSymsp->TOP.__Vm_traceActivity[0U] = 0U;
    vlSymsp->TOP.__Vm_traceActivity[1U] = 0U;
    vlSymsp->TOP.__Vm_traceActivity[2U] = 0U;
    vlSymsp->TOP.__Vm_traceActivity[3U] = 0U;
}
