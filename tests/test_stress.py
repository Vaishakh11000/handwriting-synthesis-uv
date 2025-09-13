#!/usr/bin/env python3
"""
Stress test for the handwriting synthesis model
"""

import time
import traceback
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import compatibility layer first
import tf_compat

from demo import Hand

def stress_test():
    """Run continuous generation test"""
    print("Running stress test - generating 10 samples continuously...")
    
    try:
        hand = Hand()
        
        test_texts = [
            "Stress test sample 1",
            "Testing continuous generation",  
            "Model stability check",
            "Performance under load",
            "Memory usage validation"
        ]
        
        times = []
        total_start = time.time()
        
        for i in range(10):
            text = test_texts[i % len(test_texts)]
            
            start_time = time.time()
            hand.write(
                filename=f'img/stress_{i:02d}.svg',
                lines=[f"{text} - Run {i+1}"],
                biases=[0.5],
                styles=[i % 13]  # Cycle through available styles
            )
            duration = time.time() - start_time
            times.append(duration)
            
            print(f"Sample {i+1:2d}: {duration:.2f}s")
            
        total_time = time.time() - total_start
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"\n=== Stress Test Results ===")
        print(f"Total samples: 10")
        print(f"Total time: {total_time:.2f}s")
        print(f"Average time per sample: {avg_time:.2f}s")
        print(f"Fastest generation: {min_time:.2f}s")
        print(f"Slowest generation: {max_time:.2f}s")
        print(f"Performance variation: {((max_time - min_time) / avg_time * 100):.1f}%")
        
        # Check for memory leaks (significant performance degradation)
        if max_time > min_time * 2.5:
            print("⚠ Warning: Significant performance variation - possible memory issues")
            return False
        else:
            print("✓ Performance is stable across multiple generations")
            
        return True
        
    except Exception as e:
        print(f"✗ Stress test failed: {str(e)}")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = stress_test()
    sys.exit(0 if success else 1)