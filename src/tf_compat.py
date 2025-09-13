"""TensorFlow compatibility layer for TF 1.x code running on TF 2.x"""

import tensorflow as tf

# Disable eager execution to run TF 1.x style code
tf.compat.v1.disable_eager_execution()

# Enable TF 1.x behavior
tf.compat.v1.disable_v2_behavior()