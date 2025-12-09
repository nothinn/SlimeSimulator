// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Model implementation (design independent parts)

#include "Vslime_top__pch.h"
#include "verilated_vcd_c.h"

//============================================================
// Constructors

Vslime_top::Vslime_top(VerilatedContext* _vcontextp__, const char* _vcname__)
    : VerilatedModel{*_vcontextp__}
    , vlSymsp{new Vslime_top__Syms(contextp(), _vcname__, this)}
    , clk_100mhz{vlSymsp->TOP.clk_100mhz}
    , btnc{vlSymsp->TOP.btnc}
    , btnu{vlSymsp->TOP.btnu}
    , btnd{vlSymsp->TOP.btnd}
    , btnl{vlSymsp->TOP.btnl}
    , btnr{vlSymsp->TOP.btnr}
    , vga_r{vlSymsp->TOP.vga_r}
    , vga_g{vlSymsp->TOP.vga_g}
    , vga_b{vlSymsp->TOP.vga_b}
    , vga_hs{vlSymsp->TOP.vga_hs}
    , vga_vs{vlSymsp->TOP.vga_vs}
    , sim_start{vlSymsp->TOP.sim_start}
    , debug_agent_sel{vlSymsp->TOP.debug_agent_sel}
    , debug_agent_write_en{vlSymsp->TOP.debug_agent_write_en}
    , step_complete_pulse{vlSymsp->TOP.step_complete_pulse}
    , sw{vlSymsp->TOP.sw}
    , led{vlSymsp->TOP.led}
    , debug_agent_idx{vlSymsp->TOP.debug_agent_idx}
    , debug_trail_addr{vlSymsp->TOP.debug_trail_addr}
    , debug_trail_data{vlSymsp->TOP.debug_trail_data}
    , debug_agent_data{vlSymsp->TOP.debug_agent_data}
    , debug_agent_data_write{vlSymsp->TOP.debug_agent_data_write}
    , rootp{&(vlSymsp->TOP)}
{
    // Register model with the context
    contextp()->addModel(this);
}

Vslime_top::Vslime_top(const char* _vcname__)
    : Vslime_top(Verilated::threadContextp(), _vcname__)
{
}

//============================================================
// Destructor

Vslime_top::~Vslime_top() {
    delete vlSymsp;
}

//============================================================
// Evaluation function

#ifdef VL_DEBUG
void Vslime_top___024root___eval_debug_assertions(Vslime_top___024root* vlSelf);
#endif  // VL_DEBUG
void Vslime_top___024root___eval_static(Vslime_top___024root* vlSelf);
void Vslime_top___024root___eval_initial(Vslime_top___024root* vlSelf);
void Vslime_top___024root___eval_settle(Vslime_top___024root* vlSelf);
void Vslime_top___024root___eval(Vslime_top___024root* vlSelf);

void Vslime_top::eval_step() {
    VL_DEBUG_IF(VL_DBG_MSGF("+++++TOP Evaluate Vslime_top::eval_step\n"); );
#ifdef VL_DEBUG
    // Debug assertions
    Vslime_top___024root___eval_debug_assertions(&(vlSymsp->TOP));
#endif  // VL_DEBUG
    vlSymsp->__Vm_activity = true;
    vlSymsp->__Vm_deleter.deleteAll();
    if (VL_UNLIKELY(!vlSymsp->__Vm_didInit)) {
        vlSymsp->__Vm_didInit = true;
        VL_DEBUG_IF(VL_DBG_MSGF("+ Initial\n"););
        Vslime_top___024root___eval_static(&(vlSymsp->TOP));
        Vslime_top___024root___eval_initial(&(vlSymsp->TOP));
        Vslime_top___024root___eval_settle(&(vlSymsp->TOP));
    }
    VL_DEBUG_IF(VL_DBG_MSGF("+ Eval\n"););
    Vslime_top___024root___eval(&(vlSymsp->TOP));
    // Evaluate cleanup
    Verilated::endOfEval(vlSymsp->__Vm_evalMsgQp);
}

//============================================================
// Events and timing
bool Vslime_top::eventsPending() { return false; }

uint64_t Vslime_top::nextTimeSlot() {
    VL_FATAL_MT(__FILE__, __LINE__, "", "%Error: No delays in the design");
    return 0;
}

//============================================================
// Utilities

const char* Vslime_top::name() const {
    return vlSymsp->name();
}

//============================================================
// Invoke final blocks

void Vslime_top___024root___eval_final(Vslime_top___024root* vlSelf);

VL_ATTR_COLD void Vslime_top::final() {
    Vslime_top___024root___eval_final(&(vlSymsp->TOP));
}

//============================================================
// Implementations of abstract methods from VerilatedModel

const char* Vslime_top::hierName() const { return vlSymsp->name(); }
const char* Vslime_top::modelName() const { return "Vslime_top"; }
unsigned Vslime_top::threads() const { return 1; }
void Vslime_top::prepareClone() const { contextp()->prepareClone(); }
void Vslime_top::atClone() const {
    contextp()->threadPoolpOnClone();
}
std::unique_ptr<VerilatedTraceConfig> Vslime_top::traceConfig() const {
    return std::unique_ptr<VerilatedTraceConfig>{new VerilatedTraceConfig{false, false, false}};
};

//============================================================
// Trace configuration

void Vslime_top___024root__trace_decl_types(VerilatedVcd* tracep);

void Vslime_top___024root__trace_init_top(Vslime_top___024root* vlSelf, VerilatedVcd* tracep);

VL_ATTR_COLD static void trace_init(void* voidSelf, VerilatedVcd* tracep, uint32_t code) {
    // Callback from tracep->open()
    Vslime_top___024root* const __restrict vlSelf VL_ATTR_UNUSED = static_cast<Vslime_top___024root*>(voidSelf);
    Vslime_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    if (!vlSymsp->_vm_contextp__->calcUnusedSigs()) {
        VL_FATAL_MT(__FILE__, __LINE__, __FILE__,
            "Turning on wave traces requires Verilated::traceEverOn(true) call before time 0.");
    }
    vlSymsp->__Vm_baseCode = code;
    tracep->pushPrefix(std::string{vlSymsp->name()}, VerilatedTracePrefixType::SCOPE_MODULE);
    Vslime_top___024root__trace_decl_types(tracep);
    Vslime_top___024root__trace_init_top(vlSelf, tracep);
    tracep->popPrefix();
}

VL_ATTR_COLD void Vslime_top___024root__trace_register(Vslime_top___024root* vlSelf, VerilatedVcd* tracep);

VL_ATTR_COLD void Vslime_top::trace(VerilatedVcdC* tfp, int levels, int options) {
    if (tfp->isOpen()) {
        vl_fatal(__FILE__, __LINE__, __FILE__,"'Vslime_top::trace()' shall not be called after 'VerilatedVcdC::open()'.");
    }
    if (false && levels && options) {}  // Prevent unused
    tfp->spTrace()->addModel(this);
    tfp->spTrace()->addInitCb(&trace_init, &(vlSymsp->TOP));
    Vslime_top___024root__trace_register(&(vlSymsp->TOP), tfp->spTrace());
}
