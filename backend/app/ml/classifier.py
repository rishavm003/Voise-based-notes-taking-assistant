import os
import pickle
import threading
import logging
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
from app.config import settings

logger = logging.getLogger(__name__)

# Singleton instances
_model = None
_tokenizer = None
_lock = threading.Lock()

CATEGORIES = {
    0: "work",
    1: "personal",
    2: "idea",
    3: "reminder"
}

def load_classifier():
    """
    Load CNN model and tokenizer once with thread safety.
    """
    global _model, _tokenizer
    
    if _model is None or _tokenizer is None:
        with _lock:
            if _model is None:
                model_path = os.path.join("app", "ml", "models", "cnn_model.keras")
                if os.path.exists(model_path):
                    logger.info("Loading CNN Classifier model...")
                    _model = tf.keras.models.load_model(model_path)
                else:
                    logger.warning(f"Model file not found at {model_path}. Run training first.")
            
            if _tokenizer is None:
                tokenizer_path = os.path.join("app", "ml", "models", "tokenizer.pkl")
                if os.path.exists(tokenizer_path):
                    logger.info("Loading Tokenizer...")
                    with open(tokenizer_path, "rb") as f:
                        _tokenizer = pickle.load(f)
                else:
                    logger.warning(f"Tokenizer file not found at {tokenizer_path}.")
                    
    return _model, _tokenizer

def predict_category(text: str) -> tuple[str, float]:
    """
    Predict category of the given text using the trained CNN.
    Returns (label, confidence).
    """
    try:
        model, tokenizer = load_classifier()
        if model is None or tokenizer is None:
            return ("uncategorized", 0.0)

        # Preprocessing
        clean_text = text.lower().strip()
        if not clean_text:
            return ("uncategorized", 0.0)

        # Tokenize and Pad
        sequences = tokenizer.texts_to_sequences([clean_text])
        padded = pad_sequences(sequences, maxlen=60, padding="post", truncating="post")

        # Predict
        predictions = model.predict(padded, verbose=0)[0]
        idx = np.argmax(predictions)
        confidence = float(predictions[idx])

        if confidence < 0.5:
            return ("uncategorized", round(confidence, 3))

        label = CATEGORIES.get(idx, "uncategorized")
        return (label, round(confidence, 3))

    except Exception as e:
        logger.error(f"Classification error: {e}")
        return ("uncategorized", 0.0)
