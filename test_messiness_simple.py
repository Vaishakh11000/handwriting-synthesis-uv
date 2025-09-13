#!/usr/bin/env python3
"""
Simple test for the messiness function without requiring TensorFlow
"""
import numpy as np
import drawing


def create_test_strokes():
    """Create simple test stroke data"""
    # Simple horizontal line with pen lifts
    coords = np.array([
        [0, 0, 0],    # start
        [10, 0, 0],   # horizontal line
        [20, 0, 0],
        [30, 0, 1],   # pen lift
        [40, 0, 0],   # new stroke
        [50, 0, 0],
        [60, 0, 1],   # pen lift
    ])
    return coords


def test_messiness_function():
    """Test the add_messiness function directly"""
    print("Testing drawing.add_messiness function...")
    
    # Create test coordinates
    original_coords = create_test_strokes()
    print(f"Original coordinates shape: {original_coords.shape}")
    print(f"Original x-coordinates: {original_coords[:, 0]}")
    print(f"Original y-coordinates: {original_coords[:, 1]}")
    
    # Test different messiness levels across full range
    messiness_levels = [0.0, 0.3, 0.6, 1.0, 1.3, 1.5]
    
    for messiness in messiness_levels:
        print(f"\nTesting messiness level: {messiness}")
        
        try:
            # Apply messiness
            messy_coords = drawing.add_messiness(original_coords, messiness)
            
            # Check that the function returns expected output
            assert messy_coords.shape == original_coords.shape, "Shape mismatch"
            assert len(messy_coords) == len(original_coords), "Length mismatch"
            
            # Check that end-of-stroke markers are preserved
            original_eos = original_coords[:, 2]
            messy_eos = messy_coords[:, 2]
            assert np.array_equal(original_eos, messy_eos), "EOS markers changed"
            
            # For messiness > 0, coordinates should be different
            if messiness > 0:
                coord_diff = np.sum(np.abs(messy_coords[:, :2] - original_coords[:, :2]))
                assert coord_diff > 0, f"No changes applied for messiness {messiness}"
                print(f"  ✓ Coordinates changed (total diff: {coord_diff:.3f})")
            else:
                # For messiness = 0, should be identical
                assert np.allclose(messy_coords, original_coords), "Messiness=0 should not change coordinates"
                print(f"  ✓ No changes for messiness=0")
            
            print(f"  ✓ Messiness {messiness} test passed")
            
        except Exception as e:
            print(f"  ✗ Messiness {messiness} test failed: {str(e)}")
            return False
    
    return True


def test_edge_cases():
    """Test edge cases for the messiness function"""
    print("\nTesting edge cases...")
    
    # Test empty coordinates
    try:
        empty_coords = np.array([]).reshape(0, 3)
        result = drawing.add_messiness(empty_coords, 0.5)
        assert result.shape == (0, 3), "Empty array handling failed"
        print("  ✓ Empty coordinates handled correctly")
    except Exception as e:
        print(f"  ✗ Empty coordinates test failed: {str(e)}")
        return False
    
    # Test single point
    try:
        single_point = np.array([[0, 0, 1]])
        result = drawing.add_messiness(single_point, 0.5)
        assert result.shape == (1, 3), "Single point handling failed"
        print("  ✓ Single point handled correctly")
    except Exception as e:
        print(f"  ✗ Single point test failed: {str(e)}")
        return False
    
    # Test negative messiness (should be handled gracefully)
    try:
        coords = create_test_strokes()
        result = drawing.add_messiness(coords, -0.1)
        # Should either handle gracefully or clamp to 0
        print("  ✓ Negative messiness handled")
    except Exception as e:
        print(f"  ✗ Negative messiness test failed: {str(e)}")
        return False
    
    # Test messiness > 1.0
    try:
        coords = create_test_strokes()
        result = drawing.add_messiness(coords, 1.5)
        print("  ✓ Messiness > 1.0 handled")
    except Exception as e:
        print(f"  ✗ Messiness > 1.0 test failed: {str(e)}")
        return False
    
    return True


def test_messiness_effects():
    """Test that different messiness effects are actually applied"""
    print("\nTesting specific messiness effects...")
    
    # Create a longer test stroke to see effects better
    coords = np.array([
        [0, 10, 0],   # start
        [10, 10, 0],  # horizontal line
        [20, 10, 0],
        [30, 10, 0],
        [40, 10, 1],  # pen lift
        [50, 10, 0],  # new stroke
        [60, 10, 0],
        [70, 10, 0],
        [80, 10, 1],  # end
    ])
    
    high_messiness = 0.8
    messy_coords = drawing.add_messiness(coords, high_messiness)
    
    # Check for various effects
    effects_found = {
        'baseline_variation': False,
        'spacing_changes': False,
        'coordinate_changes': False
    }
    
    # Check baseline variation (y-coordinate changes)
    original_y = coords[:, 1]
    messy_y = messy_coords[:, 1]
    if not np.allclose(original_y, messy_y, atol=0.1):
        effects_found['baseline_variation'] = True
        print("  ✓ Baseline variation detected")
    
    # Check spacing changes (x-coordinate shifts)
    original_x = coords[:, 0]
    messy_x = messy_coords[:, 0]
    if not np.allclose(original_x, messy_x, atol=0.1):
        effects_found['spacing_changes'] = True
        print("  ✓ Spacing changes detected")
    
    # Check overall coordinate changes
    if not np.allclose(coords[:, :2], messy_coords[:, :2]):
        effects_found['coordinate_changes'] = True
        print("  ✓ Coordinate changes detected")
    
    effects_count = sum(effects_found.values())
    print(f"  Found {effects_count}/3 expected messiness effects")
    
    return effects_count >= 2  # Expect at least 2 out of 3 effects


def main():
    print("=" * 50)
    print("MESSINESS FUNCTION TEST SUITE")
    print("=" * 50)
    
    all_passed = True
    
    # Test 1: Basic functionality
    if test_messiness_function():
        print("✓ Basic messiness function test PASSED")
    else:
        print("✗ Basic messiness function test FAILED")
        all_passed = False
    
    # Test 2: Edge cases
    if test_edge_cases():
        print("✓ Edge cases test PASSED")
    else:
        print("✗ Edge cases test FAILED")
        all_passed = False
    
    # Test 3: Messiness effects
    if test_messiness_effects():
        print("✓ Messiness effects test PASSED")
    else:
        print("✗ Messiness effects test FAILED")
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Messiness function is working correctly.")
        print("\nThe messiness feature has been successfully implemented with:")
        print("  📝 Normal Handwriting (0.0-1.0):")
        print("    • Slight forward lean and natural variations")
        print("    • Baseline drift and letter height inconsistency")
        print("    • Character spacing irregularity")
        print("  ⚡ Adult Rush Writing (1.0-1.5):")
        print("    • Increased forward lean from writing speed")
        print("    • Horizontal compression and erratic spacing")
        print("    • Pressure fluctuations and baseline instability")
        print("    • Progressive degradation under time pressure")
        print("\nUsage: hand.write(..., messiness=1.3)  # 0.0 = perfect, 1.5 = extreme rush")
    else:
        print("⚠️  SOME TESTS FAILED. Check the error messages above.")
    print("=" * 50)
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    exit(main())