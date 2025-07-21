"""
ONNX/TensorFlow Model Compatibility Module
Provides functions to load and convert models for broader support.
"""

import logging
logging.basicConfig(filename='logs/model_compat.log', level=logging.INFO)

try:
    import onnx
    import tensorflow as tf
except ImportError:
    onnx = None
    tf = None

def load_onnx_model(path):
    if onnx:
        model = onnx.load(path)
        logging.info(f'ONNX model loaded: {path}')
        return model
    else:
        logging.error('ONNX not available')
        return None

def load_tf_model(path):
    if tf:
        model = tf.saved_model.load(path)
        logging.info(f'TensorFlow model loaded: {path}')
        return model
    else:
        logging.error('TensorFlow not available')
        return None
