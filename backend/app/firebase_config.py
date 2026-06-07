import os
import uuid
import firebase_admin
from firebase_admin import credentials, firestore

PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
CLIENT_EMAIL = os.getenv("FIREBASE_CLIENT_EMAIL")
# Replace escaped newlines in Render/Koyeb secret manager
PRIVATE_KEY = os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n")

class MockFirestoreClient:
    _db = {}

    def collection(self, name):
        return MockCollectionReference(name, self._db)

class MockCollectionReference:
    def __init__(self, path, db):
        self.path = path
        self.db = db

    def document(self, doc_id=None):
        if not doc_id:
            doc_id = str(uuid.uuid4())
        return MockDocumentReference(f"{self.path}/{doc_id}", self.db)

    def where(self, field, op, val):
        return MockQuery(self.path, self.db).where(field, op, val)

    def order_by(self, field):
        return MockQuery(self.path, self.db).order_by(field)

    def get(self):
        return MockQuery(self.path, self.db).get()

class MockQuery:
    def __init__(self, path, db):
        self.path = path
        self.db = db
        self.filters = []

    def where(self, field, op, val):
        self.filters.append((field, op, val))
        return self

    def order_by(self, field):
        return self

    def get(self):
        results = []
        for doc_path, data in self.db.items():
            parts = doc_path.split("/")
            parent_path = "/".join(parts[:-1])
            doc_id = parts[-1]
            if parent_path == self.path:
                match = True
                for field, op, val in self.filters:
                    field_val = data.get(field)
                    if op == "==":
                        if field_val != val:
                            match = False
                            break
                    elif op == "!=":
                        if field_val == val:
                            match = False
                            break
                if match:
                    results.append(MockDocumentSnapshot(doc_path, doc_id, data, self.db))
        return results

class MockDocumentReference:
    def __init__(self, path, db):
        self.path = path
        self.db = db
        self.id = path.split("/")[-1]

    def collection(self, name):
        return MockCollectionReference(f"{self.path}/{name}", self.db)

    def get(self):
        data = self.db.get(self.path)
        return MockDocumentSnapshot(self.path, self.id, data, self.db)

    def set(self, data):
        self.db[self.path] = dict(data)

    def update(self, data):
        if self.path not in self.db:
            self.db[self.path] = {}
        existing = self.db[self.path]
        for k, v in data.items():
            if not isinstance(v, dict) and ((hasattr(v, 'values') and not callable(v.values)) or v.__class__.__name__ == 'ArrayUnion'):
                vals = getattr(v, 'values', [])
                existing[k] = existing.get(k, []) + list(vals)
            else:
                existing[k] = v

    def delete(self):
        if self.path in self.db:
            del self.db[self.path]

class MockDocumentSnapshot:
    def __init__(self, path, doc_id, data, db):
        self.path = path
        self.id = doc_id
        self._data = data
        self.db = db
        self.exists = data is not None
        self.reference = MockDocumentReference(path, db)

    def to_dict(self):
        return dict(self._data) if self._data else {}

class SafeFirestoreClient:
    def __init__(self, real_client):
        self.real_client = real_client
        self.mock_client = MockFirestoreClient()
        self.use_mock = False

    def collection(self, name):
        return SafeCollectionReference(self, name)

class SafeCollectionReference:
    def __init__(self, client, path):
        self.client = client
        self.path = path

    def document(self, doc_id=None):
        import uuid
        if not doc_id:
            doc_id = str(uuid.uuid4())
        return SafeDocumentReference(self.client, self.path, doc_id)

    def where(self, field, op, val):
        return SafeQuery(self.client, self.path, [(field, op, val)])

    def order_by(self, field):
        return SafeQuery(self.client, self.path)

    def get(self):
        try:
            if self.client.use_mock:
                return self.client.mock_client.collection(self.path).get()
            return self.client.real_client.collection(self.path).get()
        except Exception as e:
            if "Quota exceeded" in str(e) or "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                print("WARNING: Firestore quota exceeded during GET collection. Switching to MockFirestoreClient.")
                self.client.use_mock = True
                return self.client.mock_client.collection(self.path).get()
            raise e

class SafeDocumentReference:
    def __init__(self, client, collection_path, doc_id):
        self.client = client
        self.collection_path = collection_path
        self.id = doc_id
        self.path = f"{collection_path}/{doc_id}"

    def collection(self, name):
        return SafeCollectionReference(self.client, f"{self.path}/{name}")

    def get(self):
        try:
            if self.client.use_mock:
                return self.client.mock_client.collection(self.collection_path).document(self.id).get()
            return self.client.real_client.collection(self.collection_path).document(self.id).get()
        except Exception as e:
            if "Quota exceeded" in str(e) or "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                print("WARNING: Firestore quota exceeded during GET document. Switching to MockFirestoreClient.")
                self.client.use_mock = True
                return self.client.mock_client.collection(self.collection_path).document(self.id).get()
            raise e

    def set(self, data):
        try:
            if self.client.use_mock:
                return self.client.mock_client.collection(self.collection_path).document(self.id).set(data)
            return self.client.real_client.collection(self.collection_path).document(self.id).set(data)
        except Exception as e:
            if "Quota exceeded" in str(e) or "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                print("WARNING: Firestore quota exceeded during SET document. Switching to MockFirestoreClient.")
                self.client.use_mock = True
                return self.client.mock_client.collection(self.collection_path).document(self.id).set(data)
            raise e

    def update(self, data):
        try:
            if self.client.use_mock:
                return self.client.mock_client.collection(self.collection_path).document(self.id).update(data)
            return self.client.real_client.collection(self.collection_path).document(self.id).update(data)
        except Exception as e:
            if "Quota exceeded" in str(e) or "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                print("WARNING: Firestore quota exceeded during UPDATE document. Switching to MockFirestoreClient.")
                self.client.use_mock = True
                return self.client.mock_client.collection(self.collection_path).document(self.id).update(data)
            raise e

    def delete(self):
        try:
            if self.client.use_mock:
                return self.client.mock_client.collection(self.collection_path).document(self.id).delete()
            return self.client.real_client.collection(self.collection_path).document(self.id).delete()
        except Exception as e:
            if "Quota exceeded" in str(e) or "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                print("WARNING: Firestore quota exceeded during DELETE document. Switching to MockFirestoreClient.")
                self.client.use_mock = True
                return self.client.mock_client.collection(self.collection_path).document(self.id).delete()
            raise e

class SafeQuery:
    def __init__(self, client, collection_path, filters=None):
        self.client = client
        self.collection_path = collection_path
        self.filters = filters or []

    def where(self, field, op, val):
        return SafeQuery(self.client, self.collection_path, self.filters + [(field, op, val)])

    def order_by(self, field):
        return self

    def get(self):
        try:
            if self.client.use_mock:
                mock_q = self.client.mock_client.collection(self.collection_path)
                for f, o, v in self.filters:
                    mock_q = mock_q.where(f, o, v)
                return mock_q.get()
            
            real_q = self.client.real_client.collection(self.collection_path)
            for f, o, v in self.filters:
                real_q = real_q.where(f, o, v)
            return real_q.get()
        except Exception as e:
            if "Quota exceeded" in str(e) or "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                print("WARNING: Firestore quota exceeded during GET query. Switching to MockFirestoreClient.")
                self.client.use_mock = True
                mock_q = self.client.mock_client.collection(self.collection_path)
                for f, o, v in self.filters:
                    mock_q = mock_q.where(f, o, v)
                return mock_q.get()
            raise e

# Initialize Admin SDK or use Mock client
if PROJECT_ID and CLIENT_EMAIL and PRIVATE_KEY:
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate({
                "type": "service_account",
                "project_id": PROJECT_ID,
                "private_key": PRIVATE_KEY,
                "client_email": CLIENT_EMAIL,
                "token_uri": "https://oauth2.googleapis.com/token",
            })
            firebase_admin.initialize_app(cred)
        db_firestore = SafeFirestoreClient(firestore.client())
        print("Firebase Admin successfully initialized with service account certificate wrapper.")
    except Exception as e:
        print(f"ERROR: Failed to initialize Firebase Admin with credentials: {e}")
        print("Falling back to local in-memory MockFirestoreClient.")
        db_firestore = MockFirestoreClient()
else:
    print("WARNING: Firebase Admin credentials not fully configured. Using mock/local credentials.")
    db_firestore = MockFirestoreClient()


