cmake_minimum_required(VERSION 3.12)
project(slime_sim_verilator)

# Find Verilator
find_program(VERILATOR verilator)
if (NOT VERILATOR)
    message(FATAL_ERROR "Verilator not found!")
endif()

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# RTL source files
set(RTL_SOURCES
    ../src/slime_top.sv
    ../src/agent_processor.sv
    ../src/lfsr.sv
    ../src/fixed_point_mult.sv
    ../src/trig_lut.sv
    ../src/debouncer.sv
    ../src/vga_controller.sv
)

# Testbench sources
set(TB_SOURCES
    slime_top_tb.cpp
)

# Generate Verilator C++ module
add_custom_command(
    OUTPUT
        ${CMAKE_BINARY_DIR}/Vslime_top.mk
        ${CMAKE_BINARY_DIR}/Vslime_top.h
        ${CMAKE_BINARY_DIR}/Vslime_top__Dpi.h
        ${CMAKE_BINARY_DIR}/Vslime_top__Dpi.cpp
        ${CMAKE_BINARY_DIR}/Vslime_top.cpp
    COMMAND
        ${VERILATOR}
        --cc
        --trace
        --build
        -j 4
        --top-module slime_top
        -O3
        ${RTL_SOURCES}
        --Mdir ${CMAKE_BINARY_DIR}
        -I${CMAKE_SOURCE_DIR}/../src
    DEPENDS ${RTL_SOURCES}
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
)

# Create executable
add_executable(slime_sim
    ${TB_SOURCES}
    ${CMAKE_BINARY_DIR}/Vslime_top.cpp
    ${CMAKE_BINARY_DIR}/Vslime_top__Dpi.cpp
)

# Link against Verilated libraries
target_link_libraries(slime_sim PRIVATE
    verilated
    verilated_vcd
)

# Include directories
target_include_directories(slime_sim PRIVATE
    ${CMAKE_BINARY_DIR}
    ${CMAKE_SOURCE_DIR}/../src
)

# Set output directory
set_target_properties(slime_sim PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/bin"
)
