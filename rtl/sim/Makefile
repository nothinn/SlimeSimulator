# Makefile for Slime Simulator RTL simulation
# Uses cocotb with Icarus Verilog

# Simulator
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# Source files directory
SRC_DIR = $(PWD)/../src

# Python path for importing slime_simulator
export PYTHONPATH := $(PWD)/../..:$(PYTHONPATH)

# Icarus Verilog specific settings
COMPILE_ARGS += -g2012
COMPILE_ARGS += -I$(SRC_DIR)

# Default test
MODULE ?= test_lfsr
TOPLEVEL ?= lfsr

# Include cocotb makefile
include $(shell cocotb-config --makefiles)/Makefile.sim

# Test targets
.PHONY: test_lfsr test_fixed_point test_trig test_vga test_all clean_all

test_lfsr: VERILOG_SOURCES = $(SRC_DIR)/lfsr.sv
test_lfsr: MODULE = test_lfsr
test_lfsr: TOPLEVEL = lfsr
test_lfsr:
	$(MAKE) sim

test_fixed_point: VERILOG_SOURCES = $(SRC_DIR)/fixed_point_mult.sv
test_fixed_point: MODULE = test_fixed_point
test_fixed_point: TOPLEVEL = fixed_point_mult
test_fixed_point:
	$(MAKE) sim

test_trig: VERILOG_SOURCES = $(SRC_DIR)/trig_lut.sv
test_trig: MODULE = test_trig_lut
test_trig: TOPLEVEL = trig_lut
test_trig:
	$(MAKE) sim

test_vga: VERILOG_SOURCES = $(SRC_DIR)/vga_controller.sv
test_vga: MODULE = test_vga
test_vga: TOPLEVEL = vga_controller
test_vga:
	$(MAKE) sim

test_all: clean
	$(MAKE) test_lfsr
	$(MAKE) clean
	$(MAKE) test_fixed_point
	$(MAKE) clean
	$(MAKE) test_trig
	$(MAKE) clean
	$(MAKE) test_vga

clean_all: clean
	rm -rf __pycache__ results.xml *.vcd sim_build
