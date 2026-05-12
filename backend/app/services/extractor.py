import spacy
from typing import Dict, Any, List
from collections import Counter
from app.config import settings

# Global for lazy loading
_nlp = None

def load_spacy_model():
    """
    Loads spacy en_core_web_sm model.
    """
    global _nlp
    if _nlp is None:
        try:
            print(f"Loading spaCy model: {settings.SPACY_MODEL}...")
            _nlp = spacy.load(settings.SPACY_MODEL)
        except OSError:
            raise ImportError(
                f"spaCy model '{settings.SPACY_MODEL}' not found. Run: python -m spacy download {settings.SPACY_MODEL}"
            )
    return _nlp

def extract_keywords(text: str) -> Dict[str, Any]:
    """
    Extracts keywords, named entities, and noun phrases from text.
    """
    try:
        nlp = load_spacy_model()
        doc = nlp(text)
        
        # 1. Named Entity Extraction
        # PERSON, ORG, GPE, DATE, TIME, PRODUCT, EVENT
        valid_labels = {"PERSON", "ORG", "GPE", "DATE", "TIME", "PRODUCT", "EVENT"}
        entities = []
        for ent in doc.ents:
            if ent.label_ in valid_labels:
                entities.append({
                    "text": ent.text.strip(),
                    "label": ent.label_
                })
        
        # Deduplicate entities
        seen_entities = set()
        unique_entities = []
        for ent in entities:
            key = (ent["text"].lower(), ent["label"])
            if key not in seen_entities:
                seen_entities.add(key)
                unique_entities.append(ent)

        # 2. Noun Phrase Extraction (2-5 words)
        noun_phrases = []
        for chunk in doc.noun_chunks:
            words = chunk.text.lower().split()
            if 2 <= len(words) <= 5:
                # Check if it's not just stopwords
                if not all(nlp.vocab[w].is_stop for w in words):
                    noun_phrases.append(chunk.text.lower().strip())
        noun_phrases = list(set(noun_phrases))

        # 3. Important Single Words
        # Not stopword, not punct, not space, length >= 4
        words = [
            token.text.lower() for token in doc 
            if not token.is_stop and not token.is_punct and not token.is_space and len(token.text) >= 4
        ]
        word_freq = Counter(words)
        top_words = [word for word, count in word_freq.most_common(10)]

        # 4. Combine and deduplicate
        combined_keywords = set()
        # Add entity texts
        for ent in unique_entities:
            combined_keywords.add(ent["text"].lower())
        # Add noun phrases
        for phrase in noun_phrases:
            combined_keywords.add(phrase)
        # Add top single words
        for word in top_words:
            combined_keywords.add(word)
            
        final_keywords = list(combined_keywords)
        final_keywords.sort()
        
        return {
            "keywords": final_keywords[:15],  # Limit to top 15
            "entities": unique_entities,
            "noun_phrases": noun_phrases
        }
    except Exception as e:
        print(f"Keyword extraction error: {str(e)}")
        return {"keywords": [], "entities": [], "noun_phrases": []}
