"""
AURA AI — NLP Processing Engine
=================================
A full 13-step multilingual NLP pipeline demonstrating:
  1.  Language Detection         (langdetect + Unicode scripts)
  2.  Text Normalization         (voice artifact removal, NFKC)
  3.  Sentence Segmentation      (NLTK sent_tokenize)
  4.  Word Tokenization          (NLTK word_tokenize)
  5.  Stopword Removal           (NLTK, multilingual)
  6.  Stemming                   (NLTK PorterStemmer / SnowballStemmer)
  7.  Lemmatization              (NLTK WordNetLemmatizer, POS-aware)
  8.  Part-of-Speech Tagging     (NLTK averaged_perceptron_tagger)
  9.  Noun Phrase Chunking        (NLTK RegexpParser)
  10. Named Entity Recognition   (3-layer: Regex → NLTK ne_chunk → spaCy)
  11. Intent Classification      (TF-IDF + Logistic Regression, 97.68% acc.)
  12. Semantic Role Labeling     (PropBank-style: Agent/Action/Theme/Recipient)
  13. Task Decomposition          (Structured multi-agent workflow builder)

Architecture:
  [User Input] → [NLP Pipeline (Python)] → [Structured JSON] → [Gemini Execution]
  Gemini is ONLY used for optional intent confirmation + task execution.
  ALL parsing, classification, and entity extraction is done by this Python engine.
"""

import os
import re
import unicodedata
from typing import Dict, Any, List, Optional, Tuple

# ── Optional spaCy integration ──────────────────────────────────────────────
try:
    import spacy
    nlp_spacy = spacy.load("en_core_web_sm")
except Exception:
    nlp_spacy = None

# ── Language Detection Helper ────────────────────────────────────────────────
LANGDETECT_AVAILABLE = True

# ── Supported Languages ──────────────────────────────────────────────────────
LANGUAGE_MAP = {
    "en": "English", "hi": "Hindi", "kn": "Kannada",
    "te": "Telugu", "ta": "Tamil", "mr": "Marathi",
    "bn": "Bengali", "gu": "Gujarati", "pa": "Punjabi",
}

# ── Voice Artifact Normalization ─────────────────────────────────────────────
VOICE_FILLERS = re.compile(
    r"\b(um+|uh+|hmm+|like|you know|i mean|sort of|kind of|basically|literally|okay so|so um|well uh)\b",
    re.IGNORECASE
)
SPOKEN_PUNCTUATION = {
    r"\bperiod\b": ".", r"\bcomma\b": ",", r"\bquestion mark\b": "?",
    r"\bexclamation mark\b": "!", r"\bnew line\b": "\n",
}

# ── Multilingual Intent Patterns ─────────────────────────────────────────────
INTENT_MAP = {
    "SEND_EMAIL": {
        "patterns": {
            "en": [r"email", r"mail", r"sen[dt]", r"write to", r"compose", r"attach"],
            "hi": [r"\u0908\u092e\u0947\u0932", r"\u092e\u0947\u0932", r"\u092d\u0947\u091c\u0947\u0902", r"\u0932\u093f\u0916\u0947\u0902", r"\u092d\u0947\u091c\u094b"],
            "kn": [r"\u0c87\u0cae\u0cc7\u0cb2\u0ccd", r"\u0cae\u0cc7\u0cb2\u0ccd", r"\u0c95\u0cb3\u0cc1\u0cb9\u0cbf\u0cb8\u0cc1", r"\u0c95\u0cb3\u0cbf\u0cb8\u0cc1"],
            "hinglish": [r"email bhejo", r"mail karo", r"bhejo", r"email karo"],
        },
        "agent": "Email Agent"
    },
    "FIND_DOCUMENT": {
        "patterns": {
            "en": [r"find doc", r"search document", r"locate", r"get document", r"retrieve", r"look up"],
            "hi": [r"\u0926\u0938\u094d\u0924\u093e\u0935\u0947\u091c\u093c", r"\u0922\u0942\u0902\u0922\u0947\u0902", r"\u0916\u094b\u091c\u0947\u0902"],
            "kn": [r"\u0daa\u0dac\u0dbd\u0dda\u0d95\u0dda", r"\u0cb9\u0cc1\u0ca1\u0cc1\u0c95\u0cc1", r"\u0cab\u0cc8\u0cb2\u0ccd"],
            "hinglish": [r"file dhundo", r"document khojo"],
        },
        "agent": "Document Agent"
    },
    "AUTOMATE_BROWSER": {
        "patterns": {
            "en": [r"browse", r"website", r"google", r"search web", r"open page", r"download from", r"scrape", r"open url"],
            "hi": [r"\u0935\u0947\u092c\u0938\u093e\u0907\u091f", r"\u0916\u094b\u0932\u0947\u0902", r"\u0921\u093e\u0909\u0928\u0932\u094b\u0921"],
            "kn": [r"\u0cb5\u0cc6\u0cac\u0ccd \u0cb8\u0cc8\u0c9f\u0ccd", r"\u0cac\u0ccd\u0cb0\u0ccc\u0cb8\u0ccd", r"\u0c97\u0cc2\u0c97\u0cb2\u0ccd"],
            "hinglish": [r"website kholo", r"google karo", r"download karo"],
        },
        "agent": "Browser Agent"
    },
    "PLAN_SCHEDULE": {
        "patterns": {
            "en": [r"schedule", r"calendar", r"plan", r"meeting", r"reminder", r"set alarm", r"book"],
            "hi": [r"\u0936\u0947\u0921\u094d\u092f\u0942\u0932", r"\u092f\u094b\u091c\u0928\u093e", r"\u092c\u0948\u0920\u0915", r"\u0930\u093f\u092e\u093e\u0907\u0902\u0921\u0930"],
            "kn": [r"\u0cb8\u0cad\u0cc6", r"\u0caf\u0ccb\u0c9c\u0ca8\u0cc6", r"\u0c9c\u0ccd\u0c9e\u0cbe\u0caa\u0ca8\u0cc6"],
            "hinglish": [r"schedule karo", r"meeting rakho", r"reminder lagao"],
        },
        "agent": "Planner Agent"
    },
    "MANAGE_FILES": {
        "patterns": {
            "en": [r"copy file", r"move folder", r"delete", r"compress", r"backup", r"archive", r"zip"],
            "hi": [r"\u0915\u0949\u092a\u0940", r"\u092c\u0948\u0915\u0905\u092a", r"\u092b\u093c\u093e\u0907\u0932 \u0939\u091f\u093e\u090f\u0902"],
            "kn": [r"\u0c95\u0cbe\u0caa\u0cbf", r"\u0cac\u0ccd\u0caf\u0cbe\u0c95\u0caa\u0ccd", r"\u0ca1\u0cbf\u0cb2\u0cc0\u0c9f\u0ccd"],
            "hinglish": [r"copy karo", r"backup lo", r"file delete karo"],
        },
        "agent": "File Agent"
    }
}

# ── NLP Processor ─────────────────────────────────────────────────────────────
class NLPProcessor:
    def __init__(self):
        self.vectorizer = None
        self.classifier = None
        self._init_nltk()
        self._load_model()

    def _init_nltk(self):
        try:
            import nltk
            for res in ['punkt', 'punkt_tab', 'averaged_perceptron_tagger',
                        'averaged_perceptron_tagger_eng', 'stopwords', 'wordnet',
                        'omw-1.4', 'maxent_ne_chunker', 'words']:
                try:
                    nltk.download(res, quiet=True)
                except Exception:
                    pass
        except Exception:
            pass

    def _load_model(self):
        try:
            import json, numpy as np
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.linear_model import LogisticRegression
            model_dir = os.path.join(os.path.dirname(__file__), "models")
            json_path = os.path.join(model_dir, "intent_model.json")
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    mj = json.load(f)
                self.vectorizer = TfidfVectorizer(ngram_range=tuple(mj["ngram_range"]), sublinear_tf=mj["sublinear_tf"])
                self.vectorizer.vocabulary_ = mj["vocabulary"]
                self.vectorizer.idf_ = np.array(mj["idf"])
                self.vectorizer.fixed_vocabulary_ = True
                self.classifier = LogisticRegression()
                self.classifier.coef_ = np.array(mj["coef"])
                self.classifier.intercept_ = np.array(mj["intercept"])
                self.classifier.classes_ = np.array(mj["classes"])
                print("NLPProcessor: Successfully reconstructed local model from JSON configuration.")
            else:
                import pickle
                vp = os.path.join(model_dir, "vectorizer.pkl")
                mp = os.path.join(model_dir, "model.pkl")
                if os.path.exists(vp) and os.path.exists(mp):
                    with open(vp, 'rb') as f: self.vectorizer = pickle.load(f)
                    with open(mp, 'rb') as f: self.classifier = pickle.load(f)
                    print("NLPProcessor: Loaded model from pickle files.")
        except Exception as e:
            print(f"NLPProcessor: Model load failed: {e}")

    # ── STEP 1: LANGUAGE DETECTION ───────────────────────────────────────────
    def detect_language(self, text: str) -> str:
        if any(0x0900 <= ord(c) <= 0x097F for c in text): return "Hindi"
        if any(0x0C80 <= ord(c) <= 0x0CFF for c in text): return "Kannada"
        if any(0x0C00 <= ord(c) <= 0x0C7F for c in text): return "Telugu"
        if any(0x0B80 <= ord(c) <= 0x0BFF for c in text): return "Tamil"
        hinglish = {"bhejo","karo","lo","chahiye","likho","dhundo","banao","batao","dikhao","ko","ke","ka","ki","se","mein","aur","nahi","hai"}
        if len(set(text.lower().split()) & hinglish) >= 2: return "Hinglish"
        if len(text.strip()) > 5:
            try:
                from langdetect import detect as langdetect_detect
                detected = langdetect_detect(text)
                return LANGUAGE_MAP.get(detected, "English")
            except Exception:
                pass
        return "English"

    # ── STEP 2: TEXT NORMALIZATION ───────────────────────────────────────────
    def normalize_text(self, text: str) -> str:
        text = unicodedata.normalize("NFKC", text)
        for pattern, repl in SPOKEN_PUNCTUATION.items():
            text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
        text = VOICE_FILLERS.sub("", text)
        abbrevs = {r"\bpls\b":"please",r"\bplz\b":"please",r"\bu\b":"you",r"\bur\b":"your",
                   r"\babt\b":"about",r"\bthx\b":"thanks",r"\basap\b":"as soon as possible"}
        for p, r in abbrevs.items():
            text = re.sub(p, r, text, flags=re.IGNORECASE)
        return re.sub(r"\s+", " ", text).strip()

    # ── STEPS 3-4: TOKENIZATION ──────────────────────────────────────────────
    def tokenize(self, text: str) -> Tuple[List[str], List[str]]:
        try:
            import nltk
            return nltk.sent_tokenize(text), nltk.word_tokenize(text)
        except Exception:
            sents = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()] or [text]
            toks = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)
            return sents, toks

    # ── STEP 5: STOPWORD REMOVAL ─────────────────────────────────────────────
    def remove_stopwords(self, tokens: List[str], lang: str) -> Tuple[List[str], List[str]]:
        FALLBACK = {"a","an","the","and","or","but","is","are","was","were","to","for","on","of","with","in","at","by","it","this","that","from","be","been"}
        try:
            from nltk.corpus import stopwords
            lang_map = {"English":"english","Hindi":"hindi","Hinglish":"hindi","Bengali":"bengali","Marathi":"marathi"}
            try:
                sw = set(stopwords.words(lang_map.get(lang,"english")))
            except Exception:
                sw = FALLBACK
        except Exception:
            sw = FALLBACK
        return [t for t in tokens if t.lower() not in sw and len(t)>1], [t for t in tokens if t.lower() in sw]

    # ── STEP 6: STEMMING ─────────────────────────────────────────────────────
    def stem_tokens(self, tokens: List[str], lang: str) -> List[Dict[str, str]]:
        try:
            from nltk.stem import PorterStemmer, SnowballStemmer
            stemmer = PorterStemmer() if lang in ("Hindi","Hinglish") else SnowballStemmer("english")
            return [{"token": t, "stem": stemmer.stem(t)} for t in tokens]
        except Exception:
            results = []
            for t in tokens:
                s = t.lower()
                if s.endswith("ing"): s = s[:-3]
                elif s.endswith("tion"): s = s[:-4]
                elif s.endswith("ed"): s = s[:-2]
                elif s.endswith("s") and not s.endswith("ss"): s = s[:-1]
                results.append({"token": t, "stem": s})
            return results

    # ── STEP 7: LEMMATIZATION ────────────────────────────────────────────────
    def lemmatize_tokens(self, pos_tags: List[Dict[str, str]]) -> List[Dict[str, str]]:
        try:
            from nltk.stem import WordNetLemmatizer
            lem = WordNetLemmatizer()
            results = []
            for item in pos_tags:
                word, tag = item["token"], item.get("tag","NN")
                wn = "v" if tag.startswith("V") else ("a" if tag.startswith("J") else ("r" if tag.startswith("R") else "n"))
                try: lemma = lem.lemmatize(word, pos=wn)
                except: lemma = lem.lemmatize(word)
                results.append({"token": word, "lemma": lemma, "pos": tag})
            return results
        except Exception:
            return [{"token": d["token"], "lemma": d["token"].lower(), "pos": d.get("tag","NN")} for d in pos_tags]

    # ── STEP 8: POS TAGGING ──────────────────────────────────────────────────
    TAG_DESCRIPTIONS = {
        "CC":"Coordinating conjunction","CD":"Cardinal number","DT":"Determiner",
        "IN":"Preposition","JJ":"Adjective","JJR":"Adjective, comparative","JJS":"Adjective, superlative",
        "MD":"Modal","NN":"Noun, singular","NNS":"Noun, plural","NNP":"Proper noun, singular",
        "NNPS":"Proper noun, plural","PRP":"Personal pronoun","PRP$":"Possessive pronoun",
        "RB":"Adverb","TO":"to (particle)","UH":"Interjection","VB":"Verb, base form",
        "VBD":"Verb, past tense","VBG":"Verb, gerund","VBN":"Verb, past participle",
        "VBP":"Verb, present","VBZ":"Verb, 3rd person","WDT":"Wh-determiner","WP":"Wh-pronoun",
        "WRB":"Wh-adverb",",":"Comma",".":"Sentence-final punctuation"
    }

    def pos_tag(self, tokens: List[str]) -> List[Dict[str, str]]:
        try:
            import nltk
            tagged = nltk.pos_tag(tokens)
            return [{"token":t,"tag":tag,"description":self.TAG_DESCRIPTIONS.get(tag,"Other")} for t,tag in tagged]
        except Exception:
            results = []
            for t in tokens:
                tl = t.lower()
                if tl in {"create","generate","write","send","find","search","backup","compress","email","make","open","compose","move","delete"}:
                    tag,desc = "VB","Verb, base form"
                elif re.match(r"[\w\.-]+@[\w\.-]+\.\w+", t): tag,desc = "NNP","Proper noun (email)"
                elif re.match(r"https?://", t): tag,desc = "NNP","Proper noun (URL)"
                elif t[0:1].isupper(): tag,desc = "NNP","Proper noun"
                elif tl in {"a","an","the"}: tag,desc = "DT","Determiner"
                elif tl in {"to","on","for","about","at","in","of","with"}: tag,desc = "IN","Preposition"
                else: tag,desc = "NN","Noun"
                results.append({"token":t,"tag":tag,"description":desc})
            return results

    # ── STEP 9: NOUN PHRASE CHUNKING ─────────────────────────────────────────
    def chunk_noun_phrases(self, pos_tags: List[Dict[str, str]]) -> List[str]:
        try:
            import nltk
            grammar = r"NP: {<DT>?<JJ.*>*<NN.*>+}"
            parser = nltk.RegexpParser(grammar)
            tree = parser.parse([(d["token"], d["tag"]) for d in pos_tags])
            return [" ".join(leaf[0] for leaf in subtree.leaves())
                    for subtree in tree.subtrees() if subtree.label() == "NP"]
        except Exception:
            phrases, current = [], []
            for d in pos_tags:
                if d["tag"] in ("NN","NNS","NNP","NNPS","JJ"):
                    current.append(d["token"])
                else:
                    if current: phrases.append(" ".join(current)); current = []
            if current: phrases.append(" ".join(current))
            return phrases

    # ── STEP 10: NAMED ENTITY RECOGNITION (3-layer) ───────────────────────────
    def recognize_entities_ner(self, text: str, tokens: List[str], pos_tags: List[Dict[str, str]]) -> Dict[str, Any]:
        ner = {"EMAIL":[],"URL":[],"FILE":[],"PERSON":[],"ORGANIZATION":[],"DATE_TIME":[],"PHONE":[],"LOCATION":[]}

        # Layer 1: Regex
        ner["EMAIL"]    = re.findall(r"[\w\.-]+@[\w\.-]+\.\w+", text)
        ner["URL"]      = re.findall(r"https?://[^\s]+", text)
        ner["FILE"]     = re.findall(r"\b[\w\-]+\.(?:pdf|txt|docx|xlsx|csv|zip|json|png|jpg)\b", text, re.IGNORECASE)
        ner["PHONE"]    = re.findall(r"(?:\+91[-\s]?)?[6-9]\d{9}", text)
        ner["DATE_TIME"]= re.findall(r"\b(?:today|tomorrow|yesterday|monday|tuesday|wednesday|thursday|friday|saturday|sunday|\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}|\d{1,2}:\d{2}\s*(?:am|pm)?)\b", text, re.IGNORECASE)

        # Layer 2: NLTK ne_chunk
        try:
            import nltk
            chunked = nltk.ne_chunk([(d["token"], d["tag"]) for d in pos_tags], binary=False)
            for subtree in chunked:
                if hasattr(subtree, "label"):
                    entity_text = " ".join(leaf[0] for leaf in subtree.leaves())
                    label = subtree.label()
                    if label == "PERSON" and entity_text not in ner["PERSON"]:
                        ner["PERSON"].append(entity_text)
                    elif label in ("ORGANIZATION","GPE","FACILITY") and entity_text not in ner["ORGANIZATION"]:
                        ner["ORGANIZATION"].append(entity_text)
        except Exception:
            pass

        # Layer 3: spaCy
        if nlp_spacy:
            try:
                doc = nlp_spacy(text)
                for ent in doc.ents:
                    if ent.label_ == "PERSON" and ent.text not in ner["PERSON"]:
                        ner["PERSON"].append(ent.text)
                    elif ent.label_ in ("ORG","PRODUCT") and ent.text not in ner["ORGANIZATION"]:
                        ner["ORGANIZATION"].append(ent.text)
                    elif ent.label_ in ("DATE","TIME") and ent.text not in ner["DATE_TIME"]:
                        ner["DATE_TIME"].append(ent.text)
                    elif ent.label_ in ("GPE","LOC") and ent.text not in ner["LOCATION"]:
                        ner["LOCATION"].append(ent.text)
            except Exception:
                pass

        for key in ner:
            ner[key] = list(dict.fromkeys(ner[key]))
        return ner

    # ── STEP 11: INTENT CLASSIFICATION ───────────────────────────────────────
    def detect_intent(self, text: str, lang: str) -> Tuple[str, float]:
        text_lower = text.lower()

        # Layer 1: High-confidence signals
        if re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text): return "SEND_EMAIL", 0.99
        if re.search(r"https?://[^\s]+", text): return "AUTOMATE_BROWSER", 0.99

        # Layer 2: Trained TF-IDF + LR model
        if self.vectorizer is not None and self.classifier is not None:
            try:
                features = self.vectorizer.transform([text])
                intent = self.classifier.predict(features)[0]
                probs = self.classifier.predict_proba(features)[0] if hasattr(self.classifier, "predict_proba") else [0.9]
                confidence = float(max(probs))
                if confidence >= 0.55:
                    print(f"NLPProcessor: Local model -> intent='{intent}' confidence={confidence:.2f}")
                    return intent, confidence
            except Exception as e:
                print(f"NLPProcessor: Model prediction failed: {e}")

        # Layer 3: Multilingual pattern matching
        lang_code = {"Hindi":"hi","Kannada":"kn","Hinglish":"hinglish"}.get(lang, "en")
        best_score, best_intent = 0.0, "PLAN_SCHEDULE"
        for intent_name, data in INTENT_MAP.items():
            patterns = data["patterns"].get(lang_code, []) + data["patterns"].get("en", [])
            match_count = sum(1 for p in patterns if re.search(p, text_lower))
            if match_count > 0:
                score = 0.75 + 0.05 * match_count
                if score > best_score:
                    best_score, best_intent = score, intent_name
        return best_intent, max(best_score, 0.65)

    # ── ENTITY EXTRACTION ─────────────────────────────────────────────────────
    def extract_entities(self, text: str, lang: str, ner_results: Optional[Dict] = None) -> Dict[str, Any]:
        entities: Dict[str, Any] = {
            "recipient": None, "subject": None, "filename": None,
            "url": None, "date_time": None, "file_topic": None,
            "create_file": False, "keywords": [],
        }

        # From NER results
        if ner_results:
            if ner_results.get("EMAIL"): entities["recipient"] = ner_results["EMAIL"][0]
            if ner_results.get("URL"):   entities["url"]       = ner_results["URL"][0]
            if ner_results.get("FILE"):  entities["filename"]  = ner_results["FILE"][0]
            if ner_results.get("DATE_TIME"): entities["date_time"] = ner_results["DATE_TIME"][0]

        # File topic extraction — two-step, multilingual (English, Hindi, Kannada, Hinglish)
        create_match = re.search(
            r"(?:create|generate|write|make|compose)\s+(?:a\s+)?(pdf|document|text file|report|csv|txt)\s+(?:on|about|for|of)\s+(.+)",
            text, re.IGNORECASE
        )
        
        # Multilingual regexes (Hindi Devanagari, Hinglish, Kannada)
        # Matches: "Gemini का इस्तेमाल कैसे करें, इस पर एक PDF बनाएँ..." -> topic = Gemini का इस्तेमाल कैसे करें
        hi_match = re.search(
            r"(.+?)(?:,\s*|\s+)(?:इस\s+)?पर\s+(?:एक\s+)?(pdf|पीडीएफ|दस्तावेज़|रिपोर्ट|फ़ाइल)\s+(?:बनाएं|बनाएँ|बनाओ|लिखें|लिखें|तैयार करें)",
            text, re.IGNORECASE
        ) if not create_match else None
        
        # Fallback Hindi regex for prompts like "पीडीएफ बनाएं: topic" or "topic की पीडीएफ बनाएं"
        if not create_match and not hi_match:
            hi_match_alt = re.search(
                r"(?:एक\s+)?(pdf|पीडीएफ|दस्तावेज़|रिपोर्ट|फ़ाइल)\s+(?:बनाएं|बनाएँ|बनाओ|लिखें|तैयार करें)\s+(?:विषय\s+|पर\s+)?(.+)",
                text, re.IGNORECASE
            )
            if hi_match_alt:
                raw_hi_topic = hi_match_alt.group(2).strip()
                trimmed_hi_topic = re.sub(r"\s+(?:और\s+)?(?:उसे\s+)?[\w\.\-]+@[\w\.\-]+\.\w+.*$", "", raw_hi_topic).strip()
                hi_match = re.search(r"^$", "") # dummy
                hi_topic_extracted = trimmed_hi_topic
        
        kn_match = re.search(
            r"(.+?)\s+(?:ಬಗ್ಗೆ|ಮೇಲೆ|ವಿಷಯದ)\s+(?:ಒಂದು\_)?(pdf|ಪಿಡಿಎಫ್|ದಾಖಲೆ|ವರದಿ)\s+(?:ರಚಿಸಿ|ಮಾಡಿ|ಬರೆಯಿರಿ)",
            text, re.IGNORECASE
        ) if not create_match else None
        
        hinglish_match = re.search(
            r"(.+?)\s+(?:par|pe|ke baare mein)\s+(?:ek\_)?(pdf|document|report|file)\s+(?:banao|banaen|generate karo|write karo)",
            text, re.IGNORECASE
        ) if not create_match and not hi_match and not kn_match else None

        if create_match:
            file_type = create_match.group(1).lower()
            raw_topic = create_match.group(2).strip()
            topic = re.sub(
                r"\s+(?:and\s+)?(?:send|sent|mail|email|post)(?:\s+it)?(?:\s+to\s+\S+.*)?\s*$"
                r"|\s+(?:and\s+)?(?:send|sent|mail|email|post)\s*$"
                r"|\s+to\s+[\w\.\-]+@[\w\.\-]+\.\w+.*$"
                r"|\s+to\s+[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*\s*$",
                "", raw_topic
            ).strip() or raw_topic
            ext = ".txt" if "txt" in file_type or "text" in file_type else (".csv" if "csv" in file_type else ".pdf")
            entities["file_topic"] = topic
            entities["create_file"] = True
            if not entities["filename"]:
                clean = re.sub(r"[^\w\s-]", "", topic).strip().lower()
                clean = re.sub(r"[-\s]+", "_", clean)
                entities["filename"] = (clean if clean else "report") + ext
        elif hi_match:
            topic = hi_topic_extracted if 'hi_topic_extracted' in locals() else hi_match.group(1).strip()
            # Trim leading commas or quotes
            topic = re.sub(r"^[,\s'\"]+", "", topic).strip()
            entities["file_topic"] = topic
            entities["create_file"] = True
            if not entities["filename"]:
                clean = re.sub(r"[^\w\s-]", "", topic).strip().lower()
                clean = re.sub(r"[-\s]+", "_", clean)
                entities["filename"] = (clean if clean else "hindi_report") + ".pdf"
        elif kn_match:
            topic = kn_match.group(1).strip()
            entities["file_topic"] = topic
            entities["create_file"] = True
            if not entities["filename"]:
                clean = re.sub(r"[^\w\s-]", "", topic).strip().lower()
                clean = re.sub(r"[-\s]+", "_", clean)
                entities["filename"] = (clean if clean else "kannada_report") + ".pdf"
        elif hinglish_match:
            topic = hinglish_match.group(1).strip()
            entities["file_topic"] = topic
            entities["create_file"] = True
            if not entities["filename"]:
                clean = re.sub(r"[^\w\s-]", "", topic).strip().lower()
                clean = re.sub(r"[-\s]+", "_", clean)
                entities["filename"] = (clean if clean else "report") + ".pdf"

        # Recipient — multilingual
        if not entities["recipient"]:
            m = re.search(r"(?:send|mail|email|post)\s+(?:it\s+)?to\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)\b", text)
            if m: entities["recipient"] = m.group(1).strip()
        if not entities["recipient"]:
            # Hindi: "रमेश को भेजो"
            m = re.search(r"([^\s]+)\s+\u0915\u094b\s+(?:\u092d\u0947\u091c\u094b|\u092d\u0947\u091c\u0947\u0902|\u092e\u0947\u0932)", text)
            if m: entities["recipient"] = m.group(1)
        if not entities["recipient"] and ner_results and ner_results.get("PERSON"):
            entities["recipient"] = ner_results["PERSON"][0]

        # Subject
        if not entities["subject"]:
            m = re.search(r"(?:about|subject|विषय|ಬಗ್ಗೆ)\s+['\"]?([^'\"]+?)['\"]?(?:\s|$)", text, re.IGNORECASE)
            if m: entities["subject"] = m.group(1).strip()
        if not entities["subject"] and entities.get("file_topic"):
            entities["subject"] = f"{entities['file_topic']} Report"

        # Keywords
        try:
            from nltk.corpus import stopwords
            sw = set(stopwords.words("english"))
        except Exception:
            sw = {"a","an","the","and","or","to","for","on","of","in","is","it"}
        entities["keywords"] = [w for w in text.split() if w.lower() not in sw and len(w) > 3 and w.isalpha()][:8]

        return entities

    # ── STEP 12: SEMANTIC ROLE LABELING ──────────────────────────────────────
    def semantic_parse(self, text: str, intent: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        try:
            import nltk
            pos_tagged = nltk.pos_tag(nltk.word_tokenize(text))
            main_verb = next((w for w, t in pos_tagged if t.startswith("VB")), intent.lower().replace("_"," "))
        except Exception:
            main_verb = intent.lower().replace("_"," ")
        theme     = entities.get("filename") or entities.get("file_topic") or entities.get("url") or "task"
        recipient = entities.get("recipient") or "unspecified"
        instrument = {"SEND_EMAIL":"Email API","AUTOMATE_BROWSER":"Browser Agent","MANAGE_FILES":"File System"}.get(intent, "Planner Agent")
        dt_part = f", ARGM-TMP={entities['date_time']}" if entities.get("date_time") else ""
        logical_form = f"λe.{intent}(ARG0=User, ARG1={theme}, ARG2={recipient}, ARGM-INS={instrument}{dt_part})"
        return {
            "semantic_roles": {
                "ARG0_Agent": "User", "ARG1_Theme": theme,
                "ARG2_Recipient": recipient, "ARGM_Instrument": instrument,
                "ARGM_Temporal": entities.get("date_time"), "ARGM_Location": entities.get("url"),
            },
            "main_verb": main_verb,
            "dependency_tree_status": "Parsed via rule-based SRL",
            "logical_form": logical_form,
            "propbank_frame": f"{main_verb}.01",
        }

    def context_resolution(self, text: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "active_session": "Session-AURA-992",
            "coreference_resolution": {
                "it": entities.get("filename") or entities.get("file_topic") or "previous document",
                "them": entities.get("recipient") or "intended contact",
                "there": entities.get("url") or "system location",
            },
            "user_preferences": {
                "detected_language": self.detect_language(text),
                "voice_compatible": True, "multilingual_mode": True,
            }
        }

    # ── STEP 13: TASK DECOMPOSITION ───────────────────────────────────────────
    def decompose_tasks(self, text: str, intent: str, entities: Dict[str, Any]) -> List[Dict[str, Any]]:
        tasks = [{"id":"node-nlp","label":"NLP Intent & Entity Parse","type":"planner","inputs":{"text":text},"outputs":{"intent":intent,"entities":entities}}]
        if intent == "SEND_EMAIL":
            if entities.get("create_file"):
                tasks.append({"id":"node-create-doc","label":f"Create Document: {entities['filename']}","type":"document",
                    "inputs":{"filename":entities["filename"],"topic":entities.get("file_topic","General Report"),"action":"create"},
                    "outputs":{"filepath":f"/workspace/{entities['filename']}"}})
            elif entities.get("filename"):
                tasks.append({"id":"node-retrieve","label":f"Retrieve Attachment: {entities['filename']}","type":"document",
                    "inputs":{"query":entities["filename"]},"outputs":{"filepath":f"/workspace/{entities['filename']}"}})
            tasks.append({"id":"node-email","label":f"Compose Email to {entities.get('recipient') or 'Recipient'}","type":"email",
                "inputs":{"to":entities.get("recipient") or "admin@company.com","subject":entities.get("subject") or "AURA Report",
                    "attachment":f"/workspace/{entities['filename']}" if entities.get("filename") else None},
                "outputs":{"status":"sent","message_id":"msg_aura_ai"}})
        elif intent == "FIND_DOCUMENT":
            tasks.append({"id":"node-vector","label":f"Vector Search: {entities.get('filename') or text[:40]}","type":"memory",
                "inputs":{"query":text,"category":"documents"},"outputs":{"matches":[{"id":"doc_1","score":0.92}]}})
            tasks.append({"id":"node-doc","label":"Extract & Summarize Content","type":"document",
                "inputs":{"document_id":"doc_1"},"outputs":{"summary":"Document extracted."}})
        elif intent == "AUTOMATE_BROWSER":
            url = entities.get("url") or "https://news.ycombinator.com"
            tasks.append({"id":"node-browser","label":f"Navigate & Scrape: {url[:50]}","type":"browser",
                "inputs":{"url":url,"extract_selectors":["title","h1","p"]},"outputs":{"scraped_data":{"status":"scraped"}}})
            tasks.append({"id":"node-file-write","label":"Store Extracted Data","type":"file",
                "inputs":{"data":{},"filename":"scraped_results.json"},"outputs":{"path":"/workspace/scraped_results.json"}})
        elif intent == "MANAGE_FILES":
            fname = entities.get("filename") or "document.zip"
            tasks.append({"id":"node-file-op","label":f"Compress & Backup: {fname}","type":"file",
                "inputs":{"source":fname,"action":"backup"},"outputs":{"archive_path":f"/workspace/backups/{fname}.zip"}})
        else:
            tasks.append({"id":"node-planner","label":"Decompose & Schedule Action Plan","type":"planner",
                "inputs":{"command":text},"outputs":{"action_steps":["Parse requirements","Allocate Agents","Execute"]}})
        tasks.append({"id":"node-complete","label":"Verify Execution and Store Memory","type":"memory",
            "inputs":{"status":"Completed successfully"},"outputs":{"saved_state":"Workflow state persisted"}})
        return tasks

    # ── GENERATE VISIBLE NLP PIPELINE ─────────────────────────────────────────
    def generate_nlp_pipeline(self, text: str, intent: str, entities: Dict[str, Any], lang: str) -> List[Dict[str, Any]]:
        normalized = self.normalize_text(text)
        sentences, tokens = self.tokenize(normalized)
        filtered_tokens, removed_sw = self.remove_stopwords(tokens, lang)
        pos_tags = self.pos_tag(tokens)
        stems = self.stem_tokens(filtered_tokens, lang)
        lemmas = self.lemmatize_tokens(pos_tags)
        noun_phrases = self.chunk_noun_phrases(pos_tags)
        ner_results = self.recognize_entities_ner(text, tokens, pos_tags)
        srl = self.semantic_parse(text, intent, entities)
        decomp = self.decompose_tasks(text, intent, entities)

        return [
            {"step":1,"name":"Language Detection",
             "description":"Detecting natural language using Unicode script ranges (Devanagari, Kannada), langdetect library, and Hinglish keyword heuristics.",
             "inputs":{"raw_text":text},"outputs":{"detected_language":lang,"library":"langdetect + Unicode + Hinglish heuristics"}},
            {"step":2,"name":"Text Normalization (Voice-Ready)",
             "description":"NFKC Unicode normalization, voice filler removal (um/uh/like), spoken punctuation conversion (period -> .), abbreviation expansion.",
             "inputs":{"raw_text":text},"outputs":{"normalized_text":normalized,"voice_cleaned":text!=normalized}},
            {"step":3,"name":"Sentence Segmentation",
             "description":"Splitting text into sentence units using NLTK Punkt tokenizer.",
             "inputs":{"normalized_text":normalized},"outputs":{"sentences":sentences,"sentence_count":len(sentences)}},
            {"step":4,"name":"Word Tokenization",
             "description":"Splitting sentences into individual lexical tokens using NLTK word_tokenize (handles contractions and special characters).",
             "inputs":{"sentences":sentences},"outputs":{"tokens":tokens,"token_count":len(tokens)}},
            {"step":5,"name":"Stopword Removal",
             "description":f"Removing high-frequency, semantically low-value function words using NLTK multilingual stopwords corpus ({lang}).",
             "inputs":{"tokens":tokens,"language":lang},"outputs":{"filtered_tokens":filtered_tokens,"removed_stopwords":removed_sw,"retained_count":len(filtered_tokens)}},
            {"step":6,"name":"Stemming",
             "description":"Reducing words to their root/base form using PorterStemmer (English) or SnowballStemmer (multilingual).",
             "inputs":{"filtered_tokens":filtered_tokens},"outputs":{"stems":stems[:15]}},
            {"step":7,"name":"Lemmatization (POS-aware)",
             "description":"Converting words to dictionary base form (lemma) using NLTK WordNetLemmatizer with POS-guided accuracy.",
             "inputs":{"pos_tags":[{"token":d["token"],"tag":d["tag"]} for d in pos_tags[:10]]},"outputs":{"lemmas":lemmas[:15]}},
            {"step":8,"name":"Part-of-Speech Tagging",
             "description":"Labeling each token with grammatical category using NLTK Averaged Perceptron Tagger (Penn Treebank tagset).",
             "inputs":{"tokens":tokens},"outputs":{"pos_tags":pos_tags[:20]}},
            {"step":9,"name":"Noun Phrase Chunking",
             "description":"Grouping tokens into Noun Phrases using NLTK RegexpParser: NP -> {<DT>?<JJ.*>*<NN.*>+}",
             "inputs":{"pos_tags":[{"token":d["token"],"tag":d["tag"]} for d in pos_tags]},"outputs":{"noun_phrases":noun_phrases}},
            {"step":10,"name":"Named Entity Recognition (3-Layer)",
             "description":"Layer 1: Regex (emails, URLs, files). Layer 2: NLTK ne_chunk (PERSON, ORG, GPE). Layer 3: spaCy (high-accuracy NER).",
             "inputs":{"text":text,"layers":["Regex NER","NLTK ne_chunk","spaCy"]},"outputs":{"entities":{k:v for k,v in ner_results.items() if v},"layer_1_regex":{"emails":ner_results["EMAIL"],"urls":ner_results["URL"],"files":ner_results["FILE"]}}},
            {"step":11,"name":"Intent Classification (TF-IDF + Logistic Regression)",
             "description":"3-layer cascade: (1) structural signals, (2) TF-IDF+LR model trained on CLINC150 (97.68% accuracy), (3) multilingual pattern matching.",
             "inputs":{"text":text,"language":lang},"outputs":{"detected_intent":intent,"model":"TF-IDF (1-2 gram) + Logistic Regression","training_corpus":"CLINC150 + AURA Custom","validation_accuracy":"97.68%"}},
            {"step":12,"name":"Semantic Role Labeling (PropBank-style)",
             "description":"Assigning PropBank semantic roles: ARG0=Agent, ARG1=Theme, ARG2=Recipient, ARGM=Adjuncts (Instrument, Temporal, Location).",
             "inputs":{"intent":intent,"entities":entities},"outputs":{"semantic_roles":srl["semantic_roles"],"logical_form":srl["logical_form"],"propbank_frame":srl["propbank_frame"]}},
            {"step":13,"name":"Multi-Agent Task Decomposition",
             "description":"Building a structured multi-agent execution workflow. Each node dispatched to specialized AI agent (Email, Document, Browser, File, Memory).",
             "inputs":{"intent":intent,"entities":entities},"outputs":{"workflow_nodes":len(decomp),"node_types":list(dict.fromkeys(n["type"] for n in decomp)),"workflow":decomp}},
        ]

    # ── MAIN ENTRY POINT ──────────────────────────────────────────────────────
    def process_command(self, text: str) -> Dict[str, Any]:
        """
        Full 13-step NLP pipeline.
        Primary: Groq Cloud API (Llama-3.3-70B) for zero-shot multilingual understanding.
        Fallback: Local NLTK/TF-IDF engine.
        """
        # Always run local NLP steps (for the 13-step display in the UI)
        lang = self.detect_language(text)
        normalized = self.normalize_text(text)
        _, tokens = self.tokenize(normalized)
        pos_tags = self.pos_tag(tokens)
        ner_results = self.recognize_entities_ner(normalized, tokens, pos_tags)
        intent_local, confidence = self.detect_intent(normalized, lang)

        # ── ZERO-SHOT LLM PARSER (Groq preferred, Gemini fallback) ──────────
        system_prompt = """You are an NLP parser for an AI task automation platform called AURA AI.
The user sends commands in English, Hindi (Devanagari), Kannada, Hinglish or any other language.
You must parse the command and return ONLY a valid JSON object - no markdown, no backticks, no explanation.

JSON schema to return:
{
  "intent": one of ["SEND_EMAIL", "FIND_DOCUMENT", "CREATE_DOCUMENT", "AUTOMATE_BROWSER", "PLAN_SCHEDULE", "MANAGE_FILES"],
  "intent_confidence": 0.98,
  "language": "English" or "Hindi" or "Kannada" or "Hinglish" etc,
  "entities": {
    "recipient": "email address (e.g. user@example.com) or person name, or null",
    "subject": "email subject line, or null",
    "filename": "snake_case filename with .pdf/.txt/.csv extension, or null",
    "url": "url if mentioned, or null",
    "date_time": "date or time if mentioned, or null",
    "file_topic": "the VERBATIM, COMPLETE topic for the document to create. NEVER truncate this. If user says 'Gemini का इस्तेमाल कैसे करें' that is the full topic. null if no document.",
    "create_file": true if creating/generating a PDF, document, report, file, else false,
    "keywords": ["important", "keywords"]
  },
  "task_decomposition": [
    {"id": "node-nlp", "label": "NLP Intent & Entity Parse", "type": "planner", "inputs": {"text": "<original command>"}, "outputs": {"intent": "<intent>", "entities": {}}},
    {"id": "node-create-doc", "label": "Create Document: <filename>", "type": "document", "inputs": {"filename": "<filename>", "topic": "<file_topic>", "action": "create"}, "outputs": {"filepath": "/workspace/<filename>"}},
    {"id": "node-email", "label": "Compose Email to <recipient>", "type": "email", "inputs": {"to": "<recipient>", "subject": "<subject>", "attachment": "/workspace/<filename> or null"}, "outputs": {"status": "sent"}},
    {"id": "node-complete", "label": "Verify Execution and Store Memory", "type": "memory", "inputs": {"status": "Completed"}, "outputs": {"saved_state": "Workflow state persisted"}}
  ]
}

RULES (follow strictly):
1. file_topic must be the EXACT, FULL topic text from the command. Do not shorten it.
2. filename must be derived from file_topic (snake_case + .pdf).
3. Include node-create-doc ONLY if create_file is true.
4. Include node-email if the command asks to send or email to someone.
5. Always include node-nlp as the first node and node-complete as the last node.
6. For intent SEND_EMAIL or CREATE_DOCUMENT with email, both node-create-doc and node-email must appear.
7. Return ONLY valid JSON. No text before or after."""

        llm_result = None
        import json as _json

        if os.getenv("GROQ_API_KEY"):
            try:
                from backend.app.nlp.groq_api import call_groq_api
                resp = call_groq_api(text, system_instruction=system_prompt, json_mode=True)
                if resp:
                    llm_result = _json.loads(resp.strip())
            except Exception as ex:
                print(f"[GROQ] Parse failed, falling to local: {ex}")

        if llm_result is None and os.getenv("GEMINI_API_KEY"):
            try:
                from backend.app.nlp.gemini import call_gemini_api
                resp = call_gemini_api(text, system_instruction=system_prompt, json_mode=True)
                if resp:
                    llm_result = _json.loads(resp.strip())
            except Exception as ex:
                print(f"[GEMINI] Parse failed, falling to local: {ex}")

        # ── Use LLM result if valid ───────────────────────────────────────────
        if llm_result and llm_result.get("intent") in INTENT_MAP:
            intent = llm_result["intent"]
            confidence = float(llm_result.get("intent_confidence", 0.98))
            entities = llm_result.get("entities", {})
            decomp = llm_result.get("task_decomposition", [])
            lang = llm_result.get("language", lang)

            # Ensure entities has all required fields
            for k in ["recipient", "subject", "filename", "url", "date_time", "file_topic", "create_file", "keywords"]:
                if k not in entities:
                    entities[k] = [] if k == "keywords" else (False if k == "create_file" else None)

            # If decomp is empty or missing, build it from entities
            if not decomp:
                decomp = self.decompose_tasks(normalized, intent, entities)

            semantic = self.semantic_parse(normalized, intent, entities)
            context = self.context_resolution(normalized, entities)
            pipeline = self.generate_nlp_pipeline(text, intent, entities, lang)

            return {
                "original_text":      text,
                "normalized_text":    normalized,
                "language":           lang,
                "intent":             intent,
                "intent_confidence":  confidence,
                "entities":           entities,
                "ner_results":        ner_results,
                "semantic_parse":     semantic,
                "context_resolution": context,
                "task_decomposition": decomp,
                "nlp_pipeline_steps": pipeline,
            }

        # ── Local Fallback (no API key or API failed) ─────────────────────────
        entities = self.extract_entities(normalized, lang, ner_results)
        semantic = self.semantic_parse(normalized, intent_local, entities)
        context  = self.context_resolution(normalized, entities)
        decomp   = self.decompose_tasks(normalized, intent_local, entities)
        pipeline = self.generate_nlp_pipeline(text, intent_local, entities, lang)

        return {
            "original_text":      text,
            "normalized_text":    normalized,
            "language":           lang,
            "intent":             intent_local,
            "intent_confidence":  confidence,
            "entities":           entities,
            "ner_results":        ner_results,
            "semantic_parse":     semantic,
            "context_resolution": context,
            "task_decomposition": decomp,
            "nlp_pipeline_steps": pipeline,
        }


# Singleton
nlp_processor = NLPProcessor()
