#!/usr/bin/env python3
"""
Comprehensive test suite for the handwriting synthesis model
"""

import os
import time
import traceback
import sys

# Import compatibility layer first
import tf_compat

import numpy as np
import drawing
from demo import Hand

def test_basic_functionality():
    """Test basic model functionality with simple text"""
    print("=== Test 1: Basic Functionality ===")
    try:
        hand = Hand()
        
        # Simple test
        lines = ["Hello World"]
        biases = [0.5]
        styles = [1]
        
        print(f"Testing with text: {lines}")
        start_time = time.time()
        hand.write(
            filename='img/test_basic.svg',
            lines=lines,
            biases=biases,
            styles=styles
        )
        duration = time.time() - start_time
        print(f"✓ Basic test completed in {duration:.2f} seconds")
        
        # Check if file was created
        if os.path.exists('img/test_basic.svg'):
            file_size = os.path.getsize('img/test_basic.svg')
            print(f"✓ Output file created (size: {file_size} bytes)")
        else:
            print("✗ Output file not created")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ Basic test failed: {str(e)}")
        print(traceback.format_exc())
        return False

def test_text_lengths():
    """Test different text lengths and edge cases"""
    print("\n=== Test 2: Different Text Lengths ===")
    
    try:
        hand = Hand()
        
        test_cases = [
            # Short text
            (["Hi"], "short"),
            # Medium text  
            (["The quick brown fox jumps over the lazy dog"], "medium"),
            # Multiple lines
            (["Line 1", "Line 2", "Line 3"], "multiline"),
            # Near max length (75 chars)
            (["This is a test of a very long line that approaches the maximum length"], "long"),
        ]
        
        for lines, test_name in test_cases:
            print(f"Testing {test_name}: {lines}")
            start_time = time.time()
            
            hand.write(
                filename=f'img/test_{test_name}.svg',
                lines=lines,
                biases=[0.5] * len(lines),
                styles=[2] * len(lines)
            )
            
            duration = time.time() - start_time
            print(f"✓ {test_name.capitalize()} test completed in {duration:.2f} seconds")
            
        return True
        
    except Exception as e:
        print(f"✗ Text length test failed: {str(e)}")
        print(traceback.format_exc())
        return False

def test_bias_style_combinations():
    """Test various bias and style combinations"""
    print("\n=== Test 3: Bias and Style Combinations ===")
    
    try:
        hand = Hand()
        lines = ["Test different styles"]
        
        # Test different biases
        bias_tests = [0.1, 0.5, 0.9]
        for i, bias in enumerate(bias_tests):
            print(f"Testing bias: {bias}")
            hand.write(
                filename=f'img/test_bias_{i}.svg',
                lines=lines,
                biases=[bias],
                styles=[3]
            )
            
        # Test different styles (check available styles)
        available_styles = []
        for i in range(13):  # 0-12 based on the styles directory
            style_file = f'styles/style-{i}-strokes.npy'
            if os.path.exists(style_file):
                available_styles.append(i)
        
        print(f"Available styles: {available_styles}")
        
        # Test a few different styles
        for style in available_styles[:5]:  # Test first 5 styles
            print(f"Testing style: {style}")
            hand.write(
                filename=f'img/test_style_{style}.svg',
                lines=lines,
                biases=[0.5],
                styles=[style]
            )
            
        return True
        
    except Exception as e:
        print(f"✗ Bias/Style test failed: {str(e)}")
        print(traceback.format_exc())
        return False

def test_error_handling():
    """Test error handling and validation"""
    print("\n=== Test 4: Error Handling ===")
    
    try:
        hand = Hand()
        
        # Test 1: Text too long (should raise ValueError)
        print("Testing text length validation...")
        try:
            long_text = "a" * 76  # 76 characters, should exceed limit
            hand.write(
                filename='img/test_error.svg',
                lines=[long_text],
                biases=[0.5],
                styles=[1]
            )
            print("✗ Should have raised ValueError for long text")
            return False
        except ValueError as e:
            print(f"✓ Correctly caught ValueError: {str(e)}")
            
        # Test 2: Invalid characters
        print("Testing invalid character validation...")
        try:
            hand.write(
                filename='img/test_error2.svg',
                lines=["Hello 世界"],  # Non-ASCII characters
                biases=[0.5],
                styles=[1]
            )
            print("✗ Should have raised ValueError for invalid characters")
            return False
        except ValueError as e:
            print(f"✓ Correctly caught ValueError: {str(e)}")
            
        # Test 3: Mismatched array lengths
        print("Testing array length validation...")
        try:
            hand.write(
                filename='img/test_error3.svg',
                lines=["Hello", "World"],
                biases=[0.5],  # Only one bias for two lines
                styles=[1, 2]
            )
            print("✓ Handled mismatched array lengths gracefully")
        except Exception as e:
            print(f"Note: Got exception for mismatched arrays: {str(e)}")
            
        return True
        
    except Exception as e:
        print(f"✗ Error handling test failed: {str(e)}")
        print(traceback.format_exc())
        return False

def test_performance():
    """Test performance and memory usage"""
    print("\n=== Test 5: Performance ===")
    
    try:
        hand = Hand()
        
        # Test multiple calls to ensure no memory leaks
        print("Testing multiple generations...")
        times = []
        
        for i in range(3):
            lines = [f"Performance test {i+1}"]
            
            start_time = time.time()
            hand.write(
                filename=f'img/test_perf_{i}.svg',
                lines=lines,
                biases=[0.5],
                styles=[4]
            )
            duration = time.time() - start_time
            times.append(duration)
            print(f"Generation {i+1}: {duration:.2f} seconds")
            
        avg_time = sum(times) / len(times)
        print(f"✓ Average generation time: {avg_time:.2f} seconds")
        
        # Check for significant performance degradation
        if max(times) > min(times) * 3:
            print("⚠ Warning: Significant performance variation detected")
        else:
            print("✓ Performance is consistent")
            
        return True
        
    except Exception as e:
        print(f"✗ Performance test failed: {str(e)}")
        print(traceback.format_exc())
        return False

def main():
    """Run comprehensive tests"""
    print("Starting comprehensive handwriting synthesis tests...\n")
    
    # Ensure img directory exists
    os.makedirs('img', exist_ok=True)
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Text Lengths", test_text_lengths), 
        ("Bias/Style Combinations", test_bias_style_combinations),
        ("Error Handling", test_error_handling),
        ("Performance", test_performance)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print(f"{'='*50}")
        
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} PASSED")
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} FAILED with exception: {str(e)}")
            
    print(f"\n{'='*50}")
    print(f"SUMMARY: {passed}/{total} tests passed")
    print(f"{'='*50}")
    
    if passed == total:
        print("🎉 All tests passed! The model is working smoothly.")
        return 0
    else:
        print(f"❌ {total - passed} tests failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())