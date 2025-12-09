// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vslime_top.h for the primary calling header

#include "Vslime_top__pch.h"
#include "Vslime_top___024root.h"

VL_ATTR_COLD void Vslime_top___024root___eval_static__TOP(Vslime_top___024root* vlSelf);

VL_ATTR_COLD void Vslime_top___024root___eval_static(Vslime_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root___eval_static\n"); );
    // Body
    Vslime_top___024root___eval_static__TOP(vlSelf);
    vlSelf->__Vm_traceActivity[3U] = 1U;
    vlSelf->__Vm_traceActivity[2U] = 1U;
    vlSelf->__Vm_traceActivity[1U] = 1U;
    vlSelf->__Vm_traceActivity[0U] = 1U;
}

VL_ATTR_COLD void Vslime_top___024root___eval_static__TOP(Vslime_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root___eval_static__TOP\n"); );
    // Body
    vlSelf->slime_top__DOT__u_trail_ram__DOT__mem_out_a = 0U;
    vlSelf->slime_top__DOT__u_trail_ram__DOT__mem_out_b = 0U;
    vlSelf->slime_top__DOT__u_trail_ram__DOT__pipe_a[0U] = 0U;
    vlSelf->slime_top__DOT__u_trail_ram__DOT__pipe_a[1U] = 0U;
    vlSelf->slime_top__DOT__u_trail_ram__DOT__pipe_b[0U] = 0U;
    vlSelf->slime_top__DOT__u_trail_ram__DOT__pipe_b[1U] = 0U;
}

VL_ATTR_COLD void Vslime_top___024root___eval_initial__TOP(Vslime_top___024root* vlSelf);

VL_ATTR_COLD void Vslime_top___024root___eval_initial(Vslime_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root___eval_initial\n"); );
    // Body
    Vslime_top___024root___eval_initial__TOP(vlSelf);
    vlSelf->__Vm_traceActivity[3U] = 1U;
    vlSelf->__Vm_traceActivity[2U] = 1U;
    vlSelf->__Vm_traceActivity[1U] = 1U;
    vlSelf->__Vm_traceActivity[0U] = 1U;
    vlSelf->__Vtrigprevexpr___TOP__clk_100mhz__0 = vlSelf->clk_100mhz;
    vlSelf->__Vtrigprevexpr___TOP__slime_top__DOT__clk_25mhz__0 
        = vlSelf->slime_top__DOT__clk_25mhz;
}

VL_ATTR_COLD void Vslime_top___024root___eval_initial__TOP(Vslime_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root___eval_initial__TOP\n"); );
    // Init
    VlWide<3>/*95:0*/ __Vtemp_2;
    VlWide<3>/*95:0*/ __Vtemp_3;
    // Body
    vlSelf->debug_trail_data = 0U;
    vlSelf->slime_top__DOT__u_trail_ram__DOT__unnamedblk1__DOT__i = 0U;
    while (VL_GTS_III(32, 0x12c00U, vlSelf->slime_top__DOT__u_trail_ram__DOT__unnamedblk1__DOT__i)) {
        vlSelf->slime_top__DOT__u_trail_ram__DOT____Vlvbound_hf71990d5__0 = 0U;
        if (VL_LIKELY((0x12bffU >= (0x1ffffU & vlSelf->slime_top__DOT__u_trail_ram__DOT__unnamedblk1__DOT__i)))) {
            vlSelf->slime_top__DOT__u_trail_ram__DOT__mem[(0x1ffffU 
                                                           & vlSelf->slime_top__DOT__u_trail_ram__DOT__unnamedblk1__DOT__i)] 
                = vlSelf->slime_top__DOT__u_trail_ram__DOT____Vlvbound_hf71990d5__0;
        }
        vlSelf->slime_top__DOT__u_trail_ram__DOT__unnamedblk1__DOT__i 
            = ((IData)(1U) + vlSelf->slime_top__DOT__u_trail_ram__DOT__unnamedblk1__DOT__i);
    }
    vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x[0U] = 0U;
    vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y[0U] = 0U;
    vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle[0U] = 0U;
    vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x[1U] = 0U;
    vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y[1U] = 0U;
    vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle[1U] = 0U;
    vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x[2U] = 0U;
    vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y[2U] = 0U;
    vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle[2U] = 0U;
    vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x[3U] = 0U;
    vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y[3U] = 0U;
    vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle[3U] = 0U;
    vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x[4U] = 0U;
    vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y[4U] = 0U;
    vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle[4U] = 0U;
    vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x[5U] = 0U;
    vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y[5U] = 0U;
    vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle[5U] = 0U;
    vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x[6U] = 0U;
    vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y[6U] = 0U;
    vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle[6U] = 0U;
    vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x[7U] = 0U;
    vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y[7U] = 0U;
    vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle[7U] = 0U;
    vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x[8U] = 0U;
    vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y[8U] = 0U;
    vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle[8U] = 0U;
    vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x[9U] = 0U;
    vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y[9U] = 0U;
    vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle[9U] = 0U;
    vlSelf->slime_top__DOT__u_coordinator__DOT__unnamedblk1__DOT__i = 0xaU;
    __Vtemp_2[0U] = 0x2e686578U;
    __Vtemp_2[1U] = 0x5f6c7574U;
    __Vtemp_2[2U] = 0x73696eU;
    VL_READMEM_N(true, 25, 1024, 0, VL_CVT_PACK_STR_NW(3, __Vtemp_2)
                 ,  &(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__u_trig_lut__DOT__sin_rom)
                 , 0, ~0ULL);
    __Vtemp_3[0U] = 0x2e686578U;
    __Vtemp_3[1U] = 0x5f6c7574U;
    __Vtemp_3[2U] = 0x636f73U;
    VL_READMEM_N(true, 25, 1024, 0, VL_CVT_PACK_STR_NW(3, __Vtemp_3)
                 ,  &(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__u_trig_lut__DOT__cos_rom)
                 , 0, ~0ULL);
}

VL_ATTR_COLD void Vslime_top___024root___eval_final(Vslime_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root___eval_final\n"); );
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vslime_top___024root___dump_triggers__stl(Vslime_top___024root* vlSelf);
#endif  // VL_DEBUG
VL_ATTR_COLD bool Vslime_top___024root___eval_phase__stl(Vslime_top___024root* vlSelf);

VL_ATTR_COLD void Vslime_top___024root___eval_settle(Vslime_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root___eval_settle\n"); );
    // Init
    IData/*31:0*/ __VstlIterCount;
    CData/*0:0*/ __VstlContinue;
    // Body
    __VstlIterCount = 0U;
    vlSelf->__VstlFirstIteration = 1U;
    __VstlContinue = 1U;
    while (__VstlContinue) {
        if (VL_UNLIKELY((0x64U < __VstlIterCount))) {
#ifdef VL_DEBUG
            Vslime_top___024root___dump_triggers__stl(vlSelf);
#endif
            VL_FATAL_MT("../src/../src/slime_top.sv", 15, "", "Settle region did not converge.");
        }
        __VstlIterCount = ((IData)(1U) + __VstlIterCount);
        __VstlContinue = 0U;
        if (Vslime_top___024root___eval_phase__stl(vlSelf)) {
            __VstlContinue = 1U;
        }
        vlSelf->__VstlFirstIteration = 0U;
    }
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vslime_top___024root___dump_triggers__stl(Vslime_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root___dump_triggers__stl\n"); );
    // Body
    if ((1U & (~ (IData)(vlSelf->__VstlTriggered.any())))) {
        VL_DBG_MSGF("         No triggers active\n");
    }
    if ((1ULL & vlSelf->__VstlTriggered.word(0U))) {
        VL_DBG_MSGF("         'stl' region trigger index 0 is active: Internal 'stl' trigger - first iteration\n");
    }
}
#endif  // VL_DEBUG

extern const VlUnpacked<CData/*2:0*/, 16> Vslime_top__ConstPool__TABLE_hd2b3370f_0;
extern const VlUnpacked<CData/*4:0*/, 64> Vslime_top__ConstPool__TABLE_hc133f9f5_0;

VL_ATTR_COLD void Vslime_top___024root___stl_sequent__TOP__0(Vslime_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root___stl_sequent__TOP__0\n"); );
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
    // Body
    vlSelf->slime_top__DOT__u_lfsr__DOT__feedback = 
        (1U & VL_REDXOR_32((0xc0000401U & vlSelf->slime_top__DOT__u_lfsr__DOT__lfsr_reg)));
    vlSelf->step_complete_pulse = vlSelf->slime_top__DOT__u_coordinator__DOT__step_writeback_cycle;
    vlSelf->slime_top__DOT__clk_25mhz = (1U & ((IData)(vlSelf->slime_top__DOT__clk_div) 
                                               >> 1U));
    vlSelf->slime_top__DOT__lfsr_enable = ((~ (IData)(vlSelf->sw)) 
                                           & (0xdU 
                                              == (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state)));
    vlSelf->slime_top__DOT__btn_random = ((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_stable_prev)) 
                                          & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_stable));
    vlSelf->slime_top__DOT__frame_start = ((0U == (IData)(vlSelf->slime_top__DOT__u_vga__DOT__h_count)) 
                                           & (0U == (IData)(vlSelf->slime_top__DOT__u_vga__DOT__v_count)));
    vlSelf->slime_top__DOT__trail_addr_a = (0x7ffffU 
                                            & (((IData)(0x140U) 
                                                * VL_SHIFTR_III(32,32,32, 
                                                                (0x1ffU 
                                                                 & (IData)(vlSelf->slime_top__DOT__u_vga__DOT__v_count)), 2U)) 
                                               + (0xffU 
                                                  & ((IData)(vlSelf->slime_top__DOT__u_vga__DOT__h_count) 
                                                     >> 2U))));
    vlSelf->slime_top__DOT__pixel_valid = ((0x280U 
                                            > (IData)(vlSelf->slime_top__DOT__u_vga__DOT__h_count)) 
                                           & (0x1e0U 
                                              > (IData)(vlSelf->slime_top__DOT__u_vga__DOT__v_count)));
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
    vlSelf->slime_top__DOT__u_coordinator__DOT__debug_idx_safe 
        = ((0xaU > (IData)(vlSelf->debug_agent_idx))
            ? (0xfU & (IData)(vlSelf->debug_agent_idx))
            : 0U);
    vlSelf->slime_top__DOT__btn_start = ((~ (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_stable_prev)) 
                                         & (IData)(vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_stable));
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
    vlSelf->slime_top__DOT__pattern_trail_we = ((~ (IData)(vlSelf->sw)) 
                                                & (2U 
                                                   == (IData)(vlSelf->slime_top__DOT__sim_state)));
    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__u_mult__DOT__full_product 
        = (0x3ffffffffffffULL & VL_MULS_QQQ(50, (0x3ffffffffffffULL 
                                                 & VL_EXTENDS_QI(50,25, vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_a)), 
                                            (0x3ffffffffffffULL 
                                             & VL_EXTENDS_QI(50,25, vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_b))));
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
    __Vtableidx1 = ((((IData)(vlSelf->sim_start) | (IData)(vlSelf->slime_top__DOT__btn_start)) 
                     << 3U) | (IData)(vlSelf->slime_top__DOT__u_coordinator__DOT__state));
    vlSelf->slime_top__DOT__u_coordinator__DOT__next_state 
        = Vslime_top__ConstPool__TABLE_hd2b3370f_0[__Vtableidx1];
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

VL_ATTR_COLD void Vslime_top___024root___eval_stl(Vslime_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root___eval_stl\n"); );
    // Body
    if ((1ULL & vlSelf->__VstlTriggered.word(0U))) {
        Vslime_top___024root___stl_sequent__TOP__0(vlSelf);
        vlSelf->__Vm_traceActivity[3U] = 1U;
        vlSelf->__Vm_traceActivity[2U] = 1U;
        vlSelf->__Vm_traceActivity[1U] = 1U;
        vlSelf->__Vm_traceActivity[0U] = 1U;
    }
}

VL_ATTR_COLD void Vslime_top___024root___eval_triggers__stl(Vslime_top___024root* vlSelf);

VL_ATTR_COLD bool Vslime_top___024root___eval_phase__stl(Vslime_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root___eval_phase__stl\n"); );
    // Init
    CData/*0:0*/ __VstlExecute;
    // Body
    Vslime_top___024root___eval_triggers__stl(vlSelf);
    __VstlExecute = vlSelf->__VstlTriggered.any();
    if (__VstlExecute) {
        Vslime_top___024root___eval_stl(vlSelf);
    }
    return (__VstlExecute);
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vslime_top___024root___dump_triggers__ico(Vslime_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root___dump_triggers__ico\n"); );
    // Body
    if ((1U & (~ (IData)(vlSelf->__VicoTriggered.any())))) {
        VL_DBG_MSGF("         No triggers active\n");
    }
    if ((1ULL & vlSelf->__VicoTriggered.word(0U))) {
        VL_DBG_MSGF("         'ico' region trigger index 0 is active: Internal 'ico' trigger - first iteration\n");
    }
}
#endif  // VL_DEBUG

#ifdef VL_DEBUG
VL_ATTR_COLD void Vslime_top___024root___dump_triggers__act(Vslime_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root___dump_triggers__act\n"); );
    // Body
    if ((1U & (~ (IData)(vlSelf->__VactTriggered.any())))) {
        VL_DBG_MSGF("         No triggers active\n");
    }
    if ((1ULL & vlSelf->__VactTriggered.word(0U))) {
        VL_DBG_MSGF("         'act' region trigger index 0 is active: @(posedge clk_100mhz)\n");
    }
    if ((2ULL & vlSelf->__VactTriggered.word(0U))) {
        VL_DBG_MSGF("         'act' region trigger index 1 is active: @(posedge slime_top.clk_25mhz)\n");
    }
}
#endif  // VL_DEBUG

#ifdef VL_DEBUG
VL_ATTR_COLD void Vslime_top___024root___dump_triggers__nba(Vslime_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root___dump_triggers__nba\n"); );
    // Body
    if ((1U & (~ (IData)(vlSelf->__VnbaTriggered.any())))) {
        VL_DBG_MSGF("         No triggers active\n");
    }
    if ((1ULL & vlSelf->__VnbaTriggered.word(0U))) {
        VL_DBG_MSGF("         'nba' region trigger index 0 is active: @(posedge clk_100mhz)\n");
    }
    if ((2ULL & vlSelf->__VnbaTriggered.word(0U))) {
        VL_DBG_MSGF("         'nba' region trigger index 1 is active: @(posedge slime_top.clk_25mhz)\n");
    }
}
#endif  // VL_DEBUG

VL_ATTR_COLD void Vslime_top___024root___ctor_var_reset(Vslime_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root___ctor_var_reset\n"); );
    // Body
    vlSelf->clk_100mhz = VL_RAND_RESET_I(1);
    vlSelf->btnc = VL_RAND_RESET_I(1);
    vlSelf->btnu = VL_RAND_RESET_I(1);
    vlSelf->btnd = VL_RAND_RESET_I(1);
    vlSelf->btnl = VL_RAND_RESET_I(1);
    vlSelf->btnr = VL_RAND_RESET_I(1);
    vlSelf->sw = VL_RAND_RESET_I(16);
    vlSelf->vga_r = VL_RAND_RESET_I(4);
    vlSelf->vga_g = VL_RAND_RESET_I(4);
    vlSelf->vga_b = VL_RAND_RESET_I(4);
    vlSelf->vga_hs = VL_RAND_RESET_I(1);
    vlSelf->vga_vs = VL_RAND_RESET_I(1);
    vlSelf->led = VL_RAND_RESET_I(16);
    vlSelf->sim_start = VL_RAND_RESET_I(1);
    vlSelf->debug_trail_addr = VL_RAND_RESET_I(19);
    vlSelf->debug_trail_data = VL_RAND_RESET_I(18);
    vlSelf->debug_agent_idx = VL_RAND_RESET_I(10);
    vlSelf->debug_agent_sel = VL_RAND_RESET_I(2);
    vlSelf->debug_agent_data = VL_RAND_RESET_I(25);
    vlSelf->debug_agent_write_en = VL_RAND_RESET_I(1);
    vlSelf->debug_agent_data_write = VL_RAND_RESET_I(25);
    vlSelf->step_complete_pulse = VL_RAND_RESET_I(1);
    vlSelf->slime_top__DOT__clk_25mhz = VL_RAND_RESET_I(1);
    vlSelf->slime_top__DOT__clk_div = VL_RAND_RESET_I(2);
    vlSelf->slime_top__DOT__btn_start = VL_RAND_RESET_I(1);
    vlSelf->slime_top__DOT__btn_random = VL_RAND_RESET_I(1);
    vlSelf->slime_top__DOT__speed_level = VL_RAND_RESET_I(4);
    vlSelf->slime_top__DOT__lfsr_enable = VL_RAND_RESET_I(1);
    vlSelf->slime_top__DOT__lfsr_load = VL_RAND_RESET_I(1);
    vlSelf->slime_top__DOT__lfsr_seed = VL_RAND_RESET_I(32);
    vlSelf->slime_top__DOT__trail_addr_a = VL_RAND_RESET_I(19);
    vlSelf->slime_top__DOT__trail_addr_b = VL_RAND_RESET_I(19);
    vlSelf->slime_top__DOT__trail_data_b_in = VL_RAND_RESET_I(18);
    vlSelf->slime_top__DOT__trail_we_b = VL_RAND_RESET_I(1);
    vlSelf->slime_top__DOT__pixel_valid = VL_RAND_RESET_I(1);
    vlSelf->slime_top__DOT__frame_start = VL_RAND_RESET_I(1);
    vlSelf->slime_top__DOT__frame_count = VL_RAND_RESET_I(32);
    vlSelf->slime_top__DOT__sim_state = VL_RAND_RESET_I(4);
    vlSelf->slime_top__DOT__agent_idx = VL_RAND_RESET_I(17);
    vlSelf->slime_top__DOT__sim_running = VL_RAND_RESET_I(1);
    vlSelf->slime_top__DOT__trail_val_before_decay = VL_RAND_RESET_I(18);
    vlSelf->slime_top__DOT__trail_val_after_mult = VL_RAND_RESET_Q(36);
    vlSelf->slime_top__DOT__trail_val_decayed = VL_RAND_RESET_I(18);
    vlSelf->slime_top__DOT__orch_trail_read_data = VL_RAND_RESET_I(18);
    vlSelf->slime_top__DOT__pattern_trail_we = VL_RAND_RESET_I(1);
    vlSelf->slime_top__DOT__sim_trail_addr = VL_RAND_RESET_I(19);
    vlSelf->slime_top__DOT__sim_trail_data = VL_RAND_RESET_I(8);
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__counter = VL_RAND_RESET_I(21);
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_sync_0 = VL_RAND_RESET_I(1);
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_sync_1 = VL_RAND_RESET_I(1);
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_stable = VL_RAND_RESET_I(1);
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_stable_prev = VL_RAND_RESET_I(1);
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__counter = VL_RAND_RESET_I(21);
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_sync_0 = VL_RAND_RESET_I(1);
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_sync_1 = VL_RAND_RESET_I(1);
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable = VL_RAND_RESET_I(1);
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable_prev = VL_RAND_RESET_I(1);
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__counter = VL_RAND_RESET_I(21);
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_sync_0 = VL_RAND_RESET_I(1);
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_sync_1 = VL_RAND_RESET_I(1);
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable = VL_RAND_RESET_I(1);
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable_prev = VL_RAND_RESET_I(1);
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__counter = VL_RAND_RESET_I(21);
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_sync_0 = VL_RAND_RESET_I(1);
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_sync_1 = VL_RAND_RESET_I(1);
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_stable = VL_RAND_RESET_I(1);
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_stable_prev = VL_RAND_RESET_I(1);
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__counter = VL_RAND_RESET_I(21);
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_sync_0 = VL_RAND_RESET_I(1);
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_sync_1 = VL_RAND_RESET_I(1);
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_stable = VL_RAND_RESET_I(1);
    vlSelf->slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_stable_prev = VL_RAND_RESET_I(1);
    vlSelf->slime_top__DOT__u_lfsr__DOT__valid = VL_RAND_RESET_I(1);
    vlSelf->slime_top__DOT__u_lfsr__DOT__lfsr_reg = VL_RAND_RESET_I(32);
    vlSelf->slime_top__DOT__u_lfsr__DOT__feedback = VL_RAND_RESET_I(1);
    for (int __Vi0 = 0; __Vi0 < 76800; ++__Vi0) {
        vlSelf->slime_top__DOT__u_trail_ram__DOT__mem[__Vi0] = VL_RAND_RESET_I(18);
    }
    vlSelf->slime_top__DOT__u_trail_ram__DOT__mem_out_a = VL_RAND_RESET_I(18);
    vlSelf->slime_top__DOT__u_trail_ram__DOT__mem_out_b = VL_RAND_RESET_I(18);
    for (int __Vi0 = 0; __Vi0 < 2; ++__Vi0) {
        vlSelf->slime_top__DOT__u_trail_ram__DOT__pipe_a[__Vi0] = VL_RAND_RESET_I(18);
    }
    for (int __Vi0 = 0; __Vi0 < 2; ++__Vi0) {
        vlSelf->slime_top__DOT__u_trail_ram__DOT__pipe_b[__Vi0] = VL_RAND_RESET_I(18);
    }
    vlSelf->slime_top__DOT__u_trail_ram__DOT__unnamedblk1__DOT__i = 0;
    vlSelf->slime_top__DOT__u_trail_ram__DOT____Vlvbound_hf71990d5__0 = VL_RAND_RESET_I(18);
    vlSelf->slime_top__DOT__u_trail_ram__DOT____Vlvbound_h51f3e5a2__0 = VL_RAND_RESET_I(18);
    vlSelf->slime_top__DOT__u_vga__DOT__h_count = VL_RAND_RESET_I(10);
    vlSelf->slime_top__DOT__u_vga__DOT__v_count = VL_RAND_RESET_I(10);
    for (int __Vi0 = 0; __Vi0 < 10; ++__Vi0) {
        vlSelf->slime_top__DOT__u_coordinator__DOT__agent_x[__Vi0] = VL_RAND_RESET_I(25);
    }
    for (int __Vi0 = 0; __Vi0 < 10; ++__Vi0) {
        vlSelf->slime_top__DOT__u_coordinator__DOT__agent_y[__Vi0] = VL_RAND_RESET_I(25);
    }
    for (int __Vi0 = 0; __Vi0 < 10; ++__Vi0) {
        vlSelf->slime_top__DOT__u_coordinator__DOT__agent_angle[__Vi0] = VL_RAND_RESET_I(25);
    }
    vlSelf->slime_top__DOT__u_coordinator__DOT__state = VL_RAND_RESET_I(3);
    vlSelf->slime_top__DOT__u_coordinator__DOT__next_state = VL_RAND_RESET_I(3);
    vlSelf->slime_top__DOT__u_coordinator__DOT__current_agent_idx = VL_RAND_RESET_I(4);
    vlSelf->slime_top__DOT__u_coordinator__DOT__step_counter = VL_RAND_RESET_I(32);
    vlSelf->slime_top__DOT__u_coordinator__DOT__proc_start = VL_RAND_RESET_I(1);
    vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_read_x = VL_RAND_RESET_I(10);
    vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_write_x = VL_RAND_RESET_I(10);
    vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_read_y = VL_RAND_RESET_I(9);
    vlSelf->slime_top__DOT__u_coordinator__DOT__proc_trail_write_y = VL_RAND_RESET_I(9);
    vlSelf->slime_top__DOT__u_coordinator__DOT__latched_x_out = VL_RAND_RESET_I(25);
    vlSelf->slime_top__DOT__u_coordinator__DOT__latched_y_out = VL_RAND_RESET_I(25);
    vlSelf->slime_top__DOT__u_coordinator__DOT__latched_angle_out = VL_RAND_RESET_I(25);
    vlSelf->slime_top__DOT__u_coordinator__DOT__latched_valid = VL_RAND_RESET_I(1);
    vlSelf->slime_top__DOT__u_coordinator__DOT__prev_idx = VL_RAND_RESET_I(4);
    vlSelf->slime_top__DOT__u_coordinator__DOT__step_just_completed = VL_RAND_RESET_I(1);
    vlSelf->slime_top__DOT__u_coordinator__DOT__step_freeze_cycle = VL_RAND_RESET_I(1);
    vlSelf->slime_top__DOT__u_coordinator__DOT__step_writeback_cycle = VL_RAND_RESET_I(1);
    vlSelf->slime_top__DOT__u_coordinator__DOT__debug_idx_safe = VL_RAND_RESET_I(4);
    vlSelf->slime_top__DOT__u_coordinator__DOT__unnamedblk1__DOT__i = 0;
    vlSelf->slime_top__DOT__u_coordinator__DOT____Vlvbound_h1f94e32a__0 = VL_RAND_RESET_I(25);
    vlSelf->slime_top__DOT__u_coordinator__DOT____Vlvbound_hcb92b3ef__0 = VL_RAND_RESET_I(25);
    vlSelf->slime_top__DOT__u_coordinator__DOT____Vlvbound_hd63147c5__0 = VL_RAND_RESET_I(25);
    vlSelf->slime_top__DOT__u_coordinator__DOT____Vlvbound_h1f94e32a__1 = VL_RAND_RESET_I(25);
    vlSelf->slime_top__DOT__u_coordinator__DOT____Vlvbound_hcb92b3ef__1 = VL_RAND_RESET_I(25);
    vlSelf->slime_top__DOT__u_coordinator__DOT____Vlvbound_hd63147c5__1 = VL_RAND_RESET_I(25);
    vlSelf->slime_top__DOT__u_coordinator__DOT____Vlvbound_h1f94e32a__2 = VL_RAND_RESET_I(25);
    vlSelf->slime_top__DOT__u_coordinator__DOT____Vlvbound_hcb92b3ef__2 = VL_RAND_RESET_I(25);
    vlSelf->slime_top__DOT__u_coordinator__DOT____Vlvbound_hd63147c5__2 = VL_RAND_RESET_I(25);
    vlSelf->slime_top__DOT__u_coordinator__DOT____Vlvbound_h2b5da6a3__0 = VL_RAND_RESET_I(25);
    vlSelf->slime_top__DOT__u_coordinator__DOT____Vlvbound_haf1b776c__0 = VL_RAND_RESET_I(25);
    vlSelf->slime_top__DOT__u_coordinator__DOT____Vlvbound_hd9a9fc40__0 = VL_RAND_RESET_I(25);
    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state = VL_RAND_RESET_I(5);
    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__next_state = VL_RAND_RESET_I(5);
    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__x_reg = VL_RAND_RESET_I(25);
    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__y_reg = VL_RAND_RESET_I(25);
    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_reg = VL_RAND_RESET_I(25);
    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__new_x = VL_RAND_RESET_I(25);
    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__new_y = VL_RAND_RESET_I(25);
    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__new_angle = VL_RAND_RESET_I(25);
    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__dx = VL_RAND_RESET_I(25);
    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__dy = VL_RAND_RESET_I(25);
    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__sensor_x = VL_RAND_RESET_I(25);
    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__sensor_y = VL_RAND_RESET_I(25);
    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__trail_forward = VL_RAND_RESET_I(8);
    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__trail_left = VL_RAND_RESET_I(8);
    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__trail_right = VL_RAND_RESET_I(8);
    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__trig_angle_idx = VL_RAND_RESET_I(10);
    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__sin_val = VL_RAND_RESET_I(25);
    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__cos_val = VL_RAND_RESET_I(25);
    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_a = VL_RAND_RESET_I(25);
    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_b = VL_RAND_RESET_I(25);
    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__current_sense_angle = VL_RAND_RESET_I(25);
    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__unnamedblk1__DOT__sum_x = VL_RAND_RESET_I(25);
    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__unnamedblk1__DOT__sum_y = VL_RAND_RESET_I(25);
    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__unnamedblk1__DOT__wrapped_x = VL_RAND_RESET_I(25);
    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__unnamedblk1__DOT__wrapped_y = VL_RAND_RESET_I(25);
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__u_trig_lut__DOT__sin_rom[__Vi0] = VL_RAND_RESET_I(25);
    }
    for (int __Vi0 = 0; __Vi0 < 1024; ++__Vi0) {
        vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__u_trig_lut__DOT__cos_rom[__Vi0] = VL_RAND_RESET_I(25);
    }
    vlSelf->slime_top__DOT__u_coordinator__DOT__u_processor__DOT__u_mult__DOT__full_product = VL_RAND_RESET_Q(50);
    vlSelf->__Vtrigprevexpr___TOP__clk_100mhz__0 = VL_RAND_RESET_I(1);
    vlSelf->__Vtrigprevexpr___TOP__slime_top__DOT__clk_25mhz__0 = VL_RAND_RESET_I(1);
    for (int __Vi0 = 0; __Vi0 < 4; ++__Vi0) {
        vlSelf->__Vm_traceActivity[__Vi0] = 0;
    }
}
