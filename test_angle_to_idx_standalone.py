#!/usr/bin/env python3
"""
Standalone unit test for angle-to-index conversion.
Tests RTL formula against Python reference.
"""

def test_all_agents():
    """Test angle-to-index conversion for all 10 test agents."""

    # Test cases from actual agent initialization (circle pattern)
    test_cases = [
        (12868, 511, 180.000510, 0),  # Agent 0 @ 180°
        (15442, 614, 216.006208, 1),  # Agent 1 @ 216°
        (18015, 716, 251.997917, 2),  # Agent 2 @ 252°
        (20589, 819, 288.003614, 3),  # Agent 3 @ 288°
        (23162, 921, 323.995324, 4),  # Agent 4 @ 324°
        (    0,   0,   0.000000, 5),  # Agent 5 @ 0°
        ( 2574, 102,  36.005697, 6),  # Agent 6 @ 36°
        ( 5147, 204,  71.997407, 7),  # Agent 7 @ 72°
        ( 7721, 307, 108.003104, 8),  # Agent 8 @ 108°
        (10294, 409, 143.994813, 9),  # Agent 9 @ 144°
    ]

    print("\n" + "=" * 80)
    print("ANGLE-TO-INDEX CONVERSION TEST")
    print("=" * 80)
    print(f"Testing {len(test_cases)} angles from agent initialization")
    print()

    TWO_PI_FP = 25737
    TABLE_SIZE = 1024

    passed = 0
    failed = 0
    failures = []

    for angle_fp, expected_idx, angle_deg, agent_id in test_cases:
        # Python formula: int((angle * table_size) / two_pi)
        python_idx = int((angle_fp * TABLE_SIZE) / TWO_PI_FP)

        # RTL formula: (angle << 10) / 25737
        rtl_idx = (angle_fp << 10) // 25737

        python_match = (python_idx == expected_idx)
        rtl_match = (rtl_idx == expected_idx)

        if python_match and rtl_match:
            status = "✓ PASS"
            passed += 1
        else:
            status = "✗ FAIL"
            failed += 1
            failures.append((agent_id, angle_deg, angle_fp, python_idx, rtl_idx, expected_idx))

        print(f"Agent {agent_id} @ {angle_deg:7.3f}° (fp={angle_fp:5d}): "
              f"Python={python_idx:3d}, RTL={rtl_idx:3d}, Expected={expected_idx:3d} {status}")

    print()
    print("=" * 80)
    print(f"RESULT: {passed} passed, {failed} failed out of {len(test_cases)} tests")

    if failures:
        print()
        print("FAILURES:")
        for agent_id, angle_deg, angle_fp, python_idx, rtl_idx, expected_idx in failures:
            print(f"  Agent {agent_id}: Python={python_idx} RTL={rtl_idx} Expected={expected_idx}")

    print("=" * 80)

    return failed == 0


def test_formula_equivalence():
    """Verify Python and RTL formulas are equivalent for ALL possible angles."""

    print("\n" + "=" * 80)
    print("FORMULA EQUIVALENCE TEST (EXHAUSTIVE)")
    print("=" * 80)

    TWO_PI_FP = 25737
    TABLE_SIZE = 1024
    mismatches = []

    print(f"Testing all {TWO_PI_FP} angle values (0 to {TWO_PI_FP-1})...")

    for angle_fp in range(TWO_PI_FP):
        python_result = int((angle_fp * TABLE_SIZE) / TWO_PI_FP)
        rtl_result = (angle_fp << 10) // TWO_PI_FP

        if python_result != rtl_result:
            mismatches.append((angle_fp, python_result, rtl_result))

    if mismatches:
        print(f"✗ Found {len(mismatches)} mismatches out of {TWO_PI_FP} tests:")
        for angle, py, rtl in mismatches[:20]:  # Show first 20
            print(f"  angle_fp={angle:5d}: Python={py:3d}, RTL={rtl:3d}, diff={rtl-py}")
        if len(mismatches) > 20:
            print(f"  ... and {len(mismatches)-20} more mismatches")
    else:
        print(f"✓ All {TWO_PI_FP} angles matched perfectly (bit-exact)")

    print("=" * 80)

    return len(mismatches) == 0


if __name__ == '__main__':
    success = True
    success &= test_all_agents()
    success &= test_formula_equivalence()

    if success:
        print("\n✅ ALL TESTS PASSED")
        exit(0)
    else:
        print("\n❌ SOME TESTS FAILED")
        exit(1)
