# Installation Guide

## Quick Setup

### Prerequisites
- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) package manager

### Install uv (if not already installed)
```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Clone and Setup
```bash
# Clone the repository
git clone https://github.com/Vaishakh11000/handwriting-synthesis-uv.git
cd handwriting-synthesis-uv

# Install dependencies
uv install

# Verify setup
uv run python setup_verify.py
```

### Quick Test
```bash
# Generate test samples
uv run python -c "
from demo import Hand
h = Hand()
h.write('test.svg', ['Hello from handwriting synthesis!'], messiness=0.5)
print('Generated test.svg successfully!')
"
```

## Troubleshooting

### Common Issues

**1. TensorFlow Warnings:**
```
2025-xx-xx: W tensorflow/...
```
These are normal and don't affect functionality.

**2. CUDA Warnings:**
```
Could not find cuda drivers...
```
Model runs on CPU by default, no GPU required.

**3. Model Loading Issues:**
Ensure you have the complete repository with `checkpoints/` and `styles/` directories.

**4. Character Errors:**
```
Invalid character detected...
```
Use only supported characters: `A-Z a-z 0-9 ! " # ' ( ) , - . : ; ?`

### Verify Installation
Run the verification script to check your setup:
```bash
uv run python setup_verify.py
```

This will test:
- ✅ Dependencies installed
- ✅ Model files present  
- ✅ Basic functionality
- ✅ Neural network loading
- ✅ Sample generation

## Next Steps

Once installed, check out:
- `README.md` - Complete usage guide
- `demo.py` - Example implementations
- `test_messiness.py` - Comprehensive testing

## Support

If you encounter issues:
1. Run `uv run python setup_verify.py`
2. Check the error messages
3. Ensure you're using the correct Python version (3.11+)
4. Verify all repository files are present