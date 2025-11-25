# Validate Debug Infrastructure Setup
# This script checks that all debug cores are properly instantiated and accessible
#
# Usage:
#   vivado -mode batch -source rtl/scripts/validate_debug_setup.tcl
#
# Prerequisites:
#   - FPGA must be connected via USB
#   - Debug-enabled bitstream must be programmed

puts "============================================"
puts "Debug Infrastructure Validation"
puts "============================================"

# Connect to hardware
puts "\n[1/6] Connecting to hardware..."
open_hw_manager
connect_hw_server

if {[catch {open_hw_target}]} {
    puts "ERROR: Could not open hardware target!"
    puts "Make sure:"
    puts "  - Basys3 board is connected via USB"
    puts "  - Board power is ON"
    puts "  - Vivado drivers are installed"
    exit 1
}

puts "  Connected successfully!"

# Check for programmed device
puts "\n[2/6] Checking FPGA programming..."
set hw_device [lindex [get_hw_devices] 0]
current_hw_device $hw_device

if {![get_property PROGRAM.DONE [get_hw_device]]} {
    puts "WARNING: FPGA is not programmed!"
    puts "Programming with debug bitstream..."

    set bitstream "vivado_project_debug/slime_simulator_debug.runs/impl_1/slime_top.bit"
    if {![file exists $bitstream]} {
        puts "ERROR: Debug bitstream not found at: $bitstream"
        puts "Build it first with: vivado -mode batch -source rtl/build_with_debug.tcl"
        exit 1
    }

    set_property PROGRAM.FILE $bitstream [get_hw_device]
    program_hw_devices [get_hw_device]
    refresh_hw_device [get_hw_device]
}

puts "  FPGA is programmed!"

# Check for debug hub
puts "\n[3/6] Checking debug hub..."
if {[llength [get_hw_devices]] == 0} {
    puts "ERROR: No debug hub found!"
    puts "The bitstream may not have debug cores integrated."
    exit 1
}

puts "  Debug hub found!"

# Check for ILA
puts "\n[4/6] Checking ILA (Integrated Logic Analyzer)..."
set ila_cores [get_hw_ilas]
if {[llength $ila_cores] == 0} {
    puts "ERROR: No ILA cores found!"
    exit 1
}

puts "  Found [llength $ila_cores] ILA core(s):"
foreach ila $ila_cores {
    puts "    - $ila"
    set probes [get_hw_probes -of_objects $ila]
    puts "      Probes: [llength $probes]"

    # List first 5 probes
    set count 0
    foreach probe [lrange $probes 0 4] {
        set name [get_property NAME $probe]
        set width [get_property BIT_WIDTH $probe]
        puts "        [$count] $name \[${width}:0\]"
        incr count
    }
    if {[llength $probes] > 5} {
        puts "        ... and [expr {[llength $probes] - 5}] more"
    }
}

# Check for VIO
puts "\n[5/6] Checking VIO (Virtual I/O)..."
set vio_cores [get_hw_vios]
if {[llength $vio_cores] == 0} {
    puts "ERROR: No VIO cores found!"
    exit 1
}

puts "  Found [llength $vio_cores] VIO core(s):"
foreach vio $vio_cores {
    puts "    - $vio"

    # Count input/output probes
    set in_probes [get_hw_probes -of_objects $vio -filter {DIRECTION == "IN"}]
    set out_probes [get_hw_probes -of_objects $vio -filter {DIRECTION == "OUT"}]

    puts "      Input probes:  [llength $in_probes]"
    puts "      Output probes: [llength $out_probes]"

    # Test reading a value
    if {[llength $in_probes] > 0} {
        set test_probe [lindex $in_probes 0]
        set name [get_property NAME $test_probe]
        set value [get_property INPUT_VALUE $test_probe]
        puts "      Sample read: $name = $value"
    }
}

# Check for JTAG-to-AXI
puts "\n[6/6] Checking JTAG-to-AXI Master..."
set axi_cores [get_hw_axis]
if {[llength $axi_cores] == 0} {
    puts "WARNING: No JTAG-to-AXI cores found!"
    puts "Memory access will not be available."
} else {
    puts "  Found [llength $axi_cores] JTAG-to-AXI core(s):"
    foreach axi $axi_cores {
        puts "    - $axi"

        # Test a simple read transaction
        puts "      Testing memory read..."
        if {[catch {
            create_hw_axi_txn test_read $axi -address 0x0000 -len 1 -type read
            run_hw_axi test_read
            set data [get_property DATA [get_hw_axi_txns test_read]]
            puts "      Memory[0x0000] = $data"
        } err]} {
            puts "      WARNING: Test read failed: $err"
        }
    }
}

# Functional test - read frame counter
puts "\n============================================"
puts "Functional Tests"
puts "============================================"

puts "\n[Test 1] VIO Frame Counter Test..."
if {[llength $vio_cores] > 0} {
    set vio [lindex $vio_cores 0]

    # Try to find frame_count probe
    set frame_probe ""
    foreach probe [get_hw_probes -of_objects $vio] {
        if {[string match "*frame_count*" [get_property NAME $probe]]} {
            set frame_probe $probe
            break
        }
    }

    if {$frame_probe != ""} {
        set fc1 [get_property INPUT_VALUE $frame_probe]
        puts "  Frame count (t=0):    $fc1"

        after 1000
        refresh_hw_vio $vio

        set fc2 [get_property INPUT_VALUE $frame_probe]
        puts "  Frame count (t=1s):   $fc2"

        set diff [expr {$fc2 - $fc1}]
        puts "  Frames in 1 second:   $diff"

        if {$diff >= 55 && $diff <= 65} {
            puts "  Result: PASS (expected ~60 fps)"
        } else {
            puts "  Result: FAIL (expected ~60 fps, got $diff)"
        }
    } else {
        puts "  WARNING: frame_count probe not found"
    }
} else {
    puts "  SKIPPED: No VIO cores"
}

puts "\n[Test 2] ILA Capture Test..."
if {[llength $ila_cores] > 0} {
    set ila [lindex $ila_cores 0]

    puts "  Setting up immediate trigger..."
    set_property CONTROL.TRIGGER_MODE BASIC [get_hw_ilas $ila]
    set_property CONTROL.TRIGGER_POSITION 512 [get_hw_ilas $ila]

    puts "  Arming ILA..."
    run_hw_ila $ila

    puts "  Waiting for capture..."
    if {[catch {wait_on_hw_ila -timeout 5 $ila} err]} {
        puts "  Result: TIMEOUT - ILA did not trigger"
        puts "  This may be normal if the clock is not running"
    } else {
        puts "  Result: PASS - ILA captured successfully"

        # Try to read some samples
        set waveform [upload_hw_ila_data $ila]
        puts "  Captured waveform: $waveform"
    }
} else {
    puts "  SKIPPED: No ILA cores"
}

puts "\n[Test 3] Memory Access Test..."
if {[llength $axi_cores] > 0} {
    set axi [lindex $axi_cores 0]

    puts "  Reading memory locations..."

    # Read first 10 memory locations
    set success 0
    set fail 0

    for {set addr 0} {$addr < 10} {incr addr} {
        if {[catch {
            create_hw_axi_txn read_test_${addr} $axi \
                -address $addr -len 1 -type read
            run_hw_axi read_test_${addr}
            set data [get_property DATA [get_hw_axi_txns read_test_${addr}]]
            incr success
        } err]} {
            incr fail
        }
    }

    puts "  Successful reads: $success/10"
    puts "  Failed reads:     $fail/10"

    if {$success >= 8} {
        puts "  Result: PASS"
    } else {
        puts "  Result: FAIL"
    }
} else {
    puts "  SKIPPED: No JTAG-to-AXI cores"
}

# Summary
puts "\n============================================"
puts "Validation Summary"
puts "============================================"

set total_cores [expr {[llength $ila_cores] + [llength $vio_cores] + [llength $axi_cores]}]

puts "\nDebug Cores Found:"
puts "  ILA:          [llength $ila_cores]"
puts "  VIO:          [llength $vio_cores]"
puts "  JTAG-to-AXI:  [llength $axi_cores]"
puts "  Total:        $total_cores"

if {[llength $ila_cores] > 0 && [llength $vio_cores] > 0} {
    puts "\nResult: PASS - Debug infrastructure is operational"
    puts "\nNext Steps:"
    puts "  1. Use ILA to capture waveforms"
    puts "  2. Use VIO to monitor/control design"
    if {[llength $axi_cores] > 0} {
        puts "  3. Use JTAG-to-AXI to access memory"
    }
    puts "\nSee DEBUG_INFRASTRUCTURE.md for detailed usage"
} else {
    puts "\nResult: FAIL - Debug infrastructure is incomplete"
    puts "\nTroubleshooting:"
    puts "  - Rebuild with: vivado -mode batch -source rtl/build_with_debug.tcl"
    puts "  - Check that mark_debug attributes are in slime_top.sv"
    puts "  - Verify integrate_debug_cores.tcl ran successfully"
}

puts "\n============================================"

# Cleanup
close_hw_target
disconnect_hw_server
close_hw_manager
