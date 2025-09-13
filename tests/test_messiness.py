#!/usr/bin/env python3
"""
Test script for the messiness feature in handwriting synthesis
Run with: uv run python test_messiness.py
"""
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import compatibility layer first
import tf_compat

from demo import Hand


def test_messiness_levels():
    """Test different levels of messiness from clean to very messy"""
    print("Testing messiness levels...")
    
    # Create img directory if it doesn't exist
    if not os.path.exists('img'):
        os.makedirs('img')
    
    hand = Hand()
    
    # Test text that demonstrates various writing scenarios
    test_cases = [
        {
            'name': 'perfect_writing',
            'text': [
                'In conclusion, the economic theories discussed',
                'demonstrate clear relationships between supply',
                'and demand in modern market systems.'
            ],
            'messiness': 0.0,
            'description': 'Perfect, neat handwriting'
        },
        {
            'name': 'slight_variation',
            'text': [
                'The analysis shows that environmental factors',
                'play a crucial role in determining outcomes',
                'for sustainable development projects worldwide.'
            ],
            'messiness': 0.4,
            'description': 'Slight natural variation in handwriting'
        },
        {
            'name': 'moderate_variation',
            'text': [
                'Furthermore, the research indicates that',
                'technological advancement has significantly',
                'impacted traditional business models and practices.'
            ],
            'messiness': 0.8,
            'description': 'Moderate handwriting variation'
        },
        {
            'name': 'maximum_normal',
            'text': [
                'The statistical data reveals important trends',
                'in consumer behavior patterns that businesses',
                'must consider for future strategic planning.'
            ],
            'messiness': 1.0,
            'description': 'Maximum normal variation'
        },
        {
            'name': 'slight_rush',
            'text': [
                'Time is running short but I need to explain',
                'the key concepts clearly for full marks',
                'in this final examination question.'
            ],
            'messiness': 1.1,
            'description': 'Slightly rushed adult writing'
        },
        {
            'name': 'moderate_rush',
            'text': [
                'The professor said we have 10 minutes left',
                'so I have to write faster to finish all',
                'the required points in my essay response.'
            ],
            'messiness': 1.3,
            'description': 'Moderately rushed exam writing'
        },
        {
            'name': 'maximum_rush',
            'text': [
                'Only 2 minutes remaining must write quickly',
                'to get all main arguments down on paper',
                'before time runs out completely.'
            ],
            'messiness': 1.5,
            'description': 'Maximum rush - exam time pressure'
        }
    ]
    
    print(f"Generating {len(test_cases)} test cases...")
    
    for i, test_case in enumerate(test_cases):
        print(f"  [{i+1}/{len(test_cases)}] {test_case['description']} (messiness={test_case['messiness']})")
        
        try:
            hand.write(
                filename=f"img/messiness_{test_case['name']}.svg",
                lines=test_case['text'],
                biases=[0.75] * len(test_case['text']),
                styles=[5] * len(test_case['text']),
                messiness=test_case['messiness']
            )
            print(f"    ✓ Generated: img/messiness_{test_case['name']}.svg")
            
        except Exception as e:
            print(f"    ✗ Failed: {str(e)}")
            return False
    
    return True


def test_messiness_comparison():
    """Generate comparison samples with same text, different messiness"""
    print("\nGenerating comprehensive messiness comparison...")
    
    essay_text = [
        "The impact of technology on modern education",
        "has been both transformative and challenging.",
        "Students now have access to vast resources",
        "but must also navigate digital distractions."
    ]
    
    messiness_levels = [0.0, 0.3, 0.6, 1.0, 1.2, 1.5]
    descriptions = [
        "Perfect neat writing",
        "Slight variation", 
        "Moderate variation",
        "Maximum normal",
        "Rushed writing",
        "Extreme time pressure"
    ]
    
    hand = Hand()
    
    try:
        # Create individual files for each level
        for level, desc in zip(messiness_levels, descriptions):
            lines_with_desc = [f"Messiness {level} - {desc}:"] + essay_text
            hand.write(
                filename=f"img/comparison_mess_{level}.svg",
                lines=lines_with_desc,
                biases=[0.75] * len(lines_with_desc),
                styles=[7] * len(lines_with_desc),
                messiness=level
            )
        
        print("    ✓ Generated comparison samples for levels 0.0-1.5")
        return True
        
    except Exception as e:
        print(f"    ✗ Comparison test failed: {str(e)}")
        return False


def test_exam_scenario():
    """Test realistic exam writing scenario with time pressure progression"""
    print("\nTesting realistic exam scenario...")
    
    exam_responses = [
        {
            'question': 'Question 1: Explain the main causes',
            'answer': [
                'The primary factors contributing to this phenomenon',
                'include economic instability, social changes,',
                'and technological disruption in various sectors.'
            ],
            'messiness': 0.2,  # Start neat
            'time_pressure': 'Beginning of exam - plenty of time'
        },
        {
            'question': 'Question 3: Analyze the implications',
            'answer': [
                'The research suggests several important trends',
                'that will likely impact future developments',
                'in this field over the next decade.'
            ],
            'messiness': 0.7,  # Getting a bit rushed
            'time_pressure': 'Middle of exam - moderate pressure'
        },
        {
            'question': 'Question 5: Compare and contrast',
            'answer': [
                'Both approaches have distinct advantages',
                'however the implementation challenges',
                'vary significantly between contexts'
            ],
            'messiness': 1.2,  # Time pressure building
            'time_pressure': 'Running low on time - rushing'
        },
        {
            'question': 'Final Question: Conclude with',
            'answer': [
                'In summary the evidence clearly shows',
                'that immediate action is required',
                'to address these critical issues'
            ],
            'messiness': 1.5,  # Maximum rush
            'time_pressure': 'Final minutes - extreme rush'
        }
    ]
    
    hand = Hand()
    success_count = 0
    
    for i, scenario in enumerate(exam_responses):
        try:
            lines = [scenario['question']] + scenario['answer'] + ['']
            hand.write(
                filename=f"img/exam_scenario_{i+1}.svg",
                lines=lines,
                biases=[0.75] * len(lines),
                styles=[5] * len(lines),
                messiness=scenario['messiness']
            )
            print(f"    ✓ {scenario['time_pressure']} (messiness={scenario['messiness']})")
            success_count += 1
            
        except Exception as e:
            print(f"    ✗ Scenario {i+1} failed: {str(e)}")
    
    return success_count > 0


def test_messiness_with_styles():
    """Test messiness with different handwriting styles"""
    print("\nTesting messiness with different styles...")
    
    text = [
        "Testing style variations with messiness",
        "to ensure compatibility across all styles"
    ]
    available_styles = [0, 3, 5, 7, 9, 12]  # Common available styles
    messiness_level = 1.2  # Rush mode
    
    hand = Hand()
    
    success_count = 0
    for style in available_styles:
        try:
            # Check if style files exist
            style_file = f'styles/style-{style}-strokes.npy'
            if os.path.exists(style_file):
                lines = [f"Style {style} with rush messiness:"] + text
                hand.write(
                    filename=f"img/style_{style}_rush.svg",
                    lines=lines,
                    biases=[0.75] * len(lines),
                    styles=[style] * len(lines),
                    messiness=messiness_level
                )
                print(f"    ✓ Style {style} with rush writing")
                success_count += 1
            else:
                print(f"    - Style {style} not available")
                
        except Exception as e:
            print(f"    ✗ Style {style} failed: {str(e)}")
    
    return success_count > 0


def main():
    print("=" * 50)
    print("MESSINESS FEATURE TEST SUITE")
    print("=" * 50)
    
    all_passed = True
    
    # Test 1: Basic messiness levels
    try:
        if test_messiness_levels():
            print("✓ Messiness levels test PASSED")
        else:
            print("✗ Messiness levels test FAILED")
            all_passed = False
    except Exception as e:
        print(f"✗ Messiness levels test ERROR: {str(e)}")
        all_passed = False
    
    # Test 2: Comparison samples
    try:
        if test_messiness_comparison():
            print("✓ Comparison test PASSED")
        else:
            print("✗ Comparison test FAILED")
            all_passed = False
    except Exception as e:
        print(f"✗ Comparison test ERROR: {str(e)}")
        all_passed = False
    
    # Test 3: Exam scenario progression
    try:
        if test_exam_scenario():
            print("✓ Exam scenario test PASSED")
        else:
            print("✗ Exam scenario test FAILED")
            all_passed = False
    except Exception as e:
        print(f"✗ Exam scenario test ERROR: {str(e)}")
        all_passed = False

    # Test 4: Style + messiness combinations
    try:
        if test_messiness_with_styles():
            print("✓ Style combinations test PASSED")
        else:
            print("✗ Style combinations test FAILED")
            all_passed = False
    except Exception as e:
        print(f"✗ Style combinations test ERROR: {str(e)}")
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Messiness feature is working correctly.")
        print("Check the generated SVG files in the 'img' directory to see the results.")
    else:
        print("⚠️  SOME TESTS FAILED. Check the error messages above.")
    print("=" * 50)
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())