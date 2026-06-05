# AURA AI - Production Deployment Guide & Architecture

AURA AI is a modern full-stack web application that translates natural language directives into structured, agent-orchestrated productivity workflows. 

This guide details the steps required to deploy the complete architecture to free-tier cloud environments (**Vercel** for the frontend, **Render** for the backend, **Firebase Firestore/Auth** for authentication/database, and **Cloudinary** for file assets).

---

## 📂 Repository Folder Structure

```
d:/NLP/
├── backend/                  # FastAPI Backend Service
│   ├── app/
│   │   ├── main.py           # Core FastAPI server initialization
│   │   ├── config.py         # Environmental variables & fallback states
│   │   ├── firebase_config.py# Firebase Admin SDK & Firestore client connection
│   │   ├── security.py       # JWT verify dependency (Firebase auth guard)
│   │   ├── api/              # Route controllers
│   │   │   ├── dashboard.py  # Firestore stats logic
│   │   │   ├── command.py    # Command parsing & histories
│   │   │   ├── workflows.py  # Workflow DAG building & runs
│   │   │   ├── agents.py     # Agents monitoring & toggling
│   │   │   ├── memory.py     # Vector memory lists & queries
│   │   │   └── storage.py    # Cloudinary multipart file uploads
│   │   └── nlp/              # NLP processor and simulators
│   ├── requirements.txt      # Python deployment requirements
│   ├── render.yaml           # Render blueprint deployment setup
│   └── .env.backend.example  # Backend env var example
│
└── frontend/                 # React + TypeScript hot-reload frontend
    ├── src/
    │   ├── firebase.ts       # Firebase Client SDK credentials initialization
    │   ├── context/
    │   │   ├── AuthContext.tsx# User session provider (Google Auth popup + JWT hook)
    │   │   └── ThemeContext.tsx
    │   ├── components/       # Layout indicators, Sidebar, Header, React Flow graphs
    │   ├── pages/            # 9 Saas dashboard screens
    │   ├── types.ts          # API response type interfaces
    │   └── App.tsx           # Authenticated layout router
    ├── vercel.json           # Vercel SPA routing rules config
    ├── .env.example          # Frontend env var template
    └── index.html            # Entry layout and SEO keywords
```

---

## 🔐 Environment Variables Configuration

### 1. Frontend Configuration (`frontend/.env`)
Create a file named `.env` in the `frontend/` directory:
```env
VITE_FIREBASE_API_KEY=your_firebase_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_firebase_auth_domain
VITE_FIREBASE_PROJECT_ID=your_firebase_project_id
VITE_FIREBASE_APP_ID=your_firebase_app_id
VITE_BACKEND_URL=https://your-backend-on-koyeb.koyeb.app
```

### 2. Backend Configuration (`backend/.env`)
Create a file named `.env` in the `backend/` directory:
```env
FIREBASE_PROJECT_ID=your_firebase_project_id
FIREBASE_CLIENT_EMAIL=your_firebase_client_email
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC..."
CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret
FRONTEND_URL=https://your-frontend-on-vercel.vercel.app
```
> [!NOTE]
> Make sure the multiline private key quotes are included and newlines are escaped as `\n` to prevent Parse errors on Koyeb.

---

## ☁️ Step-by-Step Deployment Instructions

### 1. Firebase Setup (Authentication & Firestore)
1. Go to the [Firebase Console](https://console.firebase.google.com/) and click **Add Project**.
2. Go to **Authentication** -> **Sign-in method** -> Enable **Google** and **Email/Password**.
3. Go to **Firestore Database** -> Click **Create Database** -> Choose a region -> Select **Start in production mode**.
4. Go to **Project Settings** (gear icon) -> **Service Accounts** -> Click **Generate New Private Key**. Download the JSON file. Use the values in this file for your backend environment variables (`FIREBASE_PROJECT_ID`, `FIREBASE_CLIENT_EMAIL`, `FIREBASE_PRIVATE_KEY`).
5. Go to **Project Settings** -> General -> Add a Web App. Copy the `firebaseConfig` object variables to your frontend `.env` config.
6. **Firestore Security Rules**: Configure the rules tab in Firestore to authorize users to read/write their own scopes:
   ```javascript
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       match /{document=**} {
         allow read, write: if request.auth != null;
       }
     }
   }
   ```

### 2. Cloudinary Setup (File Storage)
1. Sign up for a free account at [Cloudinary](https://cloudinary.com/).
2. On your Cloudinary Dashboard, locate your **Cloud Name**, **API Key**, and **API Secret**.
3. Set these values in your backend environment variables.

### 3. Backend Deployment (Koyeb)
1. Sign up/Log in to [Koyeb](https://www.koyeb.com/).
2. Click **Create Service** -> Connect GitHub -> Select your `NLP-Project` repository.
3. Configure the service deployment settings:
   - **Root Directory**: `/` (Leave as default repository root to allow Python to resolve the `backend` package imports correctly).
   - **Builder**: Select **Buildpack** (Koyeb auto-detects `requirements.txt` inside the project).
   - **Run Command**: `uvicorn backend.app.main:app --host 0.0.0.0 --port 8000`
   - **Port**: Set port mapping to forward traffic to container port `8000`.
4. In the Koyeb Dashboard, under the **Environment Variables** section, add all keys listed in the backend section.
5. Click **Deploy**. Koyeb will build and launch your FastAPI backend.

### 4. Frontend Deployment (Vercel)
1. Sign up/Log in to [Vercel](https://vercel.com/).
2. Click **Add New** -> **Project**.
3. Connect your GitHub repository.
4. Set the **Framework Preset** to **Vite**.
5. Set the **Root Directory** to `frontend`.
6. Expand **Environment Variables** and insert the keys listed in the frontend section.
7. Click **Deploy**. Vercel will build the React application and deploy it with automatic SSL.

---

## 🛠️ API Integration Examples

### 1. Attaching JWT Bearer Tokens (React Client)
All API requests must carry the Firebase ID token in their headers:
```typescript
import { useAuth } from '../context/AuthContext';

const fetchDashboardStats = async () => {
  const { token } = useAuth();
  const backendUrl = import.meta.env.VITE_BACKEND_URL;

  const res = await fetch(`${backendUrl}/api/dashboard/stats`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  return await res.json();
};
```

### 2. Uploading Files to Cloudinary via Backend
```typescript
const handleUpload = async (file: File) => {
  const { token } = useAuth();
  const backendUrl = import.meta.env.VITE_BACKEND_URL;
  
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${backendUrl}/api/storage/upload`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  });
  return await res.json();
};
```

---

## 🏁 Final Production Deployment Checklist

- [ ] Firebase: Google Authentication is enabled.
- [ ] Firebase: Firestore is provisioned and security rules are published.
- [ ] Environment Variables: `VITE_BACKEND_URL` on Vercel points to the HTTPS Render endpoint.
- [ ] Environment Variables: `FRONTEND_URL` on Render points to the HTTPS Vercel production endpoint (or `*`).
- [ ] Environment Variables: The Render `FIREBASE_PRIVATE_KEY` has quotation marks and contains all escaped `\n` linebreaks.
- [ ] Environment Variables: Cloudinary credentials match the developer dashboard keys exactly.
- [ ] CORS: Render backend logs verify origins are configured correctly for Vercel domains.
- [ ] Health Check: Render service monitors report `/health` endpoint status is `200 OK`.
