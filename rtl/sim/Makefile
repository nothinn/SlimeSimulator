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
.PHONY: test_lfsr test_fixed_point test_trig test_vga test_rtl_vs_python test_trail_map test_all test_comparison clean_all

test_lfsr:
	$(MAKE) sim VERILOG_SOURCES="$(SRC_DIR)/lfsr.sv" MODULE=test_lfsr TOPLEVEL=lfsr

test_fixed_point:
	$(MAKE) sim VERILOG_SOURCES="$(SRC_DIR)/fixed_point_mult.sv" MODULE=test_fixed_point TOPLEVEL=fixed_point_mult

test_trig:
	$(MAKE) sim VERILOG_SOURCES="$(SRC_DIR)/trig_lut.sv" MODULE=test_trig_lut TOPLEVEL=trig_lut

test_vga:
	$(MAKE) sim VERILOG_SOURCES="$(SRC_DIR)/vga_controller.sv" MODULE=test_vga TOPLEVEL=vga_controller

test_trail_map:
	$(MAKE) sim \
		VERILOG_SOURCES="$(SRC_DIR)/agent_sim_tb.sv $(SRC_DIR)/agent_processor.sv $(SRC_DIR)/lfsr.sv $(SRC_DIR)/trig_lut.sv $(SRC_DIR)/fixed_point_mult.sv" \
		MODULE=test_trail_map \
		TOPLEVEL=agent_sim_tb

test_all: clean
	$(MAKE) test_lfsr
	$(MAKE) clean
	$(MAKE) test_fixed_point
	$(MAKE) clean
	$(MAKE) test_trig
	$(MAKE) clean
	$(MAKE) test_vga

# RTL vs Python comparison tests (run individual modules against Python reference)
test_rtl_vs_python_lfsr:
	$(MAKE) sim \
		VERILOG_SOURCES="$(SRC_DIR)/lfsr.sv" \
		MODULE=test_rtl_vs_python \
		TOPLEVEL=lfsr \
		TESTCASE=test_lfsr_sequence_extended,test_lfsr_statistics

test_rtl_vs_python_fp:
	$(MAKE) sim \
		VERILOG_SOURCES="$(SRC_DIR)/fixed_point_mult.sv" \
		MODULE=test_rtl_vs_python \
		TOPLEVEL=fixed_point_mult \
		TESTCASE=test_fixed_point_multiply_comprehensive

test_rtl_vs_python_trig:
	$(MAKE) sim \
		VERILOG_SOURCES="$(SRC_DIR)/trig_lut.sv" \
		MODULE=test_rtl_vs_python \
		TOPLEVEL=trig_lut \
		TESTCASE=test_trig_lut_full_table

# Run all comparison tests
test_comparison: clean
	@echo "========================================="
	@echo "Running RTL vs Python comparison tests"
	@echo "========================================="
	$(MAKE) test_rtl_vs_python_lfsr
	$(MAKE) clean
	$(MAKE) test_rtl_vs_python_fp
	$(MAKE) clean
	$(MAKE) test_rtl_vs_python_trig
	@echo "========================================="
	@echo "All comparison tests passed!"
	@echo "========================================="

clean_all: clean
	rm -rf __pycache__ results.xml *.vcd sim_build
