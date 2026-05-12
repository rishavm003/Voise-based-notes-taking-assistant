import os
import pickle
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
from typing import Dict, Any, Tuple
from app.config import settings

# Global variables for lazy loading
_model = None
_tokenizer = None

CATEGORIES = {0: "work", 1: "personal", 2: "idea", 3: "reminder"}

def load_classifier() -> Tuple[Any, Any]:
    """
    Loads cnn_model.h5 and tokenizer.pkl from models directory.
    Caches in module-level globals after first load.
    """
    global _model, _tokenizer
    
    model_path = settings.CNN_MODEL_PATH
    tokenizer_path = settings.TOKENIZER_PATH

    if not os.path.exists(model_path) or not os.path.exists(tokenizer_path):
        raise FileNotFoundError(
            "CNN model or tokenizer not found. Run python app/ml/train_model.py first."
        )

    if _model is None:
        print("Loading CNN classifier model...")
        _model = tf.keras.models.load_model(model_path)
    
    if _tokenizer is None:
        print("Loading tokenizer...")
        with open(tokenizer_path, 'rb') as f:
            _tokenizer = pickle.load(f)
            
    return _model, _tokenizer

def predict_category(text: str) -> Dict[str, Any]:
    """
    Takes raw transcript text and predicts its category using the CNN model.
    """
    try:
        model, tokenizer = load_classifier()
        
        # Preprocessing
        text = text.lower()
        sequences = tokenizer.texts_to_sequences([text])
        padded = pad_sequences(sequences, maxlen=50, padding="post")
        
        # Prediction
        predictions = model.predict(padded)[0]
        top_idx = np.argmax(predictions)
        confidence = float(predictions[top_idx])
        
        category = CATEGORIES.get(top_idx, "uncategorized")
        
        all_scores = {CATEGORIES[i]: float(predictions[i]) for i in range(len(CATEGORIES))}
        
        return {
            "category": category,
            "confidence": confidence,
            "all_scores": all_scores
        }
    except Exception as e:
        print(f"Classification error: {str(e)}")
        return {"category": "uncategorized", "confidence": 0.0, "all_scores": {}}
