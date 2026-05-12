import spacy
import logging
import threading
import string
from app.config import settings

logger = logging.getLogger(__name__)

# Singleton
_nlp = None
_lock = threading.Lock()

def load_spacy_model():
    """
    Load spaCy model once with thread safety.
    """
    global _nlp
    if _nlp is None:
        with _lock:
            if _nlp is None:
                try:
                    logger.info(f"Loading spaCy model ({settings.SPACY_MODEL})...")
                    _nlp = spacy.load(settings.SPACY_MODEL)
                except OSError:
                    logger.error(f"Model {settings.SPACY_MODEL} not found. Run: python -m spacy download {settings.SPACY_MODEL}")
    return _nlp

def extract_keywords(text: str) -> list[str]:
    """
    Extract keywords using NER and Noun Chunking.
    Returns top 10 keywords by length.
    """
    try:
        nlp = load_spacy_model()
        if nlp is None:
            return []

        doc = nlp(text)
        results = set()

        # Approach 1: Named Entities
        valid_labels = {"PERSON", "ORG", "GPE", "PRODUCT", "EVENT", "WORK_OF_ART", "DATE"}
        for ent in doc.ents:
            if ent.label_ in valid_labels:
                clean_ent = ent.text.lower().strip().translate(str.maketrans("", "", string.punctuation))
                if clean_ent:
                    results.add(clean_ent)

        # Approach 2: Noun Chunks
        for chunk in doc.noun_chunks:
            # Filter: must contain a NOUN or PROPN, skip stops and single chars
            if any(t.pos_ in {"NOUN", "PROPN"} for t in chunk) and not all(t.is_stop for t in chunk):
                clean_chunk = chunk.text.lower().strip().translate(str.maketrans("", "", string.punctuation))
                if len(clean_chunk) > 1:
                    results.add(clean_chunk)

        # Combine, sort by length (descending) and take top 10
        sorted_results = sorted(list(results), key=len, reverse=True)
        return sorted_results[:10]

    except Exception as e:
        logger.error(f"Extraction error: {e}")
        return []
