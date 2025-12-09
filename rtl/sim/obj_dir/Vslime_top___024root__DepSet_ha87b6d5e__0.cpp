// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vslime_top.h for the primary calling header

#include "Vslime_top__pch.h"
#include "Vslime_top__Syms.h"
#include "Vslime_top___024root.h"

#ifdef VL_DEBUG
VL_ATTR_COLD void Vslime_top___024root___dump_triggers__ico(Vslime_top___024root* vlSelf);
#endif  // VL_DEBUG

void Vslime_top___024root___eval_triggers__ico(Vslime_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root___eval_triggers__ico\n"); );
    // Body
    vlSelf->__VicoTriggered.set(0U, (IData)(vlSelf->__VicoFirstIteration));
#ifdef VL_DEBUG
    if (VL_UNLIKELY(vlSymsp->_vm_contextp__->debug())) {
        Vslime_top___024root___dump_triggers__ico(vlSelf);
    }
#endif
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vslime_top___024root___dump_triggers__act(Vslime_top___024root* vlSelf);
#endif  // VL_DEBUG

void Vslime_top___024root___eval_triggers__act(Vslime_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vslime_top___024root___eval_triggers__act\n"); );
    // Body
    vlSelf->__VactTriggered.set(0U, ((IData)(vlSelf->clk_100mhz) 
                                     & (~ (IData)(vlSelf->__Vtrigprevexpr___TOP__clk_100mhz__0))));
    vlSelf->__VactTriggered.set(1U, ((IData)(vlSelf->slime_top__DOT__clk_25mhz) 
                                     & (~ (IData)(vlSelf->__Vtrigprevexpr___TOP__slime_top__DOT__clk_25mhz__0))));
    vlSelf->__Vtrigprevexpr___TOP__clk_100mhz__0 = vlSelf->clk_100mhz;
    vlSelf->__Vtrigprevexpr___TOP__slime_top__DOT__clk_25mhz__0 
        = vlSelf->slime_top__DOT__clk_25mhz;
#ifdef VL_DEBUG
    if (VL_UNLIKELY(vlSymsp->_vm_contextp__->debug())) {
        Vslime_top___024root___dump_triggers__act(vlSelf);
    }
#endif
}
