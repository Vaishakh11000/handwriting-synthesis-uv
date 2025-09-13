# Handwriting Synthesis with Messiness Control

A neural network-based handwriting synthesis model that generates realistic handwritten text with controllable messiness levels, from perfect neat writing to rushed exam conditions.

## 🎯 Features

- **Neural handwriting synthesis** using RNN/LSTM with attention mechanisms
- **Messiness control** with realistic adult writing variations (0.0-1.5 range)
- **Multiple handwriting styles** (0-12 available styles)
- **Bias control** for writing pressure and characteristics
- **SVG output** for scalable, high-quality results
- **Realistic writing effects** including time pressure simulation

## 📋 Messiness Range

### 🖊️ Normal Writing (0.0-1.0)
- **0.0**: Perfect, neat handwriting
- **0.4**: Slight natural variations
- **0.8**: Moderate handwriting inconsistency
- **1.0**: Maximum normal variation

### ⏰ Rush Writing (1.0-1.5)
- **1.1**: Slight time pressure effects
- **1.3**: Moderate rushing with compressed letters
- **1.5**: Extreme exam time pressure writing

### Effects Applied
- **Forward lean** - Natural slant from writing speed
- **Horizontal compression** - Narrower letters when rushing
- **Letter height variations** - Inconsistent sizing from speed
- **Spacing irregularities** - Uneven gaps between words/letters
- **Baseline drift** - Gradual up/down movement across the line
- **Pressure fluctuations** - Varying stroke thickness
- **Progressive degradation** - Realistic time pressure simulation

## 🚀 Installation

### Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd H-syn-1.5

# Install dependencies with uv
uv install

# Verify installation
uv run python test_messiness_simple.py
```

## 💻 Usage

### Basic Usage
```python
from demo import Hand

# Initialize the model
hand = Hand()

# Generate neat handwriting
hand.write(
    filename='neat_writing.svg',
    lines=['This is neat handwriting'],
    messiness=0.0
)

# Generate rushed handwriting
hand.write(
    filename='rushed_writing.svg',
    lines=['This is rushed exam writing'],
    messiness=1.3
)
```

### Advanced Usage
```python
# Multiple lines with different parameters
hand.write(
    filename='essay.svg',
    lines=[
        'The first paragraph is written neatly',
        'The second shows time pressure building',
        'The final paragraph is very rushed'
    ],
    biases=[0.5, 0.7, 0.9],           # Writing pressure
    styles=[5, 5, 5],                 # Handwriting style
    messiness=1.2                     # Rush level
)
```

### Command Line Usage
```bash
# Run comprehensive tests
uv run python test_messiness.py

# Generate demo samples
uv run python demo.py

# Test simple messiness function
uv run python test_messiness_simple.py
```

## 📊 Examples

### Messiness Progression
```python
scenarios = [
    ("Perfect writing", 0.0),
    ("Natural variation", 0.5), 
    ("Maximum normal", 1.0),
    ("Time pressure", 1.3),
    ("Extreme rush", 1.5)
]

for desc, messiness in scenarios:
    hand.write(
        filename=f'example_{messiness}.svg',
        lines=[f'{desc}: The quick brown fox jumps'],
        messiness=messiness
    )
```

### Exam Scenario Simulation
```python
# Simulate exam time pressure progression
exam_questions = [
    ("Question 1: Early in exam", 0.2),
    ("Question 3: Time awareness", 0.7),  
    ("Question 5: Getting rushed", 1.2),
    ("Final question: Extreme rush", 1.5)
]

for question, messiness in exam_questions:
    hand.write(
        filename=f'exam_{messiness}.svg',
        lines=[
            question,
            'The answer demonstrates clear understanding',
            'of the key concepts and provides examples'
        ],
        messiness=messiness
    )
```

## 🔧 API Reference

### Hand.write()
```python
Hand.write(
    filename: str,              # Output SVG filename
    lines: List[str],          # Text lines to generate
    biases: List[float] = None, # Writing pressure (0.0-1.0)
    styles: List[int] = None,   # Style IDs (0-12)
    messiness: float = 0.0,     # Messiness level (0.0-1.5)
    stroke_colors: List[str] = None,  # Line colors
    stroke_widths: List[int] = None   # Line widths
)
```

### Parameters
- **lines**: Text to generate (max 75 characters per line)
- **biases**: Controls writing pressure and flow (default: 0.5)
- **styles**: Handwriting style variations (default: random)
- **messiness**: Writing messiness level:
  - `0.0-1.0`: Normal handwriting variations
  - `1.0-1.5`: Adult rush writing effects
- **stroke_colors**: SVG color names (default: 'black')
- **stroke_widths**: Pixel widths (default: 2)

### Supported Characters
```
A-Z a-z 0-9 ! " # ' ( ) , - . : ; ?
```

## 🧪 Testing

### Run All Tests
```bash
uv run python test_messiness.py
```

### Test Categories
1. **Messiness Levels**: Tests 0.0-1.5 range with various text lengths
2. **Comparison Samples**: Side-by-side messiness comparisons
3. **Exam Scenarios**: Realistic time pressure progression
4. **Style Compatibility**: Messiness with different handwriting styles

### Simple Function Testing
```bash
uv run python test_messiness_simple.py
```

## 📁 Project Structure
```
H-syn-1.5/
├── demo.py              # Main usage examples and demos
├── drawing.py           # Core drawing utilities and messiness function
├── rnn.py              # Neural network architecture
├── tf_base_model.py    # TensorFlow model base class
├── test_messiness.py   # Comprehensive test suite
├── test_messiness_simple.py  # Simple function tests
├── styles/             # Pre-trained handwriting styles
├── checkpoints/        # Model checkpoints
└── img/               # Generated output samples
```

## 🎨 Generated Samples

The model generates realistic handwriting samples showing:

- **Natural progressions** from neat to rushed writing
- **Exam scenario simulations** with time pressure effects
- **Style variations** across different handwriting types
- **Realistic artifacts** like forward lean, compression, and spacing changes

## 🔬 Technical Details

### Model Architecture
- **RNN/LSTM** with attention mechanism
- **Mixture density networks** for stroke prediction
- **Style conditioning** with pre-trained style vectors
- **Bias control** for writing characteristics

### Messiness Implementation
- **Dual-range system** (0.0-1.0 normal, 1.0-1.5 rush)
- **Progressive effects** that build upon each other
- **Realistic parameters** based on adult writing behavior
- **Style-agnostic** processing compatible with all handwriting styles

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Test your changes with `uv run python test_messiness.py`
4. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Based on neural handwriting synthesis research
- Inspired by realistic writing behavior analysis
- Designed for educational and research applications

## 💡 Tips & Best Practices

### For Realistic Results
- Use **messiness 0.0-0.8** for everyday handwriting
- Use **messiness 1.0-1.3** for time pressure scenarios  
- Use **messiness 1.4-1.5** only for extreme rush conditions

### Text Recommendations
- Keep lines under 75 characters
- Use realistic sentence structures
- Consider context when setting messiness levels

### Style Selection
- Different styles respond differently to messiness
- Test with your preferred style for optimal results
- Style 5 and 7 work well for most applications

---

**Ready to generate realistic handwritten text with controllable messiness? Get started with the examples above!**