// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design internal header
// See Vslime_top.h for the primary calling header

#ifndef VERILATED_VSLIME_TOP___024ROOT_H_
#define VERILATED_VSLIME_TOP___024ROOT_H_  // guard

#include "verilated.h"


class Vslime_top__Syms;

class alignas(VL_CACHE_LINE_BYTES) Vslime_top___024root final : public VerilatedModule {
  public:

    // DESIGN SPECIFIC STATE
    // Anonymous structures to workaround compiler member-count bugs
    struct {
        VL_IN8(clk_100mhz,0,0);
        CData/*0:0*/ slime_top__DOT__clk_25mhz;
        VL_IN8(btnc,0,0);
        VL_IN8(btnu,0,0);
        VL_IN8(btnd,0,0);
        VL_IN8(btnl,0,0);
        VL_IN8(btnr,0,0);
        VL_OUT8(vga_r,3,0);
        VL_OUT8(vga_g,3,0);
        VL_OUT8(vga_b,3,0);
        VL_OUT8(vga_hs,0,0);
        VL_OUT8(vga_vs,0,0);
        VL_IN8(sim_start,0,0);
        VL_IN8(debug_agent_sel,1,0);
        VL_IN8(debug_agent_write_en,0,0);
        VL_OUT8(step_complete_pulse,0,0);
        CData/*1:0*/ slime_top__DOT__clk_div;
        CData/*0:0*/ slime_top__DOT__btn_start;
        CData/*0:0*/ slime_top__DOT__btn_random;
        CData/*3:0*/ slime_top__DOT__speed_level;
        CData/*0:0*/ slime_top__DOT__lfsr_enable;
        CData/*0:0*/ slime_top__DOT__lfsr_load;
        CData/*0:0*/ slime_top__DOT__trail_we_b;
        CData/*0:0*/ slime_top__DOT__pixel_valid;
        CData/*0:0*/ slime_top__DOT__frame_start;
        CData/*3:0*/ slime_top__DOT__sim_state;
        CData/*0:0*/ slime_top__DOT__sim_running;
        CData/*0:0*/ slime_top__DOT__pattern_trail_we;
        CData/*7:0*/ slime_top__DOT__sim_trail_data;
        CData/*0:0*/ slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_sync_0;
        CData/*0:0*/ slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_sync_1;
        CData/*0:0*/ slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_stable;
        CData/*0:0*/ slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__btn_stable_prev;
        CData/*0:0*/ slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_sync_0;
        CData/*0:0*/ slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_sync_1;
        CData/*0:0*/ slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable;
        CData/*0:0*/ slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__btn_stable_prev;
        CData/*0:0*/ slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_sync_0;
        CData/*0:0*/ slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_sync_1;
        CData/*0:0*/ slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable;
        CData/*0:0*/ slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__btn_stable_prev;
        CData/*0:0*/ slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_sync_0;
        CData/*0:0*/ slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_sync_1;
        CData/*0:0*/ slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_stable;
        CData/*0:0*/ slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__btn_stable_prev;
        CData/*0:0*/ slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_sync_0;
        CData/*0:0*/ slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_sync_1;
        CData/*0:0*/ slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_stable;
        CData/*0:0*/ slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__btn_stable_prev;
        CData/*0:0*/ slime_top__DOT__u_lfsr__DOT__valid;
        CData/*0:0*/ slime_top__DOT__u_lfsr__DOT__feedback;
        CData/*2:0*/ slime_top__DOT__u_coordinator__DOT__state;
        CData/*2:0*/ slime_top__DOT__u_coordinator__DOT__next_state;
        CData/*3:0*/ slime_top__DOT__u_coordinator__DOT__current_agent_idx;
        CData/*0:0*/ slime_top__DOT__u_coordinator__DOT__proc_start;
        CData/*0:0*/ slime_top__DOT__u_coordinator__DOT__latched_valid;
        CData/*3:0*/ slime_top__DOT__u_coordinator__DOT__prev_idx;
        CData/*0:0*/ slime_top__DOT__u_coordinator__DOT__step_just_completed;
        CData/*0:0*/ slime_top__DOT__u_coordinator__DOT__step_freeze_cycle;
        CData/*0:0*/ slime_top__DOT__u_coordinator__DOT__step_writeback_cycle;
        CData/*3:0*/ slime_top__DOT__u_coordinator__DOT__debug_idx_safe;
        CData/*4:0*/ slime_top__DOT__u_coordinator__DOT__u_processor__DOT__state;
        CData/*4:0*/ slime_top__DOT__u_coordinator__DOT__u_processor__DOT__next_state;
        CData/*7:0*/ slime_top__DOT__u_coordinator__DOT__u_processor__DOT__trail_forward;
    };
    struct {
        CData/*7:0*/ slime_top__DOT__u_coordinator__DOT__u_processor__DOT__trail_left;
        CData/*7:0*/ slime_top__DOT__u_coordinator__DOT__u_processor__DOT__trail_right;
        CData/*0:0*/ __VstlFirstIteration;
        CData/*0:0*/ __VicoFirstIteration;
        CData/*0:0*/ __Vtrigprevexpr___TOP__clk_100mhz__0;
        CData/*0:0*/ __Vtrigprevexpr___TOP__slime_top__DOT__clk_25mhz__0;
        CData/*0:0*/ __VactContinue;
        VL_IN16(sw,15,0);
        VL_OUT16(led,15,0);
        VL_IN16(debug_agent_idx,9,0);
        SData/*9:0*/ slime_top__DOT__u_vga__DOT__h_count;
        SData/*9:0*/ slime_top__DOT__u_vga__DOT__v_count;
        SData/*9:0*/ slime_top__DOT__u_coordinator__DOT__proc_trail_read_x;
        SData/*9:0*/ slime_top__DOT__u_coordinator__DOT__proc_trail_write_x;
        SData/*8:0*/ slime_top__DOT__u_coordinator__DOT__proc_trail_read_y;
        SData/*8:0*/ slime_top__DOT__u_coordinator__DOT__proc_trail_write_y;
        SData/*9:0*/ slime_top__DOT__u_coordinator__DOT__u_processor__DOT__trig_angle_idx;
        VL_IN(debug_trail_addr,18,0);
        VL_OUT(debug_trail_data,17,0);
        VL_OUT(debug_agent_data,24,0);
        VL_IN(debug_agent_data_write,24,0);
        IData/*31:0*/ slime_top__DOT__lfsr_seed;
        IData/*18:0*/ slime_top__DOT__trail_addr_a;
        IData/*18:0*/ slime_top__DOT__trail_addr_b;
        IData/*17:0*/ slime_top__DOT__trail_data_b_in;
        IData/*31:0*/ slime_top__DOT__frame_count;
        IData/*16:0*/ slime_top__DOT__agent_idx;
        IData/*17:0*/ slime_top__DOT__trail_val_before_decay;
        IData/*17:0*/ slime_top__DOT__trail_val_decayed;
        IData/*17:0*/ slime_top__DOT__orch_trail_read_data;
        IData/*18:0*/ slime_top__DOT__sim_trail_addr;
        IData/*20:0*/ slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__0__KET____DOT__u_debouncer__DOT__counter;
        IData/*20:0*/ slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__1__KET____DOT__u_debouncer__DOT__counter;
        IData/*20:0*/ slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__2__KET____DOT__u_debouncer__DOT__counter;
        IData/*20:0*/ slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__3__KET____DOT__u_debouncer__DOT__counter;
        IData/*20:0*/ slime_top__DOT__u_debouncer__DOT__gen_debouncer__BRA__4__KET____DOT__u_debouncer__DOT__counter;
        IData/*31:0*/ slime_top__DOT__u_lfsr__DOT__lfsr_reg;
        IData/*17:0*/ slime_top__DOT__u_trail_ram__DOT__mem_out_a;
        IData/*17:0*/ slime_top__DOT__u_trail_ram__DOT__mem_out_b;
        IData/*31:0*/ slime_top__DOT__u_trail_ram__DOT__unnamedblk1__DOT__i;
        IData/*17:0*/ slime_top__DOT__u_trail_ram__DOT____Vlvbound_hf71990d5__0;
        IData/*17:0*/ slime_top__DOT__u_trail_ram__DOT____Vlvbound_h51f3e5a2__0;
        IData/*31:0*/ slime_top__DOT__u_coordinator__DOT__step_counter;
        IData/*24:0*/ slime_top__DOT__u_coordinator__DOT__latched_x_out;
        IData/*24:0*/ slime_top__DOT__u_coordinator__DOT__latched_y_out;
        IData/*24:0*/ slime_top__DOT__u_coordinator__DOT__latched_angle_out;
        IData/*31:0*/ slime_top__DOT__u_coordinator__DOT__unnamedblk1__DOT__i;
        IData/*24:0*/ slime_top__DOT__u_coordinator__DOT____Vlvbound_h1f94e32a__0;
        IData/*24:0*/ slime_top__DOT__u_coordinator__DOT____Vlvbound_hcb92b3ef__0;
        IData/*24:0*/ slime_top__DOT__u_coordinator__DOT____Vlvbound_hd63147c5__0;
        IData/*24:0*/ slime_top__DOT__u_coordinator__DOT____Vlvbound_h1f94e32a__1;
        IData/*24:0*/ slime_top__DOT__u_coordinator__DOT____Vlvbound_hcb92b3ef__1;
        IData/*24:0*/ slime_top__DOT__u_coordinator__DOT____Vlvbound_hd63147c5__1;
        IData/*24:0*/ slime_top__DOT__u_coordinator__DOT____Vlvbound_h1f94e32a__2;
        IData/*24:0*/ slime_top__DOT__u_coordinator__DOT____Vlvbound_hcb92b3ef__2;
        IData/*24:0*/ slime_top__DOT__u_coordinator__DOT____Vlvbound_hd63147c5__2;
        IData/*24:0*/ slime_top__DOT__u_coordinator__DOT____Vlvbound_h2b5da6a3__0;
        IData/*24:0*/ slime_top__DOT__u_coordinator__DOT____Vlvbound_haf1b776c__0;
        IData/*24:0*/ slime_top__DOT__u_coordinator__DOT____Vlvbound_hd9a9fc40__0;
        IData/*24:0*/ slime_top__DOT__u_coordinator__DOT__u_processor__DOT__x_reg;
        IData/*24:0*/ slime_top__DOT__u_coordinator__DOT__u_processor__DOT__y_reg;
        IData/*24:0*/ slime_top__DOT__u_coordinator__DOT__u_processor__DOT__angle_reg;
        IData/*24:0*/ slime_top__DOT__u_coordinator__DOT__u_processor__DOT__new_x;
        IData/*24:0*/ slime_top__DOT__u_coordinator__DOT__u_processor__DOT__new_y;
    };
    struct {
        IData/*24:0*/ slime_top__DOT__u_coordinator__DOT__u_processor__DOT__new_angle;
        IData/*24:0*/ slime_top__DOT__u_coordinator__DOT__u_processor__DOT__dx;
        IData/*24:0*/ slime_top__DOT__u_coordinator__DOT__u_processor__DOT__dy;
        IData/*24:0*/ slime_top__DOT__u_coordinator__DOT__u_processor__DOT__sensor_x;
        IData/*24:0*/ slime_top__DOT__u_coordinator__DOT__u_processor__DOT__sensor_y;
        IData/*24:0*/ slime_top__DOT__u_coordinator__DOT__u_processor__DOT__sin_val;
        IData/*24:0*/ slime_top__DOT__u_coordinator__DOT__u_processor__DOT__cos_val;
        IData/*24:0*/ slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_a;
        IData/*24:0*/ slime_top__DOT__u_coordinator__DOT__u_processor__DOT__mult_b;
        IData/*24:0*/ slime_top__DOT__u_coordinator__DOT__u_processor__DOT__current_sense_angle;
        IData/*24:0*/ slime_top__DOT__u_coordinator__DOT__u_processor__DOT__unnamedblk1__DOT__sum_x;
        IData/*24:0*/ slime_top__DOT__u_coordinator__DOT__u_processor__DOT__unnamedblk1__DOT__sum_y;
        IData/*24:0*/ slime_top__DOT__u_coordinator__DOT__u_processor__DOT__unnamedblk1__DOT__wrapped_x;
        IData/*24:0*/ slime_top__DOT__u_coordinator__DOT__u_processor__DOT__unnamedblk1__DOT__wrapped_y;
        IData/*31:0*/ __VactIterCount;
        QData/*35:0*/ slime_top__DOT__trail_val_after_mult;
        QData/*49:0*/ slime_top__DOT__u_coordinator__DOT__u_processor__DOT__u_mult__DOT__full_product;
        VlUnpacked<IData/*17:0*/, 76800> slime_top__DOT__u_trail_ram__DOT__mem;
        VlUnpacked<IData/*17:0*/, 2> slime_top__DOT__u_trail_ram__DOT__pipe_a;
        VlUnpacked<IData/*17:0*/, 2> slime_top__DOT__u_trail_ram__DOT__pipe_b;
        VlUnpacked<IData/*24:0*/, 10> slime_top__DOT__u_coordinator__DOT__agent_x;
        VlUnpacked<IData/*24:0*/, 10> slime_top__DOT__u_coordinator__DOT__agent_y;
        VlUnpacked<IData/*24:0*/, 10> slime_top__DOT__u_coordinator__DOT__agent_angle;
        VlUnpacked<IData/*24:0*/, 1024> slime_top__DOT__u_coordinator__DOT__u_processor__DOT__u_trig_lut__DOT__sin_rom;
        VlUnpacked<IData/*24:0*/, 1024> slime_top__DOT__u_coordinator__DOT__u_processor__DOT__u_trig_lut__DOT__cos_rom;
        VlUnpacked<CData/*0:0*/, 4> __Vm_traceActivity;
    };
    VlTriggerVec<1> __VstlTriggered;
    VlTriggerVec<1> __VicoTriggered;
    VlTriggerVec<2> __VactTriggered;
    VlTriggerVec<2> __VnbaTriggered;

    // INTERNAL VARIABLES
    Vslime_top__Syms* const vlSymsp;

    // CONSTRUCTORS
    Vslime_top___024root(Vslime_top__Syms* symsp, const char* v__name);
    ~Vslime_top___024root();
    VL_UNCOPYABLE(Vslime_top___024root);

    // INTERNAL METHODS
    void __Vconfigure(bool first);
};


#endif  // guard
