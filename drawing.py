from __future__ import print_function
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import savgol_filter
from scipy.interpolate import interp1d


alphabet = [
    '\x00', ' ', '!', '"', '#', "'", '(', ')', ',', '-', '.',
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';',
    '?', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K',
    'L', 'M', 'N', 'O', 'P', 'R', 'S', 'T', 'U', 'V', 'W', 'Y',
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l',
    'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x',
    'y', 'z'
]
alphabet_ord = list(map(ord, alphabet))
alpha_to_num = defaultdict(int, list(map(reversed, enumerate(alphabet))))
num_to_alpha = dict(enumerate(alphabet_ord))

MAX_STROKE_LEN = 1200
MAX_CHAR_LEN = 75


def align(coords):
    """
    corrects for global slant/offset in handwriting strokes
    """
    coords = np.copy(coords)
    X, Y = coords[:, 0].reshape(-1, 1), coords[:, 1].reshape(-1, 1)
    X = np.concatenate([np.ones([X.shape[0], 1]), X], axis=1)
    offset, slope = np.linalg.inv(X.T.dot(X)).dot(X.T).dot(Y).squeeze()
    theta = np.arctan(slope)
    rotation_matrix = np.array(
        [[np.cos(theta), -np.sin(theta)],
         [np.sin(theta), np.cos(theta)]]
    )
    coords[:, :2] = np.dot(coords[:, :2], rotation_matrix) - offset
    return coords


def skew(coords, degrees):
    """
    skews strokes by given degrees
    """
    coords = np.copy(coords)
    theta = degrees * np.pi/180
    A = np.array([[np.cos(-theta), 0], [np.sin(-theta), 1]])
    coords[:, :2] = np.dot(coords[:, :2], A)
    return coords


def stretch(coords, x_factor, y_factor):
    """
    stretches strokes along x and y axis
    """
    coords = np.copy(coords)
    coords[:, :2] *= np.array([x_factor, y_factor])
    return coords


def add_noise(coords, scale):
    """
    adds gaussian noise to strokes
    """
    coords = np.copy(coords)
    coords[1:, :2] += np.random.normal(loc=0.0, scale=scale, size=coords[1:, :2].shape)
    return coords


def add_messiness(coords, messiness_factor, char_boundaries=None):
    """
    Adds realistic handwriting messiness to simulate normal to rushed adult writing.
    
    Args:
        coords: stroke coordinates array (N, 3) with [x, y, eos]
        messiness_factor: float 0.0-1.5, amount of messiness to apply
                         0.0-1.0: Normal handwriting variations
                         1.0-1.5: Adult rushed writing (exam conditions)
        char_boundaries: optional list of indices where characters start/end
    
    Returns:
        modified coordinates with messiness applied
    """
    if messiness_factor <= 0.0:
        return coords
    
    coords = np.copy(coords).astype(np.float64)
    
    # Get stroke segments (split at pen lifts)
    stroke_ends = np.where(coords[:, 2] == 1)[0]
    stroke_starts = np.concatenate([[0], stroke_ends[:-1] + 1])
    
    # Determine if we're in normal (0.0-1.0) or rush mode (1.0-1.5)
    if messiness_factor <= 1.0:
        # Normal handwriting variations (0.0-1.0)
        normal_factor = messiness_factor
        rush_factor = 0.0
    else:
        # Adult rush writing (1.0-1.5)
        normal_factor = 1.0
        rush_factor = messiness_factor - 1.0
    
    # Apply effects to each stroke segment
    for start, end in zip(stroke_starts, stroke_ends + 1):
        stroke_coords = coords[start:end]
        stroke_length = len(stroke_coords)
        
        if stroke_length < 2:
            continue
        
        # 1. Forward lean (natural slant from writing speed)
        base_lean = normal_factor * np.random.uniform(-2, 8) * np.pi / 180
        rush_lean = rush_factor * np.random.uniform(3, 10) * np.pi / 180  # Additional lean when rushing
        total_lean = base_lean + rush_lean
        
        if abs(total_lean) > 0.01:
            center_x = np.mean(stroke_coords[:, 0])
            center_y = np.mean(stroke_coords[:, 1])
            
            stroke_coords[:, 0] -= center_x
            stroke_coords[:, 1] -= center_y
            
            cos_a, sin_a = np.cos(total_lean), np.sin(total_lean)
            x_new = stroke_coords[:, 0] * cos_a - stroke_coords[:, 1] * sin_a
            y_new = stroke_coords[:, 0] * sin_a + stroke_coords[:, 1] * cos_a
            
            stroke_coords[:, 0] = x_new + center_x
            stroke_coords[:, 1] = y_new + center_y
        
        # 2. Baseline drift (gradual up/down movement)
        baseline_drift = normal_factor * np.random.uniform(-1, 1)
        rush_drift = rush_factor * np.random.uniform(-2, 2)  # More drift when rushing
        stroke_coords[:, 1] += baseline_drift + rush_drift
        
        # 3. Letter height variations (inconsistent sizing)
        base_size_var = normal_factor * np.random.uniform(-0.08, 0.08)
        rush_size_var = rush_factor * np.random.uniform(-0.12, 0.12)  # More variation when rushing
        size_variation = 1 + base_size_var + rush_size_var
        
        center_y = np.mean(stroke_coords[:, 1])
        stroke_coords[:, 1] = (stroke_coords[:, 1] - center_y) * size_variation + center_y
        
        # 4. Horizontal compression (narrower letters from speed)
        base_compression = normal_factor * 0.05
        rush_compression = rush_factor * 0.15  # More compression when rushing
        compression = 1 - (base_compression + rush_compression)
        
        center_x = np.mean(stroke_coords[:, 0])
        stroke_coords[:, 0] = (stroke_coords[:, 0] - center_x) * compression + center_x
        
        # 5. Pen pressure fluctuation (stroke width variation simulation)
        if stroke_length > 3:
            pressure_var = normal_factor * 0.1 + rush_factor * 0.2
            # Simulate by adding slight coordinate noise (represents pressure changes)
            pressure_noise = np.random.normal(0, pressure_var, (stroke_length, 2))
            stroke_coords[:, :2] += pressure_noise * 0.3  # Subtle effect
        
        coords[start:end] = stroke_coords
    
    # 6. Letter and word spacing irregularity
    if len(stroke_starts) > 1:
        for i in range(1, len(stroke_starts)):
            # Normal spacing variation
            base_spacing = normal_factor * np.random.uniform(-2, 4)
            # Rush spacing variation (more erratic)
            rush_spacing = rush_factor * np.random.uniform(-4, 8)
            total_spacing = base_spacing + rush_spacing
            coords[stroke_starts[i]:] += [total_spacing, 0, 0]
    
    # 7. Gradual baseline drift across entire text (rush mode only)
    if rush_factor > 0 and len(coords) > 10:
        # Create subtle curve across the entire line
        x_range = coords[-1, 0] - coords[0, 0]
        if x_range > 0:
            drift_amplitude = rush_factor * np.random.uniform(-3, 3)
            for i in range(len(coords)):
                progress = (coords[i, 0] - coords[0, 0]) / x_range
                coords[i, 1] += drift_amplitude * np.sin(progress * np.pi)
    
    return coords


def encode_ascii(ascii_string):
    """
    encodes ascii string to array of ints
    """
    return np.array(list(map(lambda x: alpha_to_num[x], ascii_string)) + [0])


def denoise(coords):
    """
    smoothing filter to mitigate some artifacts of the data collection
    """
    coords = np.split(coords, np.where(coords[:, 2] == 1)[0] + 1, axis=0)
    new_coords = []
    for stroke in coords:
        if len(stroke) != 0:
            x_new = savgol_filter(stroke[:, 0], 7, 3, mode='nearest')
            y_new = savgol_filter(stroke[:, 1], 7, 3, mode='nearest')
            xy_coords = np.hstack([x_new.reshape(-1, 1), y_new.reshape(-1, 1)])
            stroke = np.concatenate([xy_coords, stroke[:, 2].reshape(-1, 1)], axis=1)
            new_coords.append(stroke)

    coords = np.vstack(new_coords)
    return coords


def interpolate(coords, factor=2):
    """
    interpolates strokes using cubic spline
    """
    coords = np.split(coords, np.where(coords[:, 2] == 1)[0] + 1, axis=0)
    new_coords = []
    for stroke in coords:

        if len(stroke) == 0:
            continue

        xy_coords = stroke[:, :2]

        if len(stroke) > 3:
            f_x = interp1d(np.arange(len(stroke)), stroke[:, 0], kind='cubic')
            f_y = interp1d(np.arange(len(stroke)), stroke[:, 1], kind='cubic')

            xx = np.linspace(0, len(stroke) - 1, factor*(len(stroke)))
            yy = np.linspace(0, len(stroke) - 1, factor*(len(stroke)))

            x_new = f_x(xx)
            y_new = f_y(yy)

            xy_coords = np.hstack([x_new.reshape(-1, 1), y_new.reshape(-1, 1)])

        stroke_eos = np.zeros([len(xy_coords), 1])
        stroke_eos[-1] = 1.0
        stroke = np.concatenate([xy_coords, stroke_eos], axis=1)
        new_coords.append(stroke)

    coords = np.vstack(new_coords)
    return coords


def normalize(offsets):
    """
    normalizes strokes to median unit norm
    """
    offsets = np.copy(offsets)
    offsets[:, :2] /= np.median(np.linalg.norm(offsets[:, :2], axis=1))
    return offsets


def coords_to_offsets(coords):
    """
    convert from coordinates to offsets
    """
    offsets = np.concatenate([coords[1:, :2] - coords[:-1, :2], coords[1:, 2:3]], axis=1)
    offsets = np.concatenate([np.array([[0, 0, 1]]), offsets], axis=0)
    return offsets


def offsets_to_coords(offsets):
    """
    convert from offsets to coordinates
    """
    return np.concatenate([np.cumsum(offsets[:, :2], axis=0), offsets[:, 2:3]], axis=1)


def draw(
        offsets,
        ascii_seq=None,
        align_strokes=True,
        denoise_strokes=True,
        interpolation_factor=None,
        save_file=None
):
    strokes = offsets_to_coords(offsets)

    if denoise_strokes:
        strokes = denoise(strokes)

    if interpolation_factor is not None:
        strokes = interpolate(strokes, factor=interpolation_factor)

    if align_strokes:
        strokes[:, :2] = align(strokes[:, :2])

    fig, ax = plt.subplots(figsize=(12, 3))

    stroke = []
    for x, y, eos in strokes:
        stroke.append((x, y))
        if eos == 1:
            coords = zip(*stroke)
            ax.plot(coords[0], coords[1], 'k')
            stroke = []
    if stroke:
        coords = zip(*stroke)
        ax.plot(coords[0], coords[1], 'k')
        stroke = []

    ax.set_xlim(-50, 600)
    ax.set_ylim(-40, 40)

    ax.set_aspect('equal')
    plt.tick_params(
        axis='both',
        left='off',
        top='off',
        right='off',
        bottom='off',
        labelleft='off',
        labeltop='off',
        labelright='off',
        labelbottom='off'
    )

    if ascii_seq is not None:
        if not isinstance(ascii_seq, str):
            ascii_seq = ''.join(list(map(chr, ascii_seq)))
        plt.title(ascii_seq)

    if save_file is not None:
        plt.savefig(save_file)
        print('saved to {}'.format(save_file))
    else:
        plt.show()
    plt.close('all')
