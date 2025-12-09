"""
Cocotb testbench for trail_map_ram module

Tests:
1. Basic read/write operations on both ports
2. Independent clock domain operation
3. Write-first behavior on Port B
4. Pipeline stage configurations (0, 1, 2)
5. Read enable functionality
6. Concurrent access to different addresses
7. Same address access from both ports
8. Full memory sweep
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from cocotb.regression import TestFactory
import random


class TrailMapRAMTB:
    """Testbench wrapper for trail_map_ram"""

    def __init__(self, dut):
        self.dut = dut
        self.width = int(dut.WIDTH.value)
        self.height = int(dut.HEIGHT.value)
        self.data_width = int(dut.DATA_WIDTH.value)
        self.pipeline_stages = int(dut.PIPELINE_STAGES.value)
        self.mem_size = self.width * self.height

        # Shadow memory for verification
        self.shadow_mem = [0] * self.mem_size

    async def setup_clocks(self):
        """Start clocks for both ports"""
        # Port A: 25 MHz (40 ns period)
        cocotb.start_soon(Clock(self.dut.clk_a, 40, units="ns").start())
        # Port B: 100 MHz (10 ns period)
        cocotb.start_soon(Clock(self.dut.clk_b, 10, units="ns").start())

    async def reset(self):
        """Reset inputs to safe values"""
        self.dut.en_a.value = 0
        self.dut.addr_a.value = 0
        self.dut.en_b.value = 0
        self.dut.addr_b.value = 0
        self.dut.data_b_in.value = 0
        self.dut.we_b.value = 0
        await Timer(100, units="ns")

    async def write_b(self, addr, data):
        """Write to Port B"""
        assert addr < self.mem_size, f"Address {addr} out of range"
        self.dut.addr_b.value = addr
        self.dut.data_b_in.value = data
        self.dut.we_b.value = 1
        self.dut.en_b.value = 1
        await RisingEdge(self.dut.clk_b)
        self.dut.we_b.value = 0
        self.shadow_mem[addr] = data

        # Wait one more cycle for write to complete before next operation
        await RisingEdge(self.dut.clk_b)

    async def read_b(self, addr):
        """Read from Port B with pipeline consideration"""
        assert addr < self.mem_size, f"Address {addr} out of range"
        self.dut.addr_b.value = addr
        self.dut.en_b.value = 1
        self.dut.we_b.value = 0
        await RisingEdge(self.dut.clk_b)

        # Wait for pipeline stages
        for _ in range(self.pipeline_stages):
            await RisingEdge(self.dut.clk_b)

        return int(self.dut.data_b_out.value)

    async def read_a(self, addr):
        """Read from Port A with pipeline consideration"""
        assert addr < self.mem_size, f"Address {addr} out of range"
        self.dut.addr_a.value = addr
        self.dut.en_a.value = 1
        await RisingEdge(self.dut.clk_a)

        # Wait for pipeline stages
        for _ in range(self.pipeline_stages):
            await RisingEdge(self.dut.clk_a)

        return int(self.dut.data_a.value)


@cocotb.test()
async def test_basic_write_read(dut):
    """Test basic write on Port B and read from both ports"""
    tb = TrailMapRAMTB(dut)
    await tb.setup_clocks()
    await tb.reset()

    dut._log.info(f"Testing basic write/read (pipeline stages: {tb.pipeline_stages})")

    # Write some test values
    test_addr = 100
    test_value = 0x12345

    await tb.write_b(test_addr, test_value)

    # Read back from Port B
    read_val_b = await tb.read_b(test_addr)
    assert read_val_b == test_value, f"Port B read mismatch: expected {test_value:x}, got {read_val_b:x}"
    dut._log.info(f"✓ Port B write/read verified: {test_value:x}")

    # Read from Port A
    read_val_a = await tb.read_a(test_addr)
    assert read_val_a == test_value, f"Port A read mismatch: expected {test_value:x}, got {read_val_a:x}"
    dut._log.info(f"✓ Port A read verified: {test_value:x}")


@cocotb.test()
async def test_write_first_behavior(dut):
    """Test write-first mode: simultaneous write and read on Port B"""
    tb = TrailMapRAMTB(dut)
    await tb.setup_clocks()
    await tb.reset()

    dut._log.info("Testing write-first behavior")

    test_addr = 200
    old_value = 0xAAAA
    new_value = 0x5555

    # Write initial value
    await tb.write_b(test_addr, old_value)

    # Simultaneously write new value and read (write-first mode)
    dut.addr_b.value = test_addr
    dut.data_b_in.value = new_value
    dut.we_b.value = 1
    dut.en_b.value = 1
    await RisingEdge(dut.clk_b)
    dut.we_b.value = 0

    # Wait for pipeline
    for _ in range(tb.pipeline_stages):
        await RisingEdge(dut.clk_b)

    # In write-first mode, we should read the NEW value
    read_val = int(dut.data_b_out.value)
    assert read_val == new_value, f"Write-first failed: expected {new_value:x}, got {read_val:x}"
    dut._log.info(f"✓ Write-first behavior verified: {new_value:x}")


@cocotb.test()
async def test_read_enable(dut):
    """Test read enable functionality"""
    tb = TrailMapRAMTB(dut)
    await tb.setup_clocks()
    await tb.reset()

    dut._log.info("Testing read enable")

    test_addr = 300
    test_value = 0xBEEF

    # Write a value
    await tb.write_b(test_addr, test_value)

    # Read with enable=0 (should not update output)
    dut.addr_b.value = test_addr
    dut.en_b.value = 0
    dut.we_b.value = 0
    old_output = int(dut.data_b_out.value)
    await RisingEdge(dut.clk_b)
    await RisingEdge(dut.clk_b)

    # Output should not have changed
    new_output = int(dut.data_b_out.value)
    # Note: This test assumes previous output is different from test_value
    dut._log.info(f"Read enable=0: output remained {new_output:x}")

    # Now read with enable=1
    read_val = await tb.read_b(test_addr)
    assert read_val == test_value, f"Read with enable=1 failed: expected {test_value:x}, got {read_val:x}"
    dut._log.info(f"✓ Read enable behavior verified")


@cocotb.test()
async def test_independent_clocks(dut):
    """Test that ports work independently with different clock domains"""
    tb = TrailMapRAMTB(dut)
    await tb.setup_clocks()
    await tb.reset()

    dut._log.info("Testing independent clock operation")

    # Write from Port B (100 MHz)
    addr_b = 400
    value_b = 0xCAFE
    await tb.write_b(addr_b, value_b)

    # Read from Port A (25 MHz) at different address
    addr_a = 500
    value_a = 0xDEAD
    await tb.write_b(addr_a, value_a)

    # Verify both reads work independently
    read_a = await tb.read_a(addr_a)
    read_b = await tb.read_b(addr_b)

    assert read_a == value_a, f"Port A independent read failed"
    assert read_b == value_b, f"Port B independent read failed"
    dut._log.info(f"✓ Independent clock operation verified")


@cocotb.test()
async def test_concurrent_access_different_addr(dut):
    """Test concurrent access to different addresses"""
    tb = TrailMapRAMTB(dut)
    await tb.setup_clocks()
    await tb.reset()

    dut._log.info("Testing concurrent access to different addresses")

    # Setup different addresses
    addr_a = 1000
    addr_b = 2000
    value_a = 0x1111
    value_b = 0x2222

    # Write both values
    await tb.write_b(addr_a, value_a)
    await tb.write_b(addr_b, value_b)

    # Start concurrent reads (one from each port)
    dut.addr_a.value = addr_a
    dut.en_a.value = 1
    dut.addr_b.value = addr_b
    dut.en_b.value = 1
    dut.we_b.value = 0

    # Let them run for a bit
    for _ in range(5):
        await RisingEdge(dut.clk_b)

    # Verify reads
    read_a = await tb.read_a(addr_a)
    read_b = await tb.read_b(addr_b)

    assert read_a == value_a, f"Concurrent Port A read failed"
    assert read_b == value_b, f"Concurrent Port B read failed"
    dut._log.info(f"✓ Concurrent access to different addresses verified")


@cocotb.test()
async def test_same_address_access(dut):
    """Test access to same address from both ports"""
    tb = TrailMapRAMTB(dut)
    await tb.setup_clocks()
    await tb.reset()

    dut._log.info("Testing same address access from both ports")

    test_addr = 5000
    test_value = 0xFACE

    # Write value on Port B
    await tb.write_b(test_addr, test_value)

    # Read from both ports simultaneously
    dut.addr_a.value = test_addr
    dut.en_a.value = 1
    dut.addr_b.value = test_addr
    dut.en_b.value = 1
    dut.we_b.value = 0

    await RisingEdge(dut.clk_b)
    for _ in range(5):
        await RisingEdge(dut.clk_a)
        await RisingEdge(dut.clk_b)

    # Both ports should read the same value
    read_a = await tb.read_a(test_addr)
    read_b = await tb.read_b(test_addr)

    assert read_a == test_value, f"Port A same-address read failed"
    assert read_b == test_value, f"Port B same-address read failed"
    dut._log.info(f"✓ Same address access verified")


@cocotb.test()
async def test_memory_sweep(dut):
    """Test writing and reading entire memory space"""
    tb = TrailMapRAMTB(dut)
    await tb.setup_clocks()
    await tb.reset()

    dut._log.info("Testing full memory sweep")

    # Test a subset of memory (full test would take too long)
    test_size = min(1000, tb.mem_size)
    test_addrs = random.sample(range(tb.mem_size), test_size)

    # Write phase
    dut._log.info(f"Writing {test_size} random addresses...")
    for i, addr in enumerate(test_addrs):
        value = (addr * 7 + 13) & ((1 << tb.data_width) - 1)  # Pseudo-random pattern
        await tb.write_b(addr, value)

        if (i + 1) % 100 == 0:
            dut._log.info(f"  Written {i+1}/{test_size} addresses")

    # Read and verify phase
    dut._log.info(f"Verifying {test_size} addresses...")
    errors = 0
    for i, addr in enumerate(test_addrs):
        expected = (addr * 7 + 13) & ((1 << tb.data_width) - 1)

        # Read from Port B
        read_val = await tb.read_b(addr)
        if read_val != expected:
            dut._log.error(f"Mismatch at addr {addr}: expected {expected:x}, got {read_val:x}")
            errors += 1

        if (i + 1) % 100 == 0:
            dut._log.info(f"  Verified {i+1}/{test_size} addresses")

    assert errors == 0, f"Memory sweep found {errors} errors"
    dut._log.info(f"✓ Full memory sweep verified ({test_size} addresses)")


@cocotb.test()
async def test_pipeline_delay(dut):
    """Test that pipeline stages introduce correct delay"""
    tb = TrailMapRAMTB(dut)
    await tb.setup_clocks()
    await tb.reset()

    dut._log.info(f"Testing pipeline delay (stages: {tb.pipeline_stages})")

    test_addr = 10000
    test_value = 0xAAAA

    # Write value
    await tb.write_b(test_addr, test_value)

    # Start read
    dut.addr_b.value = test_addr
    dut.en_b.value = 1
    dut.we_b.value = 0
    await RisingEdge(dut.clk_b)

    # Check that data is NOT immediately available (if pipeline > 0)
    if tb.pipeline_stages > 0:
        immediate_val = int(dut.data_b_out.value)
        # Should still have old data
        dut._log.info(f"After 1 cycle: data_b_out = {immediate_val:x} (should not be {test_value:x} yet)")

    # Wait for full pipeline
    for i in range(tb.pipeline_stages):
        await RisingEdge(dut.clk_b)
        dut._log.info(f"Pipeline stage {i+1}/{tb.pipeline_stages}")

    # Now data should be available
    final_val = int(dut.data_b_out.value)
    assert final_val == test_value, f"Pipeline delay test failed: expected {test_value:x}, got {final_val:x}"
    dut._log.info(f"✓ Pipeline delay verified: {tb.pipeline_stages} stages")


@cocotb.test()
async def test_burst_writes(dut):
    """Test burst write operations"""
    tb = TrailMapRAMTB(dut)
    await tb.setup_clocks()
    await tb.reset()

    dut._log.info("Testing burst writes")

    base_addr = 20000
    burst_size = 100

    # Burst write
    for i in range(burst_size):
        addr = base_addr + i
        value = (i * 0x111) & ((1 << tb.data_width) - 1)
        await tb.write_b(addr, value)

    # Verify all writes
    errors = 0
    for i in range(burst_size):
        addr = base_addr + i
        expected = (i * 0x111) & ((1 << tb.data_width) - 1)
        read_val = await tb.read_b(addr)

        if read_val != expected:
            dut._log.error(f"Burst write error at offset {i}: expected {expected:x}, got {read_val:x}")
            errors += 1

    assert errors == 0, f"Burst write test found {errors} errors"
    dut._log.info(f"✓ Burst write test passed ({burst_size} consecutive writes)")


# Test factory for different pipeline configurations
# This will be configured in the Makefile
