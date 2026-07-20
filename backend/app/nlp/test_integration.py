import os
import sys

# Ensure backend root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

# Set mock env vars
os.environ["FIREBASE_CREDENTIALS_JSON"] = '{"type": "service_account", "project_id": "mock"}'

def run_test():
    print("=== STARTING INTEGRATION TEST ===")
    
    # 1. Run local model training
    print("\n--- Step 1: Training local classifier ---")
    from backend.app.nlp.train_model import train_local_model
    train_local_model()
    
    # Verify model files are created
    model_dir = os.path.join(os.path.dirname(__file__), "models")
    vec_path = os.path.join(model_dir, "vectorizer.pkl")
    model_path = os.path.join(model_dir, "model.pkl")
    json_path = os.path.join(model_dir, "intent_model.json")
    
    assert os.path.exists(vec_path), "vectorizer.pkl was not saved!"
    assert os.path.exists(model_path), "model.pkl was not saved!"
    assert os.path.exists(json_path), "intent_model.json was not saved!"
    print("Verification: All model weights (pickle + JSON) successfully created!")

    # 2. Reload NLPProcessor to load the new model
    print("\n--- Step 2: Testing model loading & prediction in NLPProcessor ---")
    from backend.app.nlp.processor import NLPProcessor
    processor = NLPProcessor()
    
    # Verify models are loaded
    assert processor.vectorizer is not None, "Vectorizer was not loaded!"
    assert processor.classifier is not None, "Classifier was not loaded!"
    print("Verification: NLPProcessor successfully loaded local model weights!")

    # 3. Predict intents for various queries
    test_cases = [
        ("send an email to priya@office.com about the project", "SEND_EMAIL"),
        ("find document metrics.csv in my workspace", "FIND_DOCUMENT"),
        ("browse news on hacker news website", "AUTOMATE_BROWSER"),
        ("schedule meeting with team at 4pm tomorrow", "PLAN_SCHEDULE"),
        ("compress directory workspace and create backup", "MANAGE_FILES"),
    ]

    print("\n--- Step 3: Verifying inference accuracy ---")
    for text, expected_intent in test_cases:
        res = processor.process_command(text)
        pred_intent = res["intent"]
        print(f"Query: '{text}'")
        print(f"  Expected: {expected_intent}")
        print(f"  Predicted: {pred_intent} (Confidence: {res['intent_confidence']*100:.1f}%)")
        assert pred_intent == expected_intent, f"Mismatch! Expected {expected_intent}, got {pred_intent}"
        print("  [OK]")

    print("\n=== INTEGRATION TEST PASSED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_test()
