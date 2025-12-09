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
.PHONY: test_lfsr test_fixed_point test_trig test_vga test_trail_map_ram test_trail_map_ram_pipeline0 test_trail_map_ram_pipeline1 test_trail_map_ram_pipeline2 test_rtl_vs_python test_trail_map test_all test_comparison test_fixed_point_comprehensive test_movement_calculation test_modules_vs_python test_modules_comprehensive test_2x_movement_bug clean_all

test_lfsr:
	$(MAKE) sim VERILOG_SOURCES="$(SRC_DIR)/lfsr.sv" MODULE=test_lfsr TOPLEVEL=lfsr

test_fixed_point:
	$(MAKE) sim VERILOG_SOURCES="$(SRC_DIR)/fixed_point_mult.sv" MODULE=test_fixed_point TOPLEVEL=fixed_point_mult

test_trig:
	$(MAKE) sim VERILOG_SOURCES="$(SRC_DIR)/trig_lut.sv" MODULE=test_trig_lut TOPLEVEL=trig_lut

test_vga:
	$(MAKE) sim VERILOG_SOURCES="$(SRC_DIR)/vga_controller.sv" MODULE=test_vga TOPLEVEL=vga_controller

# Trail map RAM tests with different pipeline configurations
test_trail_map_ram_pipeline0:
	$(MAKE) sim \
		VERILOG_SOURCES="$(SRC_DIR)/trail_map_ram.sv" \
		MODULE=test_trail_map_ram \
		TOPLEVEL=trail_map_ram \
		PLUSARGS="+WIDTH=320 +HEIGHT=240 +DATA_WIDTH=18 +PIPELINE_STAGES=0"

test_trail_map_ram_pipeline1:
	$(MAKE) sim \
		VERILOG_SOURCES="$(SRC_DIR)/trail_map_ram.sv" \
		MODULE=test_trail_map_ram \
		TOPLEVEL=trail_map_ram \
		PLUSARGS="+WIDTH=320 +HEIGHT=240 +DATA_WIDTH=18 +PIPELINE_STAGES=1"

test_trail_map_ram_pipeline2:
	$(MAKE) sim \
		VERILOG_SOURCES="$(SRC_DIR)/trail_map_ram.sv" \
		MODULE=test_trail_map_ram \
		TOPLEVEL=trail_map_ram \
		PLUSARGS="+WIDTH=320 +HEIGHT=240 +DATA_WIDTH=18 +PIPELINE_STAGES=2"

# Run all trail_map_ram tests
test_trail_map_ram: clean
	@echo "========================================="
	@echo "Testing trail_map_ram (pipeline=0)"
	@echo "========================================="
	$(MAKE) test_trail_map_ram_pipeline0
	$(MAKE) clean
	@echo ""
	@echo "========================================="
	@echo "Testing trail_map_ram (pipeline=1)"
	@echo "========================================="
	$(MAKE) test_trail_map_ram_pipeline1
	$(MAKE) clean
	@echo ""
	@echo "========================================="
	@echo "Testing trail_map_ram (pipeline=2)"
	@echo "========================================="
	$(MAKE) test_trail_map_ram_pipeline2
	@echo ""
	@echo "========================================="
	@echo "All trail_map_ram tests passed!"
	@echo "========================================="

test_fixed_point_comprehensive:
	$(MAKE) sim VERILOG_SOURCES="$(SRC_DIR)/fixed_point_mult.sv" MODULE=test_fixed_point_comprehensive TOPLEVEL=fixed_point_mult

test_movement_calculation:
	$(MAKE) sim \
		VERILOG_SOURCES="$(SRC_DIR)/fixed_point_mult.sv $(SRC_DIR)/trig_lut.sv $(SRC_DIR)/agent_processor.sv $(SRC_DIR)/lfsr.sv" \
		MODULE=test_movement_calculation \
		TOPLEVEL=agent_processor

test_trail_map:
	$(MAKE) sim \
		VERILOG_SOURCES="$(SRC_DIR)/agent_sim_tb.sv $(SRC_DIR)/agent_processor.sv $(SRC_DIR)/lfsr.sv $(SRC_DIR)/trig_lut.sv $(SRC_DIR)/fixed_point_mult.sv" \
		MODULE=test_trail_map \
		TOPLEVEL=agent_sim_tb

# New comprehensive comparison tests
test_trig_lut_vs_python:
	$(MAKE) sim \
		VERILOG_SOURCES="$(SRC_DIR)/trig_lut.sv" \
		MODULE=test_modules_vs_python \
		TOPLEVEL=trig_lut \
		TESTCASE=test_trig_lut_comprehensive,test_trig_lut_latency

test_fixed_point_mult_vs_python:
	$(MAKE) sim \
		VERILOG_SOURCES="$(SRC_DIR)/fixed_point_mult.sv" \
		MODULE=test_modules_vs_python \
		TOPLEVEL=fixed_point_mult \
		TESTCASE=test_fixed_point_mult_comprehensive,test_fixed_point_movement_calculation

test_agent_processor_vs_python:
	$(MAKE) sim \
		VERILOG_SOURCES="$(SRC_DIR)/agent_processor.sv $(SRC_DIR)/fixed_point_mult.sv $(SRC_DIR)/trig_lut.sv $(SRC_DIR)/lfsr.sv" \
		MODULE=test_modules_vs_python \
		TOPLEVEL=agent_processor \
		TESTCASE=test_agent_processor_initialization,test_agent_processor_trig_latency_compensation

# Run all module comparison tests
test_modules_comprehensive: clean
	@echo "========================================="
	@echo "Running comprehensive module vs Python tests"
	@echo "========================================="
	@echo "Test 1: Trig LUT comprehensive comparison"
	$(MAKE) test_trig_lut_vs_python
	$(MAKE) clean
	@echo "Test 2: Fixed-point multiplier comprehensive comparison"
	$(MAKE) test_fixed_point_mult_vs_python
	$(MAKE) clean
	@echo "Test 3: Agent processor vs Python"
	$(MAKE) test_agent_processor_vs_python
	@echo "========================================="
	@echo "All module comparison tests completed!"
	@echo "========================================="

test_all: clean
	$(MAKE) test_lfsr
	$(MAKE) clean
	$(MAKE) test_fixed_point
	$(MAKE) clean
	$(MAKE) test_trig
	$(MAKE) clean
	$(MAKE) test_vga
	$(MAKE) clean
	$(MAKE) test_trail_map_ram

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

# Run all comparison tests (both legacy and new comprehensive)
test_comparison: clean
	@echo "========================================="
	@echo "Running RTL vs Python comparison tests"
	@echo "========================================="
	@echo ""
	@echo "--- Legacy Comparison Tests ---"
	$(MAKE) test_rtl_vs_python_lfsr
	$(MAKE) clean
	$(MAKE) test_rtl_vs_python_fp
	$(MAKE) clean
	$(MAKE) test_rtl_vs_python_trig
	$(MAKE) clean
	@echo ""
	@echo "--- Comprehensive Module Tests ---"
	$(MAKE) test_modules_comprehensive
	@echo ""
	@echo "========================================="
	@echo "All comparison tests passed!"
	@echo "========================================="

# 2x Movement Bug Isolation Test
test_2x_movement_bug:
	@echo "========================================="
	@echo "Testing 2x Movement Scaling Bug"
	@echo "========================================="
	$(MAKE) sim \
		VERILOG_SOURCES="$(SRC_DIR)/agent_sim_tb.sv $(SRC_DIR)/agent_processor.sv $(SRC_DIR)/lfsr.sv $(SRC_DIR)/trig_lut.sv $(SRC_DIR)/fixed_point_mult.sv" \
		MODULE=test_2x_movement_bug \
		TOPLEVEL=agent_sim_tb \
		TESTCASE=test_2x_movement_right_direction,test_2x_movement_diagonal,test_movement_components_isolation

# Step-Based Control Test
test_step_control:
	@echo "========================================="
	@echo "Testing Step-Based Control"
	@echo "========================================="
	$(MAKE) sim \
		VERILOG_SOURCES="$(SRC_DIR)/step_test_tb.sv $(SRC_DIR)/step_controller.sv $(SRC_DIR)/agent_coordinator.sv $(SRC_DIR)/agent_processor.sv $(SRC_DIR)/lfsr.sv $(SRC_DIR)/trig_lut.sv $(SRC_DIR)/fixed_point_mult.sv" \
		MODULE=step_test \
		TOPLEVEL=step_test_tb \
		TESTCASE=test_step_controller_basic,test_step_controller_movement

clean_all: clean
	rm -rf __pycache__ results.xml *.vcd sim_build step_test_dumps step_test_dumps_movement
