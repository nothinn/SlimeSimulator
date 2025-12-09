// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vslime_top.h for the primary calling header

#include "Vslime_top__pch.h"
#include "Vslime_top___024root.h"

extern const VlUnpacked<CData/*2:0*/, 16> Vslime_top__ConstPool__TABLE_hd2b3370f_0;
extern const VlUnpacked<CData/*4:0*/, 64> Vslime_top__ConstPool__TABLE_hc133f9f5_0;

VL_INLINE_OPT void Vslime_top___024root___ico_sequent__TOP__0(Vslime_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root___ico_sequent__TOP__0\n"); );
    // Init
    CData/*3:0*/ __Vtableidx1;
    __Vtableidx1 = 0;
    CData/*5:0*/ __Vtableidx2;
    __Vtableidx2 = 0;
    // Body
    vlSelf->slime_top__DOT__lfsr_enable = ((~ (IData)(vlSelf->sw)) 
                                           & (0xdU 
                                              == (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state)));
    vlSelf->led = ((0xff00U & (vlSelf->slime_top__DOT__u_lfsr__DOT__lfsr_reg 
                               << 8U)) | ((0xc0U & 
                                           ((IData)(vlSelf->slime_top__DOT__sim_state) 
                                            << 6U)) 
                                          | ((0x20U 
                                              & ((IData)(vlSelf->sw) 
                                                 << 5U)) 
                                             | (((IData)(vlSelf->slime_top__DOT__sim_running) 
                                                 << 4U) 
                                                | (IData)(vlSelf->slime_top__DOT__speed_level)))));
    __Vtableidx1 = ((((IData)(vlSelf->sim_start) | (IData)(vlSelf->slime_top__DOT__btn_start)) 
                     << 3U) | (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__state));
    vlSelf->slime_top__DOT__u_coordinator__DOT__next_state 
        = Vslime_top__ConstPool__TABLE_hd2b3370f_0[__Vtableidx1];
    vlSelf->slime_top__DOT__u_coordinator__DOT__debug_idx_safe 
        = ((0xaU > (IData)(vlSelf->debug_agent_idx))
            ? (0xfU & (IData)(vlSelf->debug_agent_idx))
            : 0U);
    vlSelf->slime_top__DOT__u_coordinator__DOT__proc_start 
        = ((~ ((IData)(vlSelf->sw) | ((0U != (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state)) 
                                      | (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__step_freeze_cycle)))) 
           & (2U == (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__state)));
    vlSelf->slime_top__DOT__pattern_trail_we = ((~ (IData)(vlSelf->sw)) 
                                                & (2U 
                                                   == (IData)(vlSelf->slime_top__DOT__sim_state)));
    vlSelf->debug_agent_data = ((0U == (IData)(vlSelf->debug_agent_sel))
                                 ? ((9U >= (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__debug_idx_safe))
                                     ? vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x
                                    [vlSelf->slime_top__DOT__u_coordinator__DOT__debug_idx_safe]
                                     : 0U) : ((1U == (IData)(vlSelf->debug_agent_sel))
                                               ? ((9U 
                                                   >= (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__debug_idx_safe))
                                                   ? 
                                                  vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y
                                                  [vlSelf->slime_top__DOT__u_coordinator__DOT__debug_idx_safe]
                                                   : 0U)
                                               : ((2U 
                                                   == (IData)(vlSelf->debug_agent_sel))
                                                   ? 
                                                  ((9U 
                                                    >= (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__debug_idx_safe))
                                                    ? 
                                                   vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle
                                                   [vlSelf->slime_top__DOT__u_coordinator__DOT__debug_idx_safe]
                                                    : 0U)
                                                   : 0U)));
    __Vtableidx2 = (((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_start) 
                     << 5U) | (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state));
    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__next_state 
        = Vslime_top__ConstPool__TABLE_hc133f9f5_0[__Vtableidx2];
    if (vlSelf->slime_top__DOT__pattern_trail_we) {
        if ((0x12U == (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
            vlSelf->slime_top__DOT__trail_we_b = 1U;
            vlSelf->slime_top__DOT__trail_data_b_in = 0x5000U;
            vlSelf->slime_top__DOT__trail_addr_b = 
                (0x7ffffU & (((IData)(0x140U) * (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_write_y)) 
                             + (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_write_x)));
        } else {
            vlSelf->slime_top__DOT__trail_we_b = 0U;
            vlSelf->slime_top__DOT__trail_data_b_in = 0U;
            vlSelf->slime_top__DOT__trail_addr_b = 
                (0x7ffffU & (((IData)(0x140U) * (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_read_y)) 
                             + (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_read_x)));
        }
    } else {
        vlSelf->slime_top__DOT__trail_we_b = vlSelf->slime_top__DOT__pattern_trail_we;
        vlSelf->slime_top__DOT__trail_data_b_in = vlSelf->slime_top__DOT__sim_trail_data;
        vlSelf->slime_top__DOT__trail_addr_b = (0x7ffffU 
                                                & vlSelf->slime_top__DOT__sim_trail_addr);
    }
}

void Vslime_top___024root___eval_ico(Vslime_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root___eval_ico\n"); );
    // Body
    if ((1ULL & vlSelf->__VicoTriggered.word(0U))) {
        Vslime_top___024root___ico_sequent__TOP__0(vlSelf);
        vlSelf->__Vm_traceActivity[1U] = 1U;
    }
}

void Vslime_top___024root___eval_triggers__ico(Vslime_top___024root* vlSelf);

bool Vslime_top___024root___eval_phase__ico(Vslime_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root___eval_phase__ico\n"); );
    // Init
    CData/*0:0*/ __VicoExecute;
    // Body
    Vslime_top___024root___eval_triggers__ico(vlSelf);
    __VicoExecute = vlSelf->__VicoTriggered.any();
    if (__VicoExecute) {
        Vslime_top___024root___eval_ico(vlSelf);
    }
    return (__VicoExecute);
}

void Vslime_top___024root___eval_act(Vslime_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root___eval_act\n"); );
}

VL_INLINE_OPT void Vslime_top___024root___nba_sequent__TOP__0(Vslime_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root___nba_sequent__TOP__0\n"); );
    // Init
    IData/*17:0*/ __Vdlyvval__slime_top__DOT__u_trail_ram__DOT__pipe_a__v0;
    __Vdlyvval__slime_top__DOT__u_trail_ram__DOT__pipe_a__v0 = 0;
    IData/*17:0*/ __Vdlyvval__slime_top__DOT__u_trail_ram__DOT__pipe_a__v1;
    __Vdlyvval__slime_top__DOT__u_trail_ram__DOT__pipe_a__v1 = 0;
    SData/*9:0*/ __Vdly__slime_top__DOT__u_vga__DOT__h_count;
    __Vdly__slime_top__DOT__u_vga__DOT__h_count = 0;
    SData/*9:0*/ __Vdly__slime_top__DOT__u_vga__DOT__v_count;
    __Vdly__slime_top__DOT__u_vga__DOT__v_count = 0;
    // Body
    __Vdly__slime_top__DOT__u_vga__DOT__h_count = vlSelf->slime_top__DOT__u_vga__DOT__h_count;
    __Vdly__slime_top__DOT__u_vga__DOT__v_count = vlSelf->slime_top__DOT__u_vga__DOT__v_count;
    if (vlSelf->slime_top__DOT__frame_start) {
        vlSelf->slime_top__DOT__frame_count = ((IData)(1U) 
                                               + vlSelf->slime_top__DOT__frame_count);
    }
    if ((0x31fU == (IData)(vlSelf->slime_top__DOT__u_vga__DOT__h_count))) {
        __Vdly__slime_top__DOT__u_vga__DOT__h_count = 0U;
        __Vdly__slime_top__DOT__u_vga__DOT__v_count 
            = ((0x20cU == (IData)(vlSelf->slime_top__DOT__u_vga__DOT__v_count))
                ? 0U : (0x3ffU & ((IData)(1U) + (IData)(vlSelf->slime_top__DOT__u_vga__DOT__v_count))));
    } else {
        __Vdly__slime_top__DOT__u_vga__DOT__h_count 
            = (0x3ffU & ((IData)(1U) + (IData)(vlSelf->slime_top__DOT__u_vga__DOT__h_count)));
    }
    __Vdlyvval__slime_top__DOT__u_trail_ram__DOT__pipe_a__v0 
        = vlSelf->slime_top__DOT__u_trail_ram__DOT__mem_out_a;
    __Vdlyvval__slime_top__DOT__u_trail_ram__DOT__pipe_a__v1 
        = vlSelf->slime_top__DOT__u_trail_ram__DOT__pipe_a
        [0U];
    vlSelf->vga_b = 0U;
    vlSelf->vga_r = 0U;
    vlSelf->vga_vs = (1U & (~ ((0x1eaU <= (IData)(vlSelf->slime_top__DOT__u_vga__DOT__v_count)) 
                               & (0x1ecU > (IData)(vlSelf->slime_top__DOT__u_vga__DOT__v_count)))));
    vlSelf->vga_hs = (1U & (~ ((0x290U <= (IData)(vlSelf->slime_top__DOT__u_vga__DOT__h_count)) 
                               & (0x2f0U > (IData)(vlSelf->slime_top__DOT__u_vga__DOT__h_count)))));
    vlSelf->vga_g = ((IData)(vlSelf->slime_top__DOT__pixel_valid)
                      ? (0xfU & (vlSelf->slime_top__DOT__u_trail_ram__DOT__mem_out_a 
                                 >> 4U)) : 0U);
    vlSelf->slime_top__DOT__u_trail_ram__DOT__pipe_a[0U] 
        = __Vdlyvval__slime_top__DOT__u_trail_ram__DOT__pipe_a__v0;
    vlSelf->slime_top__DOT__u_trail_ram__DOT__pipe_a[1U] 
        = __Vdlyvval__slime_top__DOT__u_trail_ram__DOT__pipe_a__v1;
    vlSelf->slime_top__DOT__u_vga__DOT__v_count = __Vdly__slime_top__DOT__u_vga__DOT__v_count;
    vlSelf->slime_top__DOT__u_vga__DOT__h_count = __Vdly__slime_top__DOT__u_vga__DOT__h_count;
    vlSelf->slime_top__DOT__pixel_valid = ((0x280U 
                                            > (IData)(vlSelf->slime_top__DOT__u_vga__DOT__h_count)) 
                                           & (0x1e0U 
                                              > (IData)(vlSelf->slime_top__DOT__u_vga__DOT__v_count)));
    vlSelf->slime_top__DOT__u_trail_ram__DOT__mem_out_a 
        = ((0x12bffU >= (0x1ffffU & vlSelf->slime_top__DOT__trail_addr_a))
            ? vlSelf->slime_top__DOT__u_trail_ram__DOT__mem
           [(0x1ffffU & vlSelf->slime_top__DOT__trail_addr_a)]
            : 0U);
    vlSelf->slime_top__DOT__trail_addr_a = (0x7ffffU 
                                            & (((IData)(0x140U) 
                                                * VL_SHIFTR_III(32,32,32, 
                                                                (0x1ffU 
                                                                 & (IData)(vlSelf->slime_top__DOT__u_vga__DOT__v_count)), 2U)) 
                                               + (0xffU 
                                                  & ((IData)(vlSelf->slime_top__DOT__u_vga__DOT__h_count) 
                                                     >> 2U))));
}

VL_INLINE_OPT void Vslime_top___024root___nba_sequent__TOP__1(Vslime_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root___nba_sequent__TOP__1\n"); );
    // Init
    SData/*9:0*/ __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_to_idx__0__Vfuncout;
    __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_to_idx__0__Vfuncout = 0;
    IData/*24:0*/ __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_to_idx__0__angle;
    __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_to_idx__0__angle = 0;
    IData/*24:0*/ __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_to_idx__0__normalized;
    __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_to_idx__0__normalized = 0;
    IData/*24:0*/ __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_to_idx__0__scaled;
    __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_to_idx__0__scaled = 0;
    SData/*9:0*/ __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__1__Vfuncout;
    __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__1__Vfuncout = 0;
    IData/*24:0*/ __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__1__fp_val;
    __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__1__fp_val = 0;
    IData/*24:0*/ __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__1__pixel;
    __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__1__pixel = 0;
    SData/*8:0*/ __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__2__Vfuncout;
    __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__2__Vfuncout = 0;
    IData/*24:0*/ __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__2__fp_val;
    __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__2__fp_val = 0;
    IData/*24:0*/ __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__2__pixel;
    __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__2__pixel = 0;
    SData/*9:0*/ __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__3__Vfuncout;
    __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__3__Vfuncout = 0;
    IData/*24:0*/ __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__3__fp_val;
    __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__3__fp_val = 0;
    IData/*24:0*/ __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__3__pixel;
    __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__3__pixel = 0;
    SData/*8:0*/ __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__4__Vfuncout;
    __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__4__Vfuncout = 0;
    IData/*24:0*/ __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__4__fp_val;
    __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__4__fp_val = 0;
    IData/*24:0*/ __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__4__pixel;
    __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__4__pixel = 0;
    CData/*3:0*/ __Vtableidx1;
    __Vtableidx1 = 0;
    CData/*5:0*/ __Vtableidx2;
    __Vtableidx2 = 0;
    CData/*1:0*/ __Vdly__slime_top__DOT__clk_div;
    __Vdly__slime_top__DOT__clk_div = 0;
    CData/*3:0*/ __Vdly__slime_top__DOT__speed_level;
    __Vdly__slime_top__DOT__speed_level = 0;
    CData/*3:0*/ __Vdly__slime_top__DOT__sim_state;
    __Vdly__slime_top__DOT__sim_state = 0;
    IData/*16:0*/ __Vdly__slime_top__DOT__agent_idx;
    __Vdly__slime_top__DOT__agent_idx = 0;
    CData/*0:0*/ __Vdly__slime_top__DOT__sim_running;
    __Vdly__slime_top__DOT__sim_running = 0;
    CData/*0:0*/ __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_stable;
    __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_stable = 0;
    IData/*20:0*/ __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__counter;
    __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__counter = 0;
    CData/*0:0*/ __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable;
    __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable = 0;
    IData/*20:0*/ __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__counter;
    __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__counter = 0;
    CData/*0:0*/ __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable;
    __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable = 0;
    IData/*20:0*/ __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__counter;
    __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__counter = 0;
    CData/*0:0*/ __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_stable;
    __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_stable = 0;
    IData/*20:0*/ __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__counter;
    __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__counter = 0;
    CData/*0:0*/ __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_stable;
    __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_stable = 0;
    IData/*20:0*/ __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__counter;
    __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__counter = 0;
    IData/*31:0*/ __Vdly__slime_top__DOT__u_lfsr__DOT__lfsr_reg;
    __Vdly__slime_top__DOT__u_lfsr__DOT__lfsr_reg = 0;
    IData/*16:0*/ __Vdlyvdim0__slime_top__DOT__u_trail_ram__DOT__mem__v0;
    __Vdlyvdim0__slime_top__DOT__u_trail_ram__DOT__mem__v0 = 0;
    IData/*17:0*/ __Vdlyvval__slime_top__DOT__u_trail_ram__DOT__mem__v0;
    __Vdlyvval__slime_top__DOT__u_trail_ram__DOT__mem__v0 = 0;
    CData/*0:0*/ __Vdlyvset__slime_top__DOT__u_trail_ram__DOT__mem__v0;
    __Vdlyvset__slime_top__DOT__u_trail_ram__DOT__mem__v0 = 0;
    IData/*17:0*/ __Vdlyvval__slime_top__DOT__u_trail_ram__DOT__pipe_b__v0;
    __Vdlyvval__slime_top__DOT__u_trail_ram__DOT__pipe_b__v0 = 0;
    IData/*17:0*/ __Vdlyvval__slime_top__DOT__u_trail_ram__DOT__pipe_b__v1;
    __Vdlyvval__slime_top__DOT__u_trail_ram__DOT__pipe_b__v1 = 0;
    CData/*2:0*/ __Vdly__slime_top__DOT__u_coordinator__DOT__state;
    __Vdly__slime_top__DOT__u_coordinator__DOT__state = 0;
    CData/*3:0*/ __Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_x__v0;
    __Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_x__v0 = 0;
    IData/*24:0*/ __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_x__v0;
    __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_x__v0 = 0;
    CData/*0:0*/ __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_x__v0;
    __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_x__v0 = 0;
    CData/*3:0*/ __Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_y__v0;
    __Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_y__v0 = 0;
    IData/*24:0*/ __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_y__v0;
    __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_y__v0 = 0;
    CData/*0:0*/ __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_y__v0;
    __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_y__v0 = 0;
    CData/*3:0*/ __Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_angle__v0;
    __Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_angle__v0 = 0;
    IData/*24:0*/ __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_angle__v0;
    __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_angle__v0 = 0;
    CData/*0:0*/ __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_angle__v0;
    __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_angle__v0 = 0;
    CData/*3:0*/ __Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_x__v1;
    __Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_x__v1 = 0;
    IData/*24:0*/ __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_x__v1;
    __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_x__v1 = 0;
    CData/*0:0*/ __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_x__v1;
    __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_x__v1 = 0;
    CData/*3:0*/ __Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_y__v1;
    __Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_y__v1 = 0;
    IData/*24:0*/ __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_y__v1;
    __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_y__v1 = 0;
    CData/*0:0*/ __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_y__v1;
    __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_y__v1 = 0;
    CData/*3:0*/ __Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_angle__v1;
    __Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_angle__v1 = 0;
    IData/*24:0*/ __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_angle__v1;
    __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_angle__v1 = 0;
    CData/*0:0*/ __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_angle__v1;
    __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_angle__v1 = 0;
    CData/*3:0*/ __Vdly__slime_top__DOT__u_coordinator__DOT__current_agent_idx;
    __Vdly__slime_top__DOT__u_coordinator__DOT__current_agent_idx = 0;
    CData/*0:0*/ __Vdly__slime_top__DOT__u_coordinator__DOT__step_freeze_cycle;
    __Vdly__slime_top__DOT__u_coordinator__DOT__step_freeze_cycle = 0;
    IData/*31:0*/ __Vdly__slime_top__DOT__u_coordinator__DOT__step_counter;
    __Vdly__slime_top__DOT__u_coordinator__DOT__step_counter = 0;
    CData/*3:0*/ __Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_x__v2;
    __Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_x__v2 = 0;
    IData/*24:0*/ __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_x__v2;
    __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_x__v2 = 0;
    CData/*0:0*/ __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_x__v2;
    __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_x__v2 = 0;
    CData/*3:0*/ __Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_y__v2;
    __Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_y__v2 = 0;
    IData/*24:0*/ __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_y__v2;
    __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_y__v2 = 0;
    CData/*0:0*/ __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_y__v2;
    __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_y__v2 = 0;
    CData/*3:0*/ __Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_angle__v2;
    __Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_angle__v2 = 0;
    IData/*24:0*/ __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_angle__v2;
    __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_angle__v2 = 0;
    CData/*0:0*/ __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_angle__v2;
    __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_angle__v2 = 0;
    CData/*3:0*/ __Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_x__v3;
    __Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_x__v3 = 0;
    IData/*24:0*/ __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_x__v3;
    __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_x__v3 = 0;
    CData/*0:0*/ __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_x__v3;
    __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_x__v3 = 0;
    CData/*3:0*/ __Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_y__v3;
    __Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_y__v3 = 0;
    IData/*24:0*/ __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_y__v3;
    __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_y__v3 = 0;
    CData/*0:0*/ __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_y__v3;
    __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_y__v3 = 0;
    CData/*3:0*/ __Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_angle__v3;
    __Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_angle__v3 = 0;
    IData/*24:0*/ __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_angle__v3;
    __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_angle__v3 = 0;
    CData/*0:0*/ __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_angle__v3;
    __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_angle__v3 = 0;
    // Body
    __Vdly__slime_top__DOT__clk_div = vlSelf->slime_top__DOT__clk_div;
    __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__counter 
        = vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__counter;
    __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_stable 
        = vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_stable;
    __Vdlyvset__slime_top__DOT__u_trail_ram__DOT__mem__v0 = 0U;
    __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__counter 
        = vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__counter;
    __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable 
        = vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable;
    __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__counter 
        = vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__counter;
    __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable 
        = vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable;
    __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__counter 
        = vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__counter;
    __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_stable 
        = vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_stable;
    __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__counter 
        = vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__counter;
    __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_stable 
        = vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_stable;
    __Vdly__slime_top__DOT__speed_level = vlSelf->slime_top__DOT__speed_level;
    __Vdly__slime_top__DOT__agent_idx = vlSelf->slime_top__DOT__agent_idx;
    __Vdly__slime_top__DOT__u_lfsr__DOT__lfsr_reg = vlSelf->slime_top__DOT__u_lfsr__DOT__lfsr_reg;
    __Vdly__slime_top__DOT__sim_running = vlSelf->slime_top__DOT__sim_running;
    __Vdly__slime_top__DOT__sim_state = vlSelf->slime_top__DOT__sim_state;
    if (VL_UNLIKELY((0x12U == (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state)))) {
        VL_WRITEF("[COORD] Trail write: addr=%0# (%0#,%0#) data=20480 (from agent[%0#])\n",
                  19,(0x7ffffU & (((IData)(0x140U) 
                                   * (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_write_y)) 
                                  + (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_write_x))),
                  10,(IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_write_x),
                  9,vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_write_y,
                  4,(IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__current_agent_idx));
    }
    if (VL_UNLIKELY(((0x12U == (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state)) 
                     | (IData)(vlSelf->slime_top__DOT__pattern_trail_we)))) {
        VL_WRITEF("[MUX] sim_state=%0# use_orch=%0b orch_we=%0b pattern_we=%0b selected_we=%0b addr=%0# data=%0#\n",
                  4,vlSelf->slime_top__DOT__sim_state,
                  1,(IData)(vlSelf->slime_top__DOT__pattern_trail_we),
                  1,(0x12U == (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state)),
                  1,(IData)(vlSelf->slime_top__DOT__pattern_trail_we),
                  1,vlSelf->slime_top__DOT__trail_we_b,
                  19,vlSelf->slime_top__DOT__trail_addr_b,
                  18,vlSelf->slime_top__DOT__trail_data_b_in);
    }
    if (VL_UNLIKELY(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_start)) {
        VL_WRITEF("[COORD] Starting processor for agent[%0#]: x=%0d y=%0d angle=%0d (busy=%0b)\n",
                  4,vlSelf->slime_top__DOT__u_coordinator__DOT__current_agent_idx,
                  25,((9U >= (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__current_agent_idx))
                       ? vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x
                      [vlSelf->slime_top__DOT__u_coordinator__DOT__current_agent_idx]
                       : 0U),25,((9U >= (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__current_agent_idx))
                                  ? vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y
                                 [vlSelf->slime_top__DOT__u_coordinator__DOT__current_agent_idx]
                                  : 0U),25,((9U >= (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__current_agent_idx))
                                             ? vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle
                                            [vlSelf->slime_top__DOT__u_coordinator__DOT__current_agent_idx]
                                             : 0U),
                  1,(0U != (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state)));
    }
    __Vdly__slime_top__DOT__u_coordinator__DOT__step_counter 
        = vlSelf->slime_top__DOT__u_coordinator__DOT__step_counter;
    __Vdly__slime_top__DOT__u_coordinator__DOT__current_agent_idx 
        = vlSelf->slime_top__DOT__u_coordinator__DOT__current_agent_idx;
    __Vdly__slime_top__DOT__u_coordinator__DOT__step_freeze_cycle 
        = vlSelf->slime_top__DOT__u_coordinator__DOT__step_freeze_cycle;
    __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_angle__v0 = 0U;
    __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_angle__v1 = 0U;
    __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_angle__v2 = 0U;
    __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_angle__v3 = 0U;
    __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_y__v0 = 0U;
    __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_y__v1 = 0U;
    __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_y__v2 = 0U;
    __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_y__v3 = 0U;
    __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_x__v0 = 0U;
    __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_x__v1 = 0U;
    __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_x__v2 = 0U;
    __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_x__v3 = 0U;
    __Vdly__slime_top__DOT__u_coordinator__DOT__state 
        = vlSelf->slime_top__DOT__u_coordinator__DOT__state;
    __Vdly__slime_top__DOT__clk_div = (3U & ((IData)(1U) 
                                             + (IData)(vlSelf->slime_top__DOT__clk_div)));
    if (((IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_sync_1) 
         != (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_stable))) {
        if ((0x1e847fU == vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__counter)) {
            __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_stable 
                = vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_sync_1;
            __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__counter = 0U;
        } else {
            __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__counter 
                = (0x1fffffU & ((IData)(1U) + vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__counter));
        }
    } else {
        __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__counter = 0U;
    }
    if (((IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_sync_1) 
         != (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable))) {
        if ((0x1e847fU == vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__counter)) {
            __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable 
                = vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_sync_1;
            __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__counter = 0U;
        } else {
            __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__counter 
                = (0x1fffffU & ((IData)(1U) + vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__counter));
        }
    } else {
        __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__counter = 0U;
    }
    if (((IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_sync_1) 
         != (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable))) {
        if ((0x1e847fU == vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__counter)) {
            __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable 
                = vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_sync_1;
            __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__counter = 0U;
        } else {
            __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__counter 
                = (0x1fffffU & ((IData)(1U) + vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__counter));
        }
    } else {
        __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__counter = 0U;
    }
    if (((IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_sync_1) 
         != (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_stable))) {
        if ((0x1e847fU == vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__counter)) {
            __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_stable 
                = vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_sync_1;
            __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__counter = 0U;
        } else {
            __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__counter 
                = (0x1fffffU & ((IData)(1U) + vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__counter));
        }
    } else {
        __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__counter = 0U;
    }
    __Vdlyvval__slime_top__DOT__u_trail_ram__DOT__pipe_b__v0 
        = vlSelf->slime_top__DOT__u_trail_ram__DOT__mem_out_b;
    __Vdlyvval__slime_top__DOT__u_trail_ram__DOT__pipe_b__v1 
        = vlSelf->slime_top__DOT__u_trail_ram__DOT__pipe_b
        [0U];
    if (((IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_sync_1) 
         != (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_stable))) {
        if ((0x1e847fU == vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__counter)) {
            __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_stable 
                = vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_sync_1;
            __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__counter = 0U;
        } else {
            __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__counter 
                = (0x1fffffU & ((IData)(1U) + vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__counter));
        }
    } else {
        __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__counter = 0U;
    }
    if ((((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable_prev)) 
          & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable)) 
         & (0xfU > (IData)(vlSelf->slime_top__DOT__speed_level)))) {
        __Vdly__slime_top__DOT__speed_level = (0xfU 
                                               & ((IData)(1U) 
                                                  + (IData)(vlSelf->slime_top__DOT__speed_level)));
    } else if ((((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable_prev)) 
                 & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable)) 
                & (0U < (IData)(vlSelf->slime_top__DOT__speed_level)))) {
        __Vdly__slime_top__DOT__speed_level = (0xfU 
                                               & ((IData)(vlSelf->slime_top__DOT__speed_level) 
                                                  - (IData)(1U)));
    }
    if (vlSelf->slime_top__DOT__lfsr_load) {
        __Vdly__slime_top__DOT__u_lfsr__DOT__lfsr_reg 
            = ((0U == vlSelf->slime_top__DOT__lfsr_seed)
                ? 0xdeadbeefU : vlSelf->slime_top__DOT__lfsr_seed);
    } else if (vlSelf->slime_top__DOT__lfsr_enable) {
        __Vdly__slime_top__DOT__u_lfsr__DOT__lfsr_reg 
            = ((vlSelf->slime_top__DOT__u_lfsr__DOT__lfsr_reg 
                << 1U) | (IData)(vlSelf->slime_top__DOT__u_lfsr__DOT__feedback));
    }
    if ((8U & (IData)(vlSelf->slime_top__DOT__sim_state))) {
        __Vdly__slime_top__DOT__sim_state = 0U;
    } else if ((4U & (IData)(vlSelf->slime_top__DOT__sim_state))) {
        if ((2U & (IData)(vlSelf->slime_top__DOT__sim_state))) {
            __Vdly__slime_top__DOT__sim_state = 0U;
        } else if ((1U & (IData)(vlSelf->slime_top__DOT__sim_state))) {
            __Vdly__slime_top__DOT__sim_state = 0U;
        } else if (vlSelf->slime_top__DOT__frame_start) {
            __Vdly__slime_top__DOT__sim_state = 2U;
        }
    } else if ((2U & (IData)(vlSelf->slime_top__DOT__sim_state))) {
        if ((1U & (IData)(vlSelf->slime_top__DOT__sim_state))) {
            if ((1U & (~ (IData)(vlSelf->sw)))) {
                if ((0x12bffU == vlSelf->slime_top__DOT__agent_idx)) {
                    __Vdly__slime_top__DOT__agent_idx = 0U;
                    __Vdly__slime_top__DOT__sim_state = 4U;
                } else {
                    __Vdly__slime_top__DOT__agent_idx 
                        = (0x1ffffU & ((IData)(1U) 
                                       + vlSelf->slime_top__DOT__agent_idx));
                }
            }
        } else {
            __Vdly__slime_top__DOT__sim_state = 2U;
        }
    } else if ((1U & (IData)(vlSelf->slime_top__DOT__sim_state))) {
        __Vdly__slime_top__DOT__agent_idx = 0U;
        __Vdly__slime_top__DOT__sim_state = 2U;
    } else if (((IData)(vlSelf->slime_top__DOT__btn_start) 
                | (IData)(vlSelf->sim_start))) {
        __Vdly__slime_top__DOT__sim_state = 1U;
        __Vdly__slime_top__DOT__sim_running = 1U;
    }
    if (((IData)(vlSelf->slime_top__DOT__btn_start) 
         & (IData)(vlSelf->slime_top__DOT__sim_running))) {
        __Vdly__slime_top__DOT__sim_state = 0U;
        __Vdly__slime_top__DOT__sim_running = 0U;
    }
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_stable_prev 
        = vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_stable;
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_stable_prev 
        = vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_stable;
    vlSelf->slime_top__DOT__u_lfsr__DOT__valid = ((1U 
                                                   & (~ (IData)(vlSelf->slime_top__DOT__lfsr_load))) 
                                                  && (IData)(vlSelf->slime_top__DOT__lfsr_enable));
    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__cos_val 
        = vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__u_trig_lut__DOT__cos_rom
        [vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__trig_angle_idx];
    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__sin_val 
        = vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__u_trig_lut__DOT__sin_rom
        [vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__trig_angle_idx];
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_stable_prev 
        = vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_stable;
    if (vlSelf->slime_top__DOT__trail_we_b) {
        vlSelf->slime_top__DOT__u_trail_ram__DOT____Vlvbound_h51f3e5a2__0 
            = vlSelf->slime_top__DOT__trail_data_b_in;
        if ((0x12bffU >= (0x1ffffU & vlSelf->slime_top__DOT__trail_addr_b))) {
            __Vdlyvval__slime_top__DOT__u_trail_ram__DOT__mem__v0 
                = vlSelf->slime_top__DOT__u_trail_ram__DOT____Vlvbound_h51f3e5a2__0;
            __Vdlyvset__slime_top__DOT__u_trail_ram__DOT__mem__v0 = 1U;
            __Vdlyvdim0__slime_top__DOT__u_trail_ram__DOT__mem__v0 
                = (0x1ffffU & vlSelf->slime_top__DOT__trail_addr_b);
        }
    }
    if (VL_UNLIKELY(((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__state) 
                     != (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__next_state)))) {
        VL_WRITEF("[COORD] State transition (cycle=%0#): %0# -> %0#\n",
                  64,VL_DIV_QQQ(64, (QData)(VL_TIME_UNITED_Q(1)), 0xaULL),
                  3,(IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__state),
                  3,vlSelf->slime_top__DOT__u_coordinator__DOT__next_state);
    }
    __Vdly__slime_top__DOT__u_coordinator__DOT__state 
        = vlSelf->slime_top__DOT__u_coordinator__DOT__next_state;
    if ((4U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__state))) {
        __Vdly__slime_top__DOT__u_coordinator__DOT__state = 0U;
    } else if ((2U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__state))) {
        if ((1U & (~ (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__state)))) {
            if (vlSelf->debug_agent_write_en) {
                if ((0U == (IData)(vlSelf->debug_agent_sel))) {
                    vlSelf->slime_top__DOT__u_coordinator__DOT____Vlvbound_h1f94e32a__2 
                        = vlSelf->debug_agent_data_write;
                    if ((9U >= (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__debug_idx_safe))) {
                        __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_x__v0 
                            = vlSelf->slime_top__DOT__u_coordinator__DOT____Vlvbound_h1f94e32a__2;
                        __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_x__v0 = 1U;
                        __Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_x__v0 
                            = vlSelf->slime_top__DOT__u_coordinator__DOT__debug_idx_safe;
                    }
                } else if ((1U == (IData)(vlSelf->debug_agent_sel))) {
                    vlSelf->slime_top__DOT__u_coordinator__DOT____Vlvbound_hcb92b3ef__2 
                        = vlSelf->debug_agent_data_write;
                    if ((9U >= (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__debug_idx_safe))) {
                        __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_y__v0 
                            = vlSelf->slime_top__DOT__u_coordinator__DOT____Vlvbound_hcb92b3ef__2;
                        __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_y__v0 = 1U;
                        __Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_y__v0 
                            = vlSelf->slime_top__DOT__u_coordinator__DOT__debug_idx_safe;
                    }
                } else if ((2U == (IData)(vlSelf->debug_agent_sel))) {
                    vlSelf->slime_top__DOT__u_coordinator__DOT____Vlvbound_hd63147c5__2 
                        = vlSelf->debug_agent_data_write;
                    if ((9U >= (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__debug_idx_safe))) {
                        __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_angle__v0 
                            = vlSelf->slime_top__DOT__u_coordinator__DOT____Vlvbound_hd63147c5__2;
                        __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_angle__v0 = 1U;
                        __Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_angle__v0 
                            = vlSelf->slime_top__DOT__u_coordinator__DOT__debug_idx_safe;
                    }
                }
            } else if (VL_UNLIKELY(vlSelf->slime_top__DOT__u_coordinator__DOT__latched_valid)) {
                vlSelf->slime_top__DOT__u_coordinator__DOT__prev_idx 
                    = ((0U == (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__current_agent_idx))
                        ? 9U : (0xfU & ((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__current_agent_idx) 
                                        - (IData)(1U))));
                VL_WRITEF("[COORD] Writing back agent[%0#]: x=%0d y=%0d angle=%0d\n",
                          4,vlSelf->slime_top__DOT__u_coordinator__DOT__prev_idx,
                          25,vlSelf->slime_top__DOT__u_coordinator__DOT__latched_x_out,
                          25,vlSelf->slime_top__DOT__u_coordinator__DOT__latched_y_out,
                          25,vlSelf->slime_top__DOT__u_coordinator__DOT__latched_angle_out);
                vlSelf->slime_top__DOT__u_coordinator__DOT__latched_valid = 0U;
                vlSelf->slime_top__DOT__u_coordinator__DOT____Vlvbound_h2b5da6a3__0 
                    = vlSelf->slime_top__DOT__u_coordinator__DOT__latched_x_out;
                vlSelf->slime_top__DOT__u_coordinator__DOT____Vlvbound_haf1b776c__0 
                    = vlSelf->slime_top__DOT__u_coordinator__DOT__latched_y_out;
                vlSelf->slime_top__DOT__u_coordinator__DOT____Vlvbound_hd9a9fc40__0 
                    = vlSelf->slime_top__DOT__u_coordinator__DOT__latched_angle_out;
                if ((9U >= (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__prev_idx))) {
                    __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_x__v1 
                        = vlSelf->slime_top__DOT__u_coordinator__DOT____Vlvbound_h2b5da6a3__0;
                    __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_x__v1 = 1U;
                    __Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_x__v1 
                        = vlSelf->slime_top__DOT__u_coordinator__DOT__prev_idx;
                    __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_y__v1 
                        = vlSelf->slime_top__DOT__u_coordinator__DOT____Vlvbound_haf1b776c__0;
                    __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_y__v1 = 1U;
                    __Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_y__v1 
                        = vlSelf->slime_top__DOT__u_coordinator__DOT__prev_idx;
                    __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_angle__v1 
                        = vlSelf->slime_top__DOT__u_coordinator__DOT____Vlvbound_hd9a9fc40__0;
                    __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_angle__v1 = 1U;
                    __Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_angle__v1 
                        = vlSelf->slime_top__DOT__u_coordinator__DOT__prev_idx;
                }
                if (VL_UNLIKELY(vlSelf->slime_top__DOT__u_coordinator__DOT__step_freeze_cycle)) {
                    VL_WRITEF("[COORD] Last agent write-back complete, firing step_complete_pulse\n");
                    vlSelf->slime_top__DOT__u_coordinator__DOT__step_writeback_cycle = 1U;
                }
            } else {
                vlSelf->slime_top__DOT__u_coordinator__DOT__step_writeback_cycle = 0U;
            }
            if (VL_UNLIKELY(((~ (IData)(vlSelf->sw)) 
                             & (0x13U == (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))))) {
                VL_WRITEF("[COORD] Processor done for agent[%0#], latching outputs x=%0d y=%0d angle=%0d\n",
                          4,vlSelf->slime_top__DOT__u_coordinator__DOT__current_agent_idx,
                          25,vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__new_x,
                          25,vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__new_y,
                          25,vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__new_angle);
                vlSelf->slime_top__DOT__u_coordinator__DOT__latched_x_out 
                    = vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__new_x;
                vlSelf->slime_top__DOT__u_coordinator__DOT__latched_y_out 
                    = vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__new_y;
                vlSelf->slime_top__DOT__u_coordinator__DOT__latched_angle_out 
                    = vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__new_angle;
                vlSelf->slime_top__DOT__u_coordinator__DOT__latched_valid = 1U;
                if ((9U > (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__current_agent_idx))) {
                    __Vdly__slime_top__DOT__u_coordinator__DOT__current_agent_idx 
                        = (0xfU & ((IData)(1U) + (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__current_agent_idx)));
                    VL_WRITEF("[COORD] Advancing to agent[%0#]\n",
                              32,((IData)(1U) + (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__current_agent_idx)));
                    vlSelf->slime_top__DOT__u_coordinator__DOT__step_just_completed = 0U;
                    __Vdly__slime_top__DOT__u_coordinator__DOT__step_freeze_cycle = 0U;
                } else {
                    __Vdly__slime_top__DOT__u_coordinator__DOT__step_counter 
                        = ((IData)(1U) + vlSelf->slime_top__DOT__u_coordinator__DOT__step_counter);
                    VL_WRITEF("[COORD] Completed step %0#, resetting to agent[0] (freeze 1 cycle)\n",
                              32,vlSelf->slime_top__DOT__u_coordinator__DOT__step_counter);
                    __Vdly__slime_top__DOT__u_coordinator__DOT__current_agent_idx = 0U;
                    vlSelf->slime_top__DOT__u_coordinator__DOT__step_just_completed = 1U;
                    __Vdly__slime_top__DOT__u_coordinator__DOT__step_freeze_cycle = 1U;
                }
            } else {
                if (vlSelf->slime_top__DOT__u_coordinator__DOT__step_freeze_cycle) {
                    __Vdly__slime_top__DOT__u_coordinator__DOT__step_freeze_cycle = 0U;
                }
                vlSelf->slime_top__DOT__u_coordinator__DOT__step_just_completed = 0U;
            }
        }
    } else if ((1U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__state))) {
        if (VL_UNLIKELY((2U == (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__next_state)))) {
            VL_WRITEF("[COORD] Entering RUNNING state (will process agents)\n");
        }
        if (vlSelf->debug_agent_write_en) {
            if ((0U == (IData)(vlSelf->debug_agent_sel))) {
                vlSelf->slime_top__DOT__u_coordinator__DOT____Vlvbound_h1f94e32a__1 
                    = vlSelf->debug_agent_data_write;
                if ((9U >= (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__debug_idx_safe))) {
                    __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_x__v2 
                        = vlSelf->slime_top__DOT__u_coordinator__DOT____Vlvbound_h1f94e32a__1;
                    __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_x__v2 = 1U;
                    __Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_x__v2 
                        = vlSelf->slime_top__DOT__u_coordinator__DOT__debug_idx_safe;
                }
            } else if ((1U == (IData)(vlSelf->debug_agent_sel))) {
                vlSelf->slime_top__DOT__u_coordinator__DOT____Vlvbound_hcb92b3ef__1 
                    = vlSelf->debug_agent_data_write;
                if ((9U >= (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__debug_idx_safe))) {
                    __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_y__v2 
                        = vlSelf->slime_top__DOT__u_coordinator__DOT____Vlvbound_hcb92b3ef__1;
                    __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_y__v2 = 1U;
                    __Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_y__v2 
                        = vlSelf->slime_top__DOT__u_coordinator__DOT__debug_idx_safe;
                }
            } else if ((2U == (IData)(vlSelf->debug_agent_sel))) {
                vlSelf->slime_top__DOT__u_coordinator__DOT____Vlvbound_hd63147c5__1 
                    = vlSelf->debug_agent_data_write;
                if ((9U >= (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__debug_idx_safe))) {
                    __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_angle__v2 
                        = vlSelf->slime_top__DOT__u_coordinator__DOT____Vlvbound_hd63147c5__1;
                    __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_angle__v2 = 1U;
                    __Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_angle__v2 
                        = vlSelf->slime_top__DOT__u_coordinator__DOT__debug_idx_safe;
                }
            }
        }
        __Vdly__slime_top__DOT__u_coordinator__DOT__current_agent_idx = 0U;
        __Vdly__slime_top__DOT__u_coordinator__DOT__step_counter = 0U;
    } else {
        if (VL_UNLIKELY((1U == (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__next_state)))) {
            VL_WRITEF("[COORD] Entering INITIALIZE state\n");
        }
        if (vlSelf->debug_agent_write_en) {
            if ((0U == (IData)(vlSelf->debug_agent_sel))) {
                vlSelf->slime_top__DOT__u_coordinator__DOT____Vlvbound_h1f94e32a__0 
                    = vlSelf->debug_agent_data_write;
                if ((9U >= (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__debug_idx_safe))) {
                    __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_x__v3 
                        = vlSelf->slime_top__DOT__u_coordinator__DOT____Vlvbound_h1f94e32a__0;
                    __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_x__v3 = 1U;
                    __Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_x__v3 
                        = vlSelf->slime_top__DOT__u_coordinator__DOT__debug_idx_safe;
                }
            } else if ((1U == (IData)(vlSelf->debug_agent_sel))) {
                vlSelf->slime_top__DOT__u_coordinator__DOT____Vlvbound_hcb92b3ef__0 
                    = vlSelf->debug_agent_data_write;
                if ((9U >= (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__debug_idx_safe))) {
                    __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_y__v3 
                        = vlSelf->slime_top__DOT__u_coordinator__DOT____Vlvbound_hcb92b3ef__0;
                    __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_y__v3 = 1U;
                    __Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_y__v3 
                        = vlSelf->slime_top__DOT__u_coordinator__DOT__debug_idx_safe;
                }
            } else if ((2U == (IData)(vlSelf->debug_agent_sel))) {
                vlSelf->slime_top__DOT__u_coordinator__DOT____Vlvbound_hd63147c5__0 
                    = vlSelf->debug_agent_data_write;
                if ((9U >= (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__debug_idx_safe))) {
                    __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_angle__v3 
                        = vlSelf->slime_top__DOT__u_coordinator__DOT____Vlvbound_hd63147c5__0;
                    __Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_angle__v3 = 1U;
                    __Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_angle__v3 
                        = vlSelf->slime_top__DOT__u_coordinator__DOT__debug_idx_safe;
                }
            }
        }
        __Vdly__slime_top__DOT__u_coordinator__DOT__current_agent_idx = 0U;
        __Vdly__slime_top__DOT__u_coordinator__DOT__step_counter = 0U;
    }
    vlSelf->slime_top__DOT__u_trail_ram__DOT__mem_out_b 
        = ((IData)(vlSelf->slime_top__DOT__trail_we_b)
            ? vlSelf->slime_top__DOT__trail_data_b_in
            : ((0x12bffU >= (0x1ffffU & vlSelf->slime_top__DOT__trail_addr_b))
                ? vlSelf->slime_top__DOT__u_trail_ram__DOT__mem
               [(0x1ffffU & vlSelf->slime_top__DOT__trail_addr_b)]
                : 0U));
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__counter 
        = __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__counter;
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__counter 
        = __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__counter;
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__counter 
        = __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__counter;
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__counter 
        = __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__counter;
    vlSelf->slime_top__DOT__u_trail_ram__DOT__pipe_b[0U] 
        = __Vdlyvval__slime_top__DOT__u_trail_ram__DOT__pipe_b__v0;
    vlSelf->slime_top__DOT__u_trail_ram__DOT__pipe_b[1U] 
        = __Vdlyvval__slime_top__DOT__u_trail_ram__DOT__pipe_b__v1;
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__counter 
        = __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__counter;
    vlSelf->slime_top__DOT__speed_level = __Vdly__slime_top__DOT__speed_level;
    vlSelf->slime_top__DOT__agent_idx = __Vdly__slime_top__DOT__agent_idx;
    vlSelf->slime_top__DOT__sim_running = __Vdly__slime_top__DOT__sim_running;
    vlSelf->slime_top__DOT__sim_state = __Vdly__slime_top__DOT__sim_state;
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_stable 
        = __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_stable;
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_stable 
        = __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_stable;
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_stable 
        = __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_stable;
    vlSelf->slime_top__DOT__u_coordinator__DOT__step_counter 
        = __Vdly__slime_top__DOT__u_coordinator__DOT__step_counter;
    vlSelf->slime_top__DOT__u_coordinator__DOT__step_freeze_cycle 
        = __Vdly__slime_top__DOT__u_coordinator__DOT__step_freeze_cycle;
    vlSelf->slime_top__DOT__u_coordinator__DOT__state 
        = __Vdly__slime_top__DOT__u_coordinator__DOT__state;
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_sync_1 
        = vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_sync_0;
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_sync_1 
        = vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_sync_0;
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_sync_1 
        = vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_sync_0;
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_sync_1 
        = vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_sync_0;
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_sync_1 
        = vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_sync_0;
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable_prev 
        = vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable;
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable_prev 
        = vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable;
    if (vlSelf->slime_top__DOT__btn_random) {
        vlSelf->slime_top__DOT__lfsr_seed = (vlSelf->slime_top__DOT__u_lfsr__DOT__lfsr_reg 
                                             ^ ((IData)(vlSelf->slime_top__DOT__clk_div) 
                                                << 0xeU));
    }
    vlSelf->slime_top__DOT__pattern_trail_we = ((~ (IData)(vlSelf->sw)) 
                                                & (2U 
                                                   == (IData)(vlSelf->slime_top__DOT__sim_state)));
    vlSelf->slime_top__DOT__lfsr_load = vlSelf->slime_top__DOT__btn_random;
    vlSelf->slime_top__DOT__btn_start = ((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_stable_prev)) 
                                         & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_stable));
    vlSelf->step_complete_pulse = vlSelf->slime_top__DOT__u_coordinator__DOT__step_writeback_cycle;
    if ((1U & (~ ((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state) 
                  >> 4U)))) {
        if ((8U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
            if ((4U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
                if ((1U & (~ ((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state) 
                              >> 1U)))) {
                    if ((1U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
                        vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__new_angle 
                            = (0x1ffffffU & ((((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__trail_forward) 
                                               > (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__trail_left)) 
                                              & ((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__trail_forward) 
                                                 > (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__trail_right)))
                                              ? vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_reg
                                              : ((((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__trail_forward) 
                                                   < (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__trail_left)) 
                                                  & ((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__trail_forward) 
                                                     < (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__trail_right)))
                                                  ? 
                                                 ((1U 
                                                   & vlSelf->slime_top__DOT__u_lfsr__DOT__lfsr_reg)
                                                   ? 
                                                  ((IData)(0x4ccU) 
                                                   + vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_reg)
                                                   : 
                                                  (vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_reg 
                                                   - (IData)(0x4ccU)))
                                                  : 
                                                 (((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__trail_left) 
                                                   < (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__trail_right))
                                                   ? 
                                                  (vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_reg 
                                                   - (IData)(0x4ccU))
                                                   : 
                                                  (((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__trail_right) 
                                                    < (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__trail_left))
                                                    ? 
                                                   ((IData)(0x4ccU) 
                                                    + vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_reg)
                                                    : vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_reg)))));
                    }
                }
            }
        }
    }
    if ((0x10U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
        if ((1U & (~ ((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state) 
                      >> 3U)))) {
            if ((1U & (~ ((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state) 
                          >> 2U)))) {
                if ((1U & (~ ((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state) 
                              >> 1U)))) {
                    if ((1U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
                        vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__unnamedblk1__DOT__sum_x 
                            = (0x1ffffffU & (vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__x_reg 
                                             + vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__dx));
                        vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__unnamedblk1__DOT__wrapped_x 
                            = (0x1ffffffU & VL_MODDIVS_III(25, 
                                                           (0x1ffffffU 
                                                            & ((IData)(0x140000U) 
                                                               + 
                                                               VL_MODDIVS_III(25, vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__unnamedblk1__DOT__sum_x, (IData)(0x140000U)))), (IData)(0x140000U)));
                        vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__new_x 
                            = vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__unnamedblk1__DOT__wrapped_x;
                    }
                }
            }
        }
    } else if ((8U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
        if ((1U & (~ ((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state) 
                      >> 2U)))) {
            if ((1U & (~ ((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state) 
                          >> 1U)))) {
                if ((1U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
                    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__sensor_x 
                        = (0x1ffffffU & (vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__x_reg 
                                         + (IData)(
                                                   (vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__u_mult__DOT__full_product 
                                                    >> 0xcU))));
                }
            }
        }
    } else if ((4U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
        if ((1U & (~ ((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state) 
                      >> 1U)))) {
            if ((1U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
                vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__sensor_x 
                    = (0x1ffffffU & (vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__x_reg 
                                     + (IData)((vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__u_mult__DOT__full_product 
                                                >> 0xcU))));
            }
        }
    } else if ((1U & (~ ((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state) 
                         >> 1U)))) {
        if ((1U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
            vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__sensor_x 
                = (0x1ffffffU & (vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__x_reg 
                                 + (IData)((vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__u_mult__DOT__full_product 
                                            >> 0xcU))));
        }
    }
    if ((1U & (~ ((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state) 
                  >> 4U)))) {
        if ((8U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
            if ((4U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
                if ((2U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
                    if ((1U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
                        vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__dx 
                            = (0x1ffffffU & (IData)(
                                                    (vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__u_mult__DOT__full_product 
                                                     >> 0xcU)));
                    }
                }
            }
        }
        if ((1U & (~ ((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state) 
                      >> 3U)))) {
            if ((1U & (~ ((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state) 
                          >> 2U)))) {
                if ((1U & (~ ((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state) 
                              >> 1U)))) {
                    if ((1U & (~ (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state)))) {
                        if (vlSelf->slime_top__DOT__u_coordinator__DOT__proc_start) {
                            vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__x_reg 
                                = ((9U >= (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__current_agent_idx))
                                    ? vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x
                                   [vlSelf->slime_top__DOT__u_coordinator__DOT__current_agent_idx]
                                    : 0U);
                        }
                    }
                }
            }
        }
    }
    if ((0x10U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
        if ((1U & (~ ((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state) 
                      >> 3U)))) {
            if ((1U & (~ ((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state) 
                          >> 2U)))) {
                if ((1U & (~ ((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state) 
                              >> 1U)))) {
                    if ((1U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
                        vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__unnamedblk1__DOT__sum_y 
                            = (0x1ffffffU & (vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__y_reg 
                                             + vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__dy));
                        vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__unnamedblk1__DOT__wrapped_y 
                            = (0x1ffffffU & VL_MODDIVS_III(25, 
                                                           (0x1ffffffU 
                                                            & ((IData)(0xf0000U) 
                                                               + 
                                                               VL_MODDIVS_III(25, vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__unnamedblk1__DOT__sum_y, (IData)(0xf0000U)))), (IData)(0xf0000U)));
                        vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__new_y 
                            = vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__unnamedblk1__DOT__wrapped_y;
                    }
                }
            }
        }
    } else if ((8U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
        if ((1U & (~ ((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state) 
                      >> 2U)))) {
            if ((2U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
                if ((1U & (~ (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state)))) {
                    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__sensor_y 
                        = (0x1ffffffU & (vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__y_reg 
                                         + (IData)(
                                                   (vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__u_mult__DOT__full_product 
                                                    >> 0xcU))));
                }
            }
        }
    } else if ((4U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
        if ((2U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
            if ((1U & (~ (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state)))) {
                vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__sensor_y 
                    = (0x1ffffffU & (vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__y_reg 
                                     + (IData)((vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__u_mult__DOT__full_product 
                                                >> 0xcU))));
            }
        }
    } else if ((2U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
        if ((1U & (~ (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state)))) {
            vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__sensor_y 
                = (0x1ffffffU & (vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__y_reg 
                                 + (IData)((vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__u_mult__DOT__full_product 
                                            >> 0xcU))));
        }
    }
    if ((1U & (~ ((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state) 
                  >> 4U)))) {
        if ((1U & (~ ((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state) 
                      >> 3U)))) {
            if ((1U & (~ ((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state) 
                          >> 2U)))) {
                if ((1U & (~ ((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state) 
                              >> 1U)))) {
                    if ((1U & (~ (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state)))) {
                        if (vlSelf->slime_top__DOT__u_coordinator__DOT__proc_start) {
                            if ((9U >= (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__current_agent_idx))) {
                                vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__y_reg 
                                    = vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y
                                    [vlSelf->slime_top__DOT__u_coordinator__DOT__current_agent_idx];
                                vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_reg 
                                    = vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle
                                    [vlSelf->slime_top__DOT__u_coordinator__DOT__current_agent_idx];
                            } else {
                                vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__y_reg = 0U;
                                vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_reg = 0U;
                            }
                        }
                    }
                }
            }
            if ((4U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
                if ((1U & (~ ((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state) 
                              >> 1U)))) {
                    if ((1U & (~ (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state)))) {
                        vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__trail_forward 
                            = (0xffU & vlSelf->slime_top__DOT__orch_trail_read_data);
                    }
                }
            }
        }
        if ((8U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
            if ((1U & (~ ((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state) 
                          >> 2U)))) {
                if ((1U & (~ ((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state) 
                              >> 1U)))) {
                    if ((1U & (~ (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state)))) {
                        vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__trail_left 
                            = (0xffU & vlSelf->slime_top__DOT__orch_trail_read_data);
                    }
                }
            }
            if ((4U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
                if ((1U & (~ ((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state) 
                              >> 1U)))) {
                    if ((1U & (~ (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state)))) {
                        vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__trail_right 
                            = (0xffU & vlSelf->slime_top__DOT__orch_trail_read_data);
                    }
                }
            }
        }
    }
    if (__Vdlyvset__slime_top__DOT__u_trail_ram__DOT__mem__v0) {
        vlSelf->slime_top__DOT__u_trail_ram__DOT__mem[__Vdlyvdim0__slime_top__DOT__u_trail_ram__DOT__mem__v0] 
            = __Vdlyvval__slime_top__DOT__u_trail_ram__DOT__mem__v0;
    }
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable 
        = __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable;
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable 
        = __Vdly__slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable;
    vlSelf->slime_top__DOT__clk_div = __Vdly__slime_top__DOT__clk_div;
    vlSelf->slime_top__DOT__btn_random = ((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_stable_prev)) 
                                          & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_stable));
    __Vtableidx1 = ((((IData)(vlSelf->sim_start) | (IData)(vlSelf->slime_top__DOT__btn_start)) 
                     << 3U) | (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__state));
    vlSelf->slime_top__DOT__u_coordinator__DOT__next_state 
        = Vslime_top__ConstPool__TABLE_hd2b3370f_0[__Vtableidx1];
    vlSelf->slime_top__DOT__u_lfsr__DOT__lfsr_reg = __Vdly__slime_top__DOT__u_lfsr__DOT__lfsr_reg;
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_sync_0 
        = vlSelf->btnr;
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_sync_0 
        = vlSelf->btnd;
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_sync_0 
        = vlSelf->btnu;
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_sync_0 
        = vlSelf->btnl;
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_sync_0 
        = vlSelf->btnc;
    vlSelf->slime_top__DOT__clk_25mhz = (1U & ((IData)(vlSelf->slime_top__DOT__clk_div) 
                                               >> 1U));
    __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__3__fp_val 
        = vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__new_x;
    __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__3__pixel 
        = (0x1ffffffU & (VL_LTES_III(32, 0U, VL_EXTENDS_II(32,25, __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__3__fp_val))
                          ? VL_SHIFTR_III(25,25,32, __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__3__fp_val, 0xcU)
                          : ((- VL_SHIFTR_III(32,32,32, 
                                              ((- VL_EXTENDS_II(32,25, __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__3__fp_val)) 
                                               - (IData)(1U)), 0xcU)) 
                             - (IData)(1U))));
    if (VL_GTS_III(32, 0U, VL_EXTENDS_II(32,25, __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__3__pixel))) {
        __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__3__pixel 
            = (0x1ffffffU & ((IData)(0x140U) + VL_EXTENDS_II(25,25, __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__3__pixel)));
    }
    if (VL_LTES_III(32, 0x140U, VL_EXTENDS_II(32,25, __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__3__pixel))) {
        __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__3__pixel 
            = (0x1ffffffU & (VL_EXTENDS_II(25,25, __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__3__pixel) 
                             - (IData)(0x140U)));
    }
    __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__3__Vfuncout 
        = (0x3ffU & __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__3__pixel);
    vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_write_x 
        = __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__3__Vfuncout;
    __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__1__fp_val 
        = vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__sensor_x;
    __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__1__pixel 
        = (0x1ffffffU & (VL_LTES_III(32, 0U, VL_EXTENDS_II(32,25, __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__1__fp_val))
                          ? VL_SHIFTR_III(25,25,32, __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__1__fp_val, 0xcU)
                          : ((- VL_SHIFTR_III(32,32,32, 
                                              ((- VL_EXTENDS_II(32,25, __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__1__fp_val)) 
                                               - (IData)(1U)), 0xcU)) 
                             - (IData)(1U))));
    if (VL_GTS_III(32, 0U, VL_EXTENDS_II(32,25, __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__1__pixel))) {
        __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__1__pixel 
            = (0x1ffffffU & ((IData)(0x140U) + VL_EXTENDS_II(25,25, __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__1__pixel)));
    }
    if (VL_LTES_III(32, 0x140U, VL_EXTENDS_II(32,25, __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__1__pixel))) {
        __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__1__pixel 
            = (0x1ffffffU & (VL_EXTENDS_II(25,25, __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__1__pixel) 
                             - (IData)(0x140U)));
    }
    __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__1__Vfuncout 
        = (0x3ffU & __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__1__pixel);
    vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_read_x 
        = __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_x__1__Vfuncout;
    __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__4__fp_val 
        = vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__new_y;
    __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__4__pixel 
        = (0x1ffffffU & (VL_LTES_III(32, 0U, VL_EXTENDS_II(32,25, __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__4__fp_val))
                          ? VL_SHIFTR_III(25,25,32, __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__4__fp_val, 0xcU)
                          : ((- VL_SHIFTR_III(32,32,32, 
                                              ((- VL_EXTENDS_II(32,25, __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__4__fp_val)) 
                                               - (IData)(1U)), 0xcU)) 
                             - (IData)(1U))));
    if (VL_GTS_III(32, 0U, VL_EXTENDS_II(32,25, __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__4__pixel))) {
        __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__4__pixel 
            = (0x1ffffffU & ((IData)(0xf0U) + VL_EXTENDS_II(25,25, __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__4__pixel)));
    }
    if (VL_LTES_III(32, 0xf0U, VL_EXTENDS_II(32,25, __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__4__pixel))) {
        __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__4__pixel 
            = (0x1ffffffU & (VL_EXTENDS_II(25,25, __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__4__pixel) 
                             - (IData)(0xf0U)));
    }
    __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__4__Vfuncout 
        = (0x1ffU & __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__4__pixel);
    vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_write_y 
        = __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__4__Vfuncout;
    __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__2__fp_val 
        = vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__sensor_y;
    __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__2__pixel 
        = (0x1ffffffU & (VL_LTES_III(32, 0U, VL_EXTENDS_II(32,25, __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__2__fp_val))
                          ? VL_SHIFTR_III(25,25,32, __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__2__fp_val, 0xcU)
                          : ((- VL_SHIFTR_III(32,32,32, 
                                              ((- VL_EXTENDS_II(32,25, __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__2__fp_val)) 
                                               - (IData)(1U)), 0xcU)) 
                             - (IData)(1U))));
    if (VL_GTS_III(32, 0U, VL_EXTENDS_II(32,25, __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__2__pixel))) {
        __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__2__pixel 
            = (0x1ffffffU & ((IData)(0xf0U) + VL_EXTENDS_II(25,25, __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__2__pixel)));
    }
    if (VL_LTES_III(32, 0xf0U, VL_EXTENDS_II(32,25, __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__2__pixel))) {
        __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__2__pixel 
            = (0x1ffffffU & (VL_EXTENDS_II(25,25, __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__2__pixel) 
                             - (IData)(0xf0U)));
    }
    __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__2__Vfuncout 
        = (0x1ffU & __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__2__pixel);
    vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_read_y 
        = __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__fp_to_pixel_y__2__Vfuncout;
    vlSelf->slime_top__DOT__u_lfsr__DOT__feedback = 
        (1U & VL_REDXOR_32((0xc0000401U & vlSelf->slime_top__DOT__u_lfsr__DOT__lfsr_reg)));
    vlSelf->led = ((0xff00U & (vlSelf->slime_top__DOT__u_lfsr__DOT__lfsr_reg 
                               << 8U)) | ((0xc0U & 
                                           ((IData)(vlSelf->slime_top__DOT__sim_state) 
                                            << 6U)) 
                                          | ((0x20U 
                                              & ((IData)(vlSelf->sw) 
                                                 << 5U)) 
                                             | (((IData)(vlSelf->slime_top__DOT__sim_running) 
                                                 << 4U) 
                                                | (IData)(vlSelf->slime_top__DOT__speed_level)))));
    if (__Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_x__v0) {
        vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x[__Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_x__v0] 
            = __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_x__v0;
    }
    if (__Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_x__v1) {
        vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x[__Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_x__v1] 
            = __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_x__v1;
    }
    if (__Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_x__v2) {
        vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x[__Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_x__v2] 
            = __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_x__v2;
    }
    if (__Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_x__v3) {
        vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x[__Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_x__v3] 
            = __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_x__v3;
    }
    if (__Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_y__v0) {
        vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y[__Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_y__v0] 
            = __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_y__v0;
    }
    if (__Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_y__v1) {
        vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y[__Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_y__v1] 
            = __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_y__v1;
    }
    if (__Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_y__v2) {
        vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y[__Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_y__v2] 
            = __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_y__v2;
    }
    if (__Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_y__v3) {
        vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y[__Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_y__v3] 
            = __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_y__v3;
    }
    vlSelf->slime_top__DOT__u_coordinator__DOT__current_agent_idx 
        = __Vdly__slime_top__DOT__u_coordinator__DOT__current_agent_idx;
    if (__Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_angle__v0) {
        vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle[__Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_angle__v0] 
            = __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_angle__v0;
    }
    if (__Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_angle__v1) {
        vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle[__Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_angle__v1] 
            = __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_angle__v1;
    }
    if (__Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_angle__v2) {
        vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle[__Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_angle__v2] 
            = __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_angle__v2;
    }
    if (__Vdlyvset__slime_top__DOT__u_coordinator__DOT__agent_angle__v3) {
        vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle[__Vdlyvdim0__slime_top__DOT__u_coordinator__DOT__agent_angle__v3] 
            = __Vdlyvval__slime_top__DOT__u_coordinator__DOT__agent_angle__v3;
    }
    if ((0x10U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
        if ((1U & (~ ((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state) 
                      >> 3U)))) {
            if ((1U & (~ ((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state) 
                          >> 2U)))) {
                if ((1U & (~ ((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state) 
                              >> 1U)))) {
                    if ((1U & (~ (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state)))) {
                        vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__dy 
                            = (0x1ffffffU & (IData)(
                                                    (vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__u_mult__DOT__full_product 
                                                     >> 0xcU)));
                    }
                }
            }
        }
    }
    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state 
        = vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__next_state;
    if ((0x10U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
        if ((8U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
            vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_b = 0U;
            vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_a = 0U;
            vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__current_sense_angle 
                = (0x1ffffffU & vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_reg);
        } else if ((4U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
            vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_b = 0U;
            vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_a = 0U;
            vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__current_sense_angle 
                = (0x1ffffffU & vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_reg);
        } else if ((2U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
            vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_b = 0U;
            vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_a = 0U;
            vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__current_sense_angle 
                = (0x1ffffffU & vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_reg);
        } else if ((1U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
            vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_b = 0U;
            vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_a = 0U;
            vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__current_sense_angle 
                = (0x1ffffffU & vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_reg);
        } else {
            vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_b = 0x1000U;
            vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_a 
                = vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__sin_val;
            vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__current_sense_angle 
                = (0x1ffffffU & vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__new_angle);
        }
    } else if ((8U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
        if ((4U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
            if ((2U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
                if ((1U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
                    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_b = 0x1000U;
                    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_a 
                        = vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__cos_val;
                    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__current_sense_angle 
                        = (0x1ffffffU & vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__new_angle);
                } else {
                    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_b = 0U;
                    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_a = 0U;
                    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__current_sense_angle 
                        = (0x1ffffffU & vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_reg);
                }
            } else {
                vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_b = 0U;
                vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_a = 0U;
                vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__current_sense_angle 
                    = (0x1ffffffU & vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_reg);
            }
        } else if ((2U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
            if ((1U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
                vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_b = 0U;
                vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_a = 0U;
                vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__current_sense_angle 
                    = (0x1ffffffU & vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_reg);
            } else {
                vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_b = 0x9000U;
                vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_a 
                    = vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__sin_val;
                vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__current_sense_angle 
                    = (0x1ffffffU & (vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_reg 
                                     - (IData)(0x800U)));
            }
        } else if ((1U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
            vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_b = 0x9000U;
            vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_a 
                = vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__cos_val;
            vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__current_sense_angle 
                = (0x1ffffffU & (vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_reg 
                                 - (IData)(0x800U)));
        } else {
            vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_b = 0U;
            vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_a = 0U;
            vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__current_sense_angle 
                = (0x1ffffffU & vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_reg);
        }
    } else {
        if ((2U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
            if ((1U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
                vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_b = 0U;
                vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_a = 0U;
            } else {
                vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_b = 0x9000U;
                vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_a 
                    = vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__sin_val;
            }
        } else if ((1U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
            vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_b = 0x9000U;
            vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_a 
                = vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__cos_val;
        } else {
            vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_b = 0U;
            vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_a = 0U;
        }
        vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__current_sense_angle 
            = (0x1ffffffU & ((4U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))
                              ? ((2U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))
                                  ? ((1U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))
                                      ? vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_reg
                                      : ((IData)(0x800U) 
                                         + vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_reg))
                                  : ((1U & (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))
                                      ? ((IData)(0x800U) 
                                         + vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_reg)
                                      : vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_reg))
                              : vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_reg));
    }
    if (vlSelf->slime_top__DOT__pattern_trail_we) {
        if ((0x12U == (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state))) {
            vlSelf->slime_top__DOT__trail_we_b = 1U;
            vlSelf->slime_top__DOT__trail_data_b_in = 0x5000U;
            vlSelf->slime_top__DOT__trail_addr_b = 
                (0x7ffffU & (((IData)(0x140U) * (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_write_y)) 
                             + (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_write_x)));
        } else {
            vlSelf->slime_top__DOT__trail_we_b = 0U;
            vlSelf->slime_top__DOT__trail_data_b_in = 0U;
            vlSelf->slime_top__DOT__trail_addr_b = 
                (0x7ffffU & (((IData)(0x140U) * (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_read_y)) 
                             + (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_read_x)));
        }
    } else {
        vlSelf->slime_top__DOT__trail_we_b = vlSelf->slime_top__DOT__pattern_trail_we;
        vlSelf->slime_top__DOT__trail_data_b_in = vlSelf->slime_top__DOT__sim_trail_data;
        vlSelf->slime_top__DOT__trail_addr_b = (0x7ffffU 
                                                & vlSelf->slime_top__DOT__sim_trail_addr);
    }
    vlSelf->slime_top__DOT__lfsr_enable = ((~ (IData)(vlSelf->sw)) 
                                           & (0xdU 
                                              == (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state)));
    vlSelf->slime_top__DOT__u_coordinator__DOT__proc_start 
        = ((~ ((IData)(vlSelf->sw) | ((0U != (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state)) 
                                      | (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__step_freeze_cycle)))) 
           & (2U == (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__state)));
    __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_to_idx__0__angle 
        = vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__current_sense_angle;
    __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_to_idx__0__normalized 
        = __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_to_idx__0__angle;
    if (VL_GTS_III(32, 0U, VL_EXTENDS_II(32,25, __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_to_idx__0__normalized))) {
        __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_to_idx__0__normalized 
            = (0x1ffffffU & ((IData)(0x6487U) + __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_to_idx__0__normalized));
    }
    if (VL_GTS_III(32, 0U, VL_EXTENDS_II(32,25, __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_to_idx__0__normalized))) {
        __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_to_idx__0__normalized 
            = (0x1ffffffU & ((IData)(0x6487U) + __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_to_idx__0__normalized));
    }
    if (VL_LTES_III(25, 0x6487U, __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_to_idx__0__normalized)) {
        __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_to_idx__0__normalized 
            = (0x1ffffffU & (__Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_to_idx__0__normalized 
                             - (IData)(0x6487U)));
    }
    if (VL_LTES_III(25, 0x6487U, __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_to_idx__0__normalized)) {
        __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_to_idx__0__normalized 
            = (0x1ffffffU & (__Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_to_idx__0__normalized 
                             - (IData)(0x6487U)));
    }
    __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_to_idx__0__scaled 
        = (0x1ffffffU & VL_DIVS_III(32, VL_SHIFTL_III(32,32,32, 
                                                      VL_EXTENDS_II(32,25, __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_to_idx__0__normalized), 0xaU), (IData)(0x6489U)));
    __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_to_idx__0__Vfuncout 
        = (0x3ffU & __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_to_idx__0__scaled);
    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__trig_angle_idx 
        = __Vfunc_slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_to_idx__0__Vfuncout;
    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__u_mult__DOT__full_product 
        = (0x3ffffffffffffULL & VL_MULS_QQQ(50, (0x3ffffffffffffULL 
                                                 & VL_EXTENDS_QI(50,25, vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_a)), 
                                            (0x3ffffffffffffULL 
                                             & VL_EXTENDS_QI(50,25, vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_b))));
    __Vtableidx2 = (((IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__proc_start) 
                     << 5U) | (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state));
    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__next_state 
        = Vslime_top__ConstPool__TABLE_hc133f9f5_0[__Vtableidx2];
}

VL_INLINE_OPT void Vslime_top___024root___nba_sequent__TOP__2(Vslime_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root___nba_sequent__TOP__2\n"); );
    // Body
    vlSelf->slime_top__DOT__frame_start = ((0U == (IData)(vlSelf->slime_top__DOT__u_vga__DOT__h_count)) 
                                           & (0U == (IData)(vlSelf->slime_top__DOT__u_vga__DOT__v_count)));
}

VL_INLINE_OPT void Vslime_top___024root___nba_sequent__TOP__3(Vslime_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root___nba_sequent__TOP__3\n"); );
    // Body
    vlSelf->debug_agent_data = ((0U == (IData)(vlSelf->debug_agent_sel))
                                 ? ((9U >= (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__debug_idx_safe))
                                     ? vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x
                                    [vlSelf->slime_top__DOT__u_coordinator__DOT__debug_idx_safe]
                                     : 0U) : ((1U == (IData)(vlSelf->debug_agent_sel))
                                               ? ((9U 
                                                   >= (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__debug_idx_safe))
                                                   ? 
                                                  vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y
                                                  [vlSelf->slime_top__DOT__u_coordinator__DOT__debug_idx_safe]
                                                   : 0U)
                                               : ((2U 
                                                   == (IData)(vlSelf->debug_agent_sel))
                                                   ? 
                                                  ((9U 
                                                    >= (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__debug_idx_safe))
                                                    ? 
                                                   vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle
                                                   [vlSelf->slime_top__DOT__u_coordinator__DOT__debug_idx_safe]
                                                    : 0U)
                                                   : 0U)));
}

void Vslime_top___024root___eval_nba(Vslime_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root___eval_nba\n"); );
    // Body
    if ((2ULL & vlSelf->__VnbaTriggered.word(0U))) {
        Vslime_top___024root___nba_sequent__TOP__0(vlSelf);
        vlSelf->__Vm_traceActivity[2U] = 1U;
    }
    if ((1ULL & vlSelf->__VnbaTriggered.word(0U))) {
        Vslime_top___024root___nba_sequent__TOP__1(vlSelf);
        vlSelf->__Vm_traceActivity[3U] = 1U;
    }
    if ((2ULL & vlSelf->__VnbaTriggered.word(0U))) {
        Vslime_top___024root___nba_sequent__TOP__2(vlSelf);
    }
    if ((1ULL & vlSelf->__VnbaTriggered.word(0U))) {
        Vslime_top___024root___nba_sequent__TOP__3(vlSelf);
    }
}

void Vslime_top___024root___eval_triggers__act(Vslime_top___024root* vlSelf);

bool Vslime_top___024root___eval_phase__act(Vslime_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root___eval_phase__act\n"); );
    // Init
    VlTriggerVec<2> __VpreTriggered;
    CData/*0:0*/ __VactExecute;
    // Body
    Vslime_top___024root___eval_triggers__act(vlSelf);
    __VactExecute = vlSelf->__VactTriggered.any();
    if (__VactExecute) {
        __VpreTriggered.andNot(vlSelf->__VactTriggered, vlSelf->__VnbaTriggered);
        vlSelf->__VnbaTriggered.thisOr(vlSelf->__VactTriggered);
        Vslime_top___024root___eval_act(vlSelf);
    }
    return (__VactExecute);
}

bool Vslime_top___024root___eval_phase__nba(Vslime_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root___eval_phase__nba\n"); );
    // Init
    CData/*0:0*/ __VnbaExecute;
    // Body
    __VnbaExecute = vlSelf->__VnbaTriggered.any();
    if (__VnbaExecute) {
        Vslime_top___024root___eval_nba(vlSelf);
        vlSelf->__VnbaTriggered.clear();
    }
    return (__VnbaExecute);
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vslime_top___024root___dump_triggers__ico(Vslime_top___024root* vlSelf);
#endif  // VL_DEBUG
#ifdef VL_DEBUG
VL_ATTR_COLD void Vslime_top___024root___dump_triggers__nba(Vslime_top___024root* vlSelf);
#endif  // VL_DEBUG
#ifdef VL_DEBUG
VL_ATTR_COLD void Vslime_top___024root___dump_triggers__act(Vslime_top___024root* vlSelf);
#endif  // VL_DEBUG

void Vslime_top___024root___eval(Vslime_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root___eval\n"); );
    // Init
    IData/*31:0*/ __VicoIterCount;
    CData/*0:0*/ __VicoContinue;
    IData/*31:0*/ __VnbaIterCount;
    CData/*0:0*/ __VnbaContinue;
    // Body
    __VicoIterCount = 0U;
    vlSelf->__VicoFirstIteration = 1U;
    __VicoContinue = 1U;
    while (__VicoContinue) {
        if (VL_UNLIKELY((0x64U < __VicoIterCount))) {
#ifdef VL_DEBUG
            Vslime_top___024root___dump_triggers__ico(vlSelf);
#endif
            VL_FATAL_MT("../src/../src/slime_top.sv", 15, "", "Input combinational region did not converge.");
        }
        __VicoIterCount = ((IData)(1U) + __VicoIterCount);
        __VicoContinue = 0U;
        if (Vslime_top___024root___eval_phase__ico(vlSelf)) {
            __VicoContinue = 1U;
        }
        vlSelf->__VicoFirstIteration = 0U;
    }
    __VnbaIterCount = 0U;
    __VnbaContinue = 1U;
    while (__VnbaContinue) {
        if (VL_UNLIKELY((0x64U < __VnbaIterCount))) {
#ifdef VL_DEBUG
            Vslime_top___024root___dump_triggers__nba(vlSelf);
#endif
            VL_FATAL_MT("../src/../src/slime_top.sv", 15, "", "NBA region did not converge.");
        }
        __VnbaIterCount = ((IData)(1U) + __VnbaIterCount);
        __VnbaContinue = 0U;
        vlSelf->__VactIterCount = 0U;
        vlSelf->__VactContinue = 1U;
        while (vlSelf->__VactContinue) {
            if (VL_UNLIKELY((0x64U < vlSelf->__VactIterCount))) {
#ifdef VL_DEBUG
                Vslime_top___024root___dump_triggers__act(vlSelf);
#endif
                VL_FATAL_MT("../src/../src/slime_top.sv", 15, "", "Active region did not converge.");
            }
            vlSelf->__VactIterCount = ((IData)(1U) 
                                       + vlSelf->__VactIterCount);
            vlSelf->__VactContinue = 0U;
            if (Vslime_top___024root___eval_phase__act(vlSelf)) {
                vlSelf->__VactContinue = 1U;
            }
        }
        if (Vslime_top___024root___eval_phase__nba(vlSelf)) {
            __VnbaContinue = 1U;
        }
    }
}

#ifdef VL_DEBUG
void Vslime_top___024root___eval_debug_assertions(Vslime_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root___eval_debug_assertions\n"); );
    // Body
    if (VL_UNLIKELY((vlSelf->clk_100mhz & 0xfeU))) {
        Verilated::overWidthError("clk_100mhz");}
    if (VL_UNLIKELY((vlSelf->btnc & 0xfeU))) {
        Verilated::overWidthError("btnc");}
    if (VL_UNLIKELY((vlSelf->btnu & 0xfeU))) {
        Verilated::overWidthError("btnu");}
    if (VL_UNLIKELY((vlSelf->btnd & 0xfeU))) {
        Verilated::overWidthError("btnd");}
    if (VL_UNLIKELY((vlSelf->btnl & 0xfeU))) {
        Verilated::overWidthError("btnl");}
    if (VL_UNLIKELY((vlSelf->btnr & 0xfeU))) {
        Verilated::overWidthError("btnr");}
    if (VL_UNLIKELY((vlSelf->sim_start & 0xfeU))) {
        Verilated::overWidthError("sim_start");}
    if (VL_UNLIKELY((vlSelf->debug_trail_addr & 0xfff80000U))) {
        Verilated::overWidthError("debug_trail_addr");}
    if (VL_UNLIKELY((vlSelf->debug_agent_idx & 0xfc00U))) {
        Verilated::overWidthError("debug_agent_idx");}
    if (VL_UNLIKELY((vlSelf->debug_agent_sel & 0xfcU))) {
        Verilated::overWidthError("debug_agent_sel");}
    if (VL_UNLIKELY((vlSelf->debug_agent_write_en & 0xfeU))) {
        Verilated::overWidthError("debug_agent_write_en");}
    if (VL_UNLIKELY((vlSelf->debug_agent_data_write 
                     & 0xfe000000U))) {
        Verilated::overWidthError("debug_agent_data_write");}
}
#endif  // VL_DEBUG
