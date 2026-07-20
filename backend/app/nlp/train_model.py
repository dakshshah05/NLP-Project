import os
import json
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

def train_local_model():
    print("=== STARTING LOCAL MODEL TRAINING ===")
    
    # 1. Load data_full.json
    dataset_path = 'D:\\NLP\\data_full.json'
    if not os.path.exists(dataset_path):
        print(f"ERROR: Dataset not found at {dataset_path}")
        return
        
    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
        
    # Supported categories
    target_intents = ["SEND_EMAIL", "FIND_DOCUMENT", "AUTOMATE_BROWSER", "PLAN_SCHEDULE", "MANAGE_FILES"]
    
    # Map CLINC150 intents to AURA AI's 5 core intents
    intent_mapping = {
        # PLAN_SCHEDULE
        "calendar": "PLAN_SCHEDULE",
        "calendar_update": "PLAN_SCHEDULE",
        "meeting_schedule": "PLAN_SCHEDULE",
        "schedule_meeting": "PLAN_SCHEDULE",
        "reminder": "PLAN_SCHEDULE",
        "reminder_update": "PLAN_SCHEDULE",
        "timer": "PLAN_SCHEDULE",
        "alarm": "PLAN_SCHEDULE",
        "todo_list": "PLAN_SCHEDULE",
        "todo_list_update": "PLAN_SCHEDULE",
        
        # AUTOMATE_BROWSER
        "weather": "AUTOMATE_BROWSER",
        "translate": "AUTOMATE_BROWSER",
        "definition": "AUTOMATE_BROWSER",
        "restaurant_reviews": "AUTOMATE_BROWSER",
        "restaurant_suggestion": "AUTOMATE_BROWSER",
        "directions": "AUTOMATE_BROWSER",
        "traffic": "AUTOMATE_BROWSER",
        "gas": "AUTOMATE_BROWSER",
        "exchange_rate": "AUTOMATE_BROWSER",
        
        # SEND_EMAIL
        "text": "SEND_EMAIL",
        "make_call": "SEND_EMAIL",
        
        # MANAGE_FILES
        "sync_device": "MANAGE_FILES",
        "reset_settings": "MANAGE_FILES",
        "shopping_list": "MANAGE_FILES",
        "shopping_list_update": "MANAGE_FILES",
        
        # FIND_DOCUMENT
        "w2": "FIND_DOCUMENT",
        "taxes": "FIND_DOCUMENT",
        "insurance": "FIND_DOCUMENT",
        "insurance_change": "FIND_DOCUMENT"
    }

    # Extract mapped training samples
    X_raw = []
    y_raw = []
    
    for split in ['train', 'val', 'test']:
        for text, orig_intent in dataset.get(split, []):
            if orig_intent in intent_mapping:
                X_raw.append(text)
                y_raw.append(intent_mapping[orig_intent])

    # 2. Add custom template-based keyword samples for 100% precision on AURA AI commands
    # (Covers English, Hindi, and Kannada patterns)
    custom_samples = [
        # SEND_EMAIL
        ("send an email to priya@office.com", "SEND_EMAIL"),
        ("email john details of the nlp project", "SEND_EMAIL"),
        ("mail quarterly reports to admin", "SEND_EMAIL"),
        ("write to supervisor about delay", "SEND_EMAIL"),
        ("ईमेल भेजें रमेश को", "SEND_EMAIL"),
        ("मेल सेंड करो", "SEND_EMAIL"),
        ("ಇಮೇಲ್ ಕಳುಹಿಸು ರಮೇಶ್ ಗೆ", "SEND_EMAIL"),
        
        # FIND_DOCUMENT
        ("find document metrics.csv", "FIND_DOCUMENT"),
        ("search document on deep learning", "FIND_DOCUMENT"),
        ("locate paper on transformers", "FIND_DOCUMENT"),
        ("get document draft.pdf", "FIND_DOCUMENT"),
        ("find project report file", "FIND_DOCUMENT"),
        ("ದಸ್ತಾವೇಜು ಫೈಲ್ ಹುಡುಕು", "FIND_DOCUMENT"),
        ("फाइल ढूंढें", "FIND_DOCUMENT"),
        
        # AUTOMATE_BROWSER
        ("browse news on hacker news", "AUTOMATE_BROWSER"),
        ("search web for latest models", "AUTOMATE_BROWSER"),
        ("open page google.com", "AUTOMATE_BROWSER"),
        ("download from url https://example.com/file", "AUTOMATE_BROWSER"),
        ("वेबसाइट गूगल खोलो", "AUTOMATE_BROWSER"),
        ("ವೆಬ್ ಸೈಟ್ ಬ್ರೌಸ್ ಮಾಡಿ", "AUTOMATE_BROWSER"),
        
        # PLAN_SCHEDULE
        ("schedule meeting with team at 4pm", "PLAN_SCHEDULE"),
        ("set a reminder to study stemming", "PLAN_SCHEDULE"),
        ("plan my schedule for tomorrow", "PLAN_SCHEDULE"),
        ("calendar check schedule", "PLAN_SCHEDULE"),
        ("ಮೀಟಿಂಗ್ ಶೆಡ್ಯೂಲ್ ಮಾಡಿ", "PLAN_SCHEDULE"),
        ("बैठक निर्धारित करें", "PLAN_SCHEDULE"),
        
        # MANAGE_FILES
        ("backup files to cloud", "MANAGE_FILES"),
        ("compress directory workspace", "MANAGE_FILES"),
        ("copy file test.txt to target", "MANAGE_FILES"),
        ("move folder documents to archive", "MANAGE_FILES"),
        ("delete archive file", "MANAGE_FILES"),
        ("ಫೋಲ್ಡರ್ ಬ್ಯಾಕಪ್ ಮಾಡಿ", "MANAGE_FILES"),
        ("फ़ाइल कॉपी करें", "MANAGE_FILES")
    ]
    
    # Replicate custom samples to boost their weight
    for text, intent in custom_samples:
        for _ in range(25):
            X_raw.append(text)
            y_raw.append(intent)

    # 3. Train Test Split
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X_raw, y_raw, test_size=0.15, random_state=42, stratify=y_raw)
    
    print(f"Total samples for training: {len(X_train)}")
    print(f"Total samples for validation/testing: {len(X_test)}")
    
    # 4. Fit TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=4000, sublinear_tf=True)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    # 5. Fit Logistic Regression Classifier
    print("Fitting Logistic Regression model...")
    model = LogisticRegression(C=2.0, max_iter=1000, class_weight='balanced')
    model.fit(X_train_vec, y_train)
    
    # 6. Evaluate model
    y_pred = model.predict(X_test_vec)
    acc = accuracy_score(y_test, y_pred)
    print(f"Validation Accuracy: {acc*100:.2f}%")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=target_intents))
    
    # 7. Serialize models
    model_dir = 'd:\\NLP\\backend\\app\\nlp\\models'
    os.makedirs(model_dir, exist_ok=True)
    
    vec_path = os.path.join(model_dir, 'vectorizer.pkl')
    model_path = os.path.join(model_dir, 'model.pkl')
    json_path = os.path.join(model_dir, 'intent_model.json')
    
    print(f"Saving vectorizer to: {vec_path}")
    with open(vec_path, 'wb') as f:
        pickle.dump(vectorizer, f)
        
    print(f"Saving classifier model to: {model_path}")
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)

    # Save as JSON for Hugging Face compatibility (text-based, bypasses binary blocks)
    print(f"Saving JSON model to: {json_path}")
    model_json = {
        "classes": model.classes_.tolist(),
        "coef": model.coef_.tolist(),
        "intercept": model.intercept_.tolist(),
        "idf": vectorizer.idf_.tolist(),
        "vocabulary": {word: int(idx) for word, idx in vectorizer.vocabulary_.items()},
        "ngram_range": vectorizer.ngram_range,
        "sublinear_tf": vectorizer.sublinear_tf
    }
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(model_json, f)
        
    print("=== MODEL TRAINING COMPLETED ===")

if __name__ == "__main__":
    train_local_model()
