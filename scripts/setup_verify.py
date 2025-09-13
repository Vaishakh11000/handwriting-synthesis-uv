#!/usr/bin/env python3
"""
Setup verification script for Handwriting Synthesis with Messiness Control
Run with: uv run python setup_verify.py
"""
import os
import sys

def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import tensorflow
        import numpy
        import svgwrite
        import matplotlib
        import scipy
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def check_model_files():
    """Check if model files exist"""
    required_files = [
        'checkpoints',
        'styles', 
        'demo.py',
        'drawing.py',
        'rnn.py'
    ]
    
    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)
    
    if missing:
        print(f"❌ Missing files/directories: {missing}")
        return False
    else:
        print("✅ All required model files present")
        return True

def test_basic_functionality():
    """Test basic messiness functionality"""
    try:
        from demo import Hand
        import drawing
        
        # Test messiness function directly
        import numpy as np
        test_coords = np.array([[0, 0, 0], [10, 0, 1]], dtype=np.float64)
        result = drawing.add_messiness(test_coords, 0.5)
        
        if result.shape == test_coords.shape:
            print("✅ Messiness function working correctly")
            return True
        else:
            print("❌ Messiness function output shape mismatch")
            return False
            
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_model_loading():
    """Test if the neural network model loads correctly"""
    try:
        from demo import Hand
        hand = Hand()
        print("✅ Neural network model loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        print("   This might be due to missing checkpoints or TensorFlow issues")
        return False

def run_sample_generation():
    """Generate a test sample to verify complete functionality"""
    try:
        from demo import Hand
        hand = Hand()
        
        # Generate test samples
        test_cases = [
            ("Perfect writing", 0.0),
            ("Natural variation", 0.5),
            ("Rushed writing", 1.3)
        ]
        
        os.makedirs('verification_output', exist_ok=True)
        
        for desc, messiness in test_cases:
            filename = f'verification_output/test_{messiness}.svg'
            hand.write(
                filename=filename,
                lines=[f'{desc} (messiness={messiness})'],
                messiness=messiness
            )
            print(f"✅ Generated: {filename}")
        
        print("✅ Sample generation completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Sample generation failed: {e}")
        return False

def main():
    print("=" * 60)
    print("🔍 HANDWRITING SYNTHESIS SETUP VERIFICATION")
    print("=" * 60)
    
    tests = [
        ("Dependencies", check_dependencies),
        ("Model Files", check_model_files),
        ("Basic Functionality", test_basic_functionality),
        ("Model Loading", test_model_loading),
        ("Sample Generation", run_sample_generation)
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"\n🧪 Testing {name}...")
        try:
            if test_func():
                passed += 1
            else:
                print(f"   Test failed: {name}")
        except Exception as e:
            print(f"   Test error: {name} - {e}")
    
    print("\n" + "=" * 60)
    if passed == total:
        print("🎉 ALL TESTS PASSED! Setup is complete and working.")
        print("\n🚀 Ready to use:")
        print("   uv run python demo.py")
        print("   uv run python test_messiness.py")
        print("\n📚 Check README.md for usage examples")
    else:
        print(f"⚠️  {passed}/{total} tests passed. Please check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("   • Ensure you're using: uv run python setup_verify.py")
        print("   • Check that all model files are present")
        print("   • Verify TensorFlow installation compatibility")
    
    print("=" * 60)
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())