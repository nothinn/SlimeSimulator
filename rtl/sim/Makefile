# Makefile for Slime Simulator RTL simulation
# Uses cocotb with Verilator

# Simulator
SIM ?= verilator
TOPLEVEL_LANG ?= verilog

# Source files
VERILOG_SOURCES = $(PWD)/../src/lfsr.sv
VERILOG_SOURCES += $(PWD)/../src/fixed_point_mult.sv
VERILOG_SOURCES += $(PWD)/../src/trig_lut.sv
VERILOG_SOURCES += $(PWD)/../src/debouncer.sv
VERILOG_SOURCES += $(PWD)/../src/vga_controller.sv
VERILOG_SOURCES += $(PWD)/../src/agent_processor.sv
VERILOG_SOURCES += $(PWD)/../src/slime_top.sv

# Verilator specific settings
EXTRA_ARGS += --trace --trace-structs
EXTRA_ARGS += -Wno-WIDTHEXPAND -Wno-WIDTHTRUNC -Wno-UNUSEDSIGNAL
EXTRA_ARGS += -Wno-UNOPTFLAT -Wno-INITIALDLY

# Python path for importing slime_simulator
export PYTHONPATH := $(PWD)/../..:$(PYTHONPATH)

# Default test module
MODULE ?= test_lfsr

# Include cocotb makefile
include $(shell cocotb-config --makefiles)/Makefile.sim

# Test targets
.PHONY: test_lfsr test_all clean_all

test_lfsr:
	$(MAKE) MODULE=test_lfsr TOPLEVEL=lfsr

test_vga:
	$(MAKE) MODULE=test_vga TOPLEVEL=vga_controller

test_all: test_lfsr

clean_all: clean
	rm -rf __pycache__ results.xml *.vcd

# Lint target (Verilator lint only)
lint:
	verilator --lint-only -Wall $(VERILOG_SOURCES)
