import time
from app.ml.classifier import predict_category
from app.ml.extractor import extract_keywords

test_sentences = [
    "schedule a team standup for monday 10am to discuss the product roadmap",
    "buy milk eggs bread and some fresh vegetables for dinner tonight",
    "what if we build a smart mirror that helps you choose outfits using ai",
    "dont forget to return the library books by friday to avoid the late fee",
    "send the invoice to the client by the end of the day",
    "call mom on sunday for her birthday and book the dinner table",
    "startup idea connecting freelance developers with local startups",
    "remind me to take my vitamins after breakfast every morning"
]

def run_test():
    print("="*60)
    print("SMART VOICE NOTES ML PIPELINE TEST")
    print("="*60)
    
    print(f"{'Sample Sentence':<45} | {'Category':<10} | {'Conf':<5}")
    print("-" * 65)
    
    for text in test_sentences:
        start_time = time.time()
        category, confidence = predict_category(text)
        keywords = extract_keywords(text)
        elapsed = (time.time() - start_time) * 1000
        
        print(f"{text[:44]:<45} | {category:<10} | {confidence:<5.2f}")
        print(f"  └─ Keywords: {', '.join(keywords[:5])}")
        print(f"  └─ Latency: {elapsed:.2f}ms")
        print("-" * 65)

if __name__ == "__main__":
    try:
        run_test()
    except Exception as e:
        print(f"Error running pipeline test: {e}")
        print("Tip: Make sure you have trained the model first: python app/ml/train_model.py")
