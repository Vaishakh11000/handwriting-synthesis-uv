import os
import logging

# Import compatibility layer first
from . import tf_compat

import numpy as np
import svgwrite

from . import drawing
from . import lyrics
from .rnn import rnn


class Hand(object):
    """
    Neural handwriting synthesis model with messiness control.
    
    This class provides an interface to generate realistic handwritten text
    with controllable messiness levels ranging from perfect neat writing (0.0)
    to extreme exam rush conditions (1.5).
    
    Features:
    - Multiple handwriting styles (0-12)
    - Writing pressure control via biases
    - Realistic messiness simulation for adult writing
    - SVG output for scalable results
    """

    def __init__(self):
        """
        Initialize the handwriting synthesis model.
        
        Sets up the neural network with pre-trained parameters and loads
        the model checkpoint for immediate use.
        """
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow warnings
        
        # Initialize RNN model with optimized hyperparameters
        self.nn = rnn(
            log_dir='logs',
            checkpoint_dir='../models/checkpoints',
            prediction_dir='predictions',
            learning_rates=[.0001, .00005, .00002],    # Multi-stage learning
            batch_sizes=[32, 64, 64],                  # Progressive batch sizes
            patiences=[1500, 1000, 500],              # Early stopping patience
            beta1_decays=[.9, .9, .9],                # Adam optimizer decay
            validation_batch_size=32,
            optimizer='rms',                          # RMSprop optimizer
            num_training_steps=100000,
            warm_start_init_step=17900,              # Resume from checkpoint
            regularization_constant=0.0,
            keep_prob=1.0,                           # No dropout during inference
            enable_parameter_averaging=False,
            min_steps_to_checkpoint=2000,
            log_interval=20,
            logging_level=logging.CRITICAL,          # Minimal logging
            grad_clip=10,                            # Gradient clipping
            lstm_size=400,                           # LSTM hidden units
            output_mixture_components=20,            # Mixture density components
            attention_mixture_components=10          # Attention components
        )
        
        # Load pre-trained model weights
        self.nn.restore()

    def write(self, filename, lines, biases=None, styles=None, stroke_colors=None, stroke_widths=None, messiness=0.0):
        """
        Generate handwritten text with controllable messiness and save as SVG.
        
        Args:
            filename (str): Output SVG file path
            lines (List[str]): Text lines to generate (max 75 chars each)
            biases (List[float], optional): Writing pressure for each line (0.0-1.0)
            styles (List[int], optional): Style IDs for each line (0-12)
            stroke_colors (List[str], optional): SVG color names for each line
            stroke_widths (List[int], optional): Stroke widths for each line
            messiness (float, optional): Messiness level (0.0-1.5):
                0.0-1.0: Normal handwriting variations
                1.0-1.5: Adult rushed writing (exam conditions)
        
        Raises:
            ValueError: If lines exceed 75 characters or contain invalid characters
        
        Example:
            hand = Hand()
            hand.write('output.svg', ['Hello world'], messiness=0.5)
        """
        # Validate input characters against supported alphabet
        valid_char_set = set(drawing.alphabet)
        for line_num, line in enumerate(lines):
            # Check line length constraint
            if len(line) > 75:
                raise ValueError(
                    f"Each line must be at most 75 characters. "
                    f"Line {line_num} contains {len(line)} characters"
                )

            # Check character validity
            for char in line:
                if char not in valid_char_set:
                    raise ValueError(
                        f"Invalid character '{char}' detected in line {line_num}. "
                        f"Valid character set is {sorted(valid_char_set)}"
                    )

        # Generate stroke sequences using neural network
        strokes = self._sample(lines, biases=biases, styles=styles)
        
        # Apply messiness and render to SVG
        self._draw(strokes, lines, filename, stroke_colors=stroke_colors, 
                  stroke_widths=stroke_widths, messiness=messiness)

    def _sample(self, lines, biases=None, styles=None):
        """
        Generate stroke sequences from text using the neural network.
        
        Args:
            lines (List[str]): Input text lines
            biases (List[float], optional): Writing pressure controls
            styles (List[int], optional): Style conditioning vectors
            
        Returns:
            List[np.ndarray]: Generated stroke sequences for each line
        """
        num_samples = len(lines)
        max_tsteps = 40 * max([len(i) for i in lines])  # Estimate max stroke steps
        biases = biases if biases is not None else [0.5] * num_samples

        x_prime = np.zeros([num_samples, 1200, 3])
        x_prime_len = np.zeros([num_samples])
        chars = np.zeros([num_samples, 120])
        chars_len = np.zeros([num_samples])

        if styles is not None:
            for i, (cs, style) in enumerate(zip(lines, styles)):
                x_p = np.load('../models/styles/style-{}-strokes.npy'.format(style))
                c_p = np.load('../models/styles/style-{}-chars.npy'.format(style)).tostring().decode('utf-8')

                c_p = str(c_p) + " " + cs
                c_p = drawing.encode_ascii(c_p)
                c_p = np.array(c_p)

                x_prime[i, :len(x_p), :] = x_p
                x_prime_len[i] = len(x_p)
                chars[i, :len(c_p)] = c_p
                chars_len[i] = len(c_p)

        else:
            for i in range(num_samples):
                encoded = drawing.encode_ascii(lines[i])
                chars[i, :len(encoded)] = encoded
                chars_len[i] = len(encoded)

        [samples] = self.nn.session.run(
            [self.nn.sampled_sequence],
            feed_dict={
                self.nn.prime: styles is not None,
                self.nn.x_prime: x_prime,
                self.nn.x_prime_len: x_prime_len,
                self.nn.num_samples: num_samples,
                self.nn.sample_tsteps: max_tsteps,
                self.nn.c: chars,
                self.nn.c_len: chars_len,
                self.nn.bias: biases
            }
        )
        samples = [sample[~np.all(sample == 0.0, axis=1)] for sample in samples]
        return samples

    def _draw(self, strokes, lines, filename, stroke_colors=None, stroke_widths=None, messiness=0.0):
        """
        Render stroke sequences to SVG with messiness effects applied.
        
        Args:
            strokes (List[np.ndarray]): Generated stroke sequences
            lines (List[str]): Original text lines for reference
            filename (str): Output SVG file path
            stroke_colors (List[str], optional): Color for each line
            stroke_widths (List[int], optional): Width for each line  
            messiness (float): Messiness level to apply (0.0-1.5)
        """
        # Set default colors and widths if not specified
        stroke_colors = stroke_colors or ['black'] * len(lines)
        stroke_widths = stroke_widths or [2] * len(lines)

        # SVG canvas configuration
        line_height = 60
        view_width = 1000
        view_height = line_height * (len(strokes) + 1)

        # Create SVG drawing with white background
        dwg = svgwrite.Drawing(filename=filename)
        dwg.viewbox(width=view_width, height=view_height)
        dwg.add(dwg.rect(insert=(0, 0), size=(view_width, view_height), fill='white'))

        initial_coord = np.array([0, -(3*line_height / 4)])
        for offsets, line, color, width in zip(strokes, lines, stroke_colors, stroke_widths):

            if not line:
                initial_coord[1] -= line_height
                continue

            offsets[:, :2] *= 1.5
            strokes = drawing.offsets_to_coords(offsets)
            strokes = drawing.denoise(strokes)
            strokes[:, :2] = drawing.align(strokes[:, :2])
            
            # Apply messiness if specified
            if messiness > 0.0:
                strokes = drawing.add_messiness(strokes, messiness)

            strokes[:, 1] *= -1
            strokes[:, :2] -= strokes[:, :2].min() + initial_coord
            strokes[:, 0] += (view_width - strokes[:, 0].max()) / 2

            prev_eos = 1.0
            p = "M{},{} ".format(0, 0)
            for x, y, eos in zip(*strokes.T):
                p += '{}{},{} '.format('M' if prev_eos == 1.0 else 'L', x, y)
                prev_eos = eos
            path = svgwrite.path.Path(p)
            path = path.stroke(color=color, width=width, linecap='round').fill("none")
            dwg.add(path)

            initial_coord[1] -= line_height

        dwg.save()


if __name__ == '__main__':
    hand = Hand()

    # usage demo
    lines = [
        "Now this is a story all about how",
        "My life got flipped turned upside down",
        "And I'd like to take a minute, just sit right there",
        "I'll tell you how I became the prince of a town called Bel-Air",
    ]
    biases = [.75 for i in lines]
    styles = [9 for i in lines]
    stroke_colors = ['red', 'green', 'black', 'blue']
    stroke_widths = [1, 2, 1, 2]

    hand.write(
        filename='img/usage_demo.svg',
        lines=lines,
        biases=biases,
        styles=styles,
        stroke_colors=stroke_colors,
        stroke_widths=stroke_widths
    )

    # demo number 1 - fixed bias, fixed style
    lines = lyrics.all_star.split("\n")
    biases = [.75 for i in lines]
    styles = [12 for i in lines]

    hand.write(
        filename='img/all_star.svg',
        lines=lines,
        biases=biases,
        styles=styles,
    )

    # demo number 2 - fixed bias, varying style
    lines = lyrics.downtown.split("\n")
    biases = [.75 for i in lines]
    styles = np.cumsum(np.array([len(i) for i in lines]) == 0).astype(int)

    hand.write(
        filename='img/downtown.svg',
        lines=lines,
        biases=biases,
        styles=styles,
    )

    # demo number 3 - varying bias, fixed style
    lines = lyrics.give_up.split("\n")
    biases = .2*np.flip(np.cumsum([len(i) == 0 for i in lines]), 0)
    styles = [7 for i in lines]

    hand.write(
        filename='img/give_up.svg',
        lines=lines,
        biases=biases,
        styles=styles,
    )

    # demo number 4 - messiness feature demonstration (0.0-1.5 range)
    print("Generating messiness demonstration samples...")
    
    # Normal handwriting variations (0.0-1.0)
    normal_scenarios = [
        ("Perfect neat handwriting example", 0.0),
        ("Slight natural variation in writing", 0.4),
        ("Moderate handwriting inconsistency", 0.8),
        ("Maximum normal variation range", 1.0)
    ]
    
    # Adult rush writing (1.0-1.5)
    rush_scenarios = [
        ("Slight time pressure beginning to show", 1.1),
        ("Moderate rushing with compressed letters", 1.3),
        ("Extreme exam time pressure writing", 1.5)
    ]
    
    all_scenarios = normal_scenarios + rush_scenarios
    
    for i, (description, messiness) in enumerate(all_scenarios):
        hand.write(
            filename=f'img/messiness_demo_{messiness}.svg',
            lines=[f"Messiness {messiness}: {description}"],
            biases=[0.75],
            styles=[5],
            messiness=messiness
        )
    
    # Additional comprehensive comparison
    essay_lines = [
        "The examination is challenging but manageable.",
        "Students need to balance accuracy with speed",
        "to complete all questions within the time limit."
    ]
    
    comparison_levels = [0.0, 0.5, 1.0, 1.3, 1.5]
    comparison_descriptions = [
        "Perfect writing",
        "Natural variation", 
        "Maximum normal",
        "Time pressure",
        "Extreme rush"
    ]
    
    for level, desc in zip(comparison_levels, comparison_descriptions):
        full_lines = [f"{desc} (messiness {level}):"] + essay_lines
        hand.write(
            filename=f'img/messiness_comparison_{level}.svg',
            lines=full_lines,
            biases=[0.75] * len(full_lines),
            styles=[7] * len(full_lines),
            messiness=level
        )
