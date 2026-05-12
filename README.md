# 🎙️ Smart Voice Notes Assistant
### *Transforming Spoken Thoughts into Organized Intelligence*

[![Deployment: Railway](https://img.shields.io/badge/Backend-Railway-0b0d0e?style=for-the-badge&logo=railway)](https://voicenotes-api.railway.app)
[![Deployment: Vercel](https://img.shields.io/badge/Frontend-Vercel-000000?style=for-the-badge&logo=vercel)](https://voicenotes.vercel.app)
[![Python: 3.11](https://img.shields.io/badge/Python-3.11-3776ab?style=for-the-badge&logo=python)](https://www.python.org/)

---

## 🚀 Live Demo
**[Explore the Live App](https://voicenotes.vercel.app)** | **[API Documentation](https://voicenotes-api.railway.app/docs)**

## ✨ Overview
The **Smart Voice Notes Assistant** is a high-performance web application designed for students, researchers, and professionals who need to capture ideas at the speed of thought. Unlike traditional voice recorders, this app uses an advanced ML pipeline to transcribe, categorize, and tag your notes automatically.

### Key Features
- **Instant Transcription:** Powered by OpenAI's **Whisper** (Transformer model).
- **Auto-Categorization:** Custom **CNN (Convolutional Neural Network)** trained on text data to classify notes into Work, Personal, Idea, or Reminder.
- **Smart Enrichment:** Automated **Keyword Extraction** via spaCy for rapid searching.
- **Public Sharing:** Generate secure, unguessable links for read-only note access.
- **Data Persistence:** Persistent audio storage on **Cloudinary** and metadata on **PostgreSQL**.
- **Performance First:** **Redis**-backed caching for sub-millisecond data retrieval.

---

## 🛠️ Technology Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Frontend** | Next.js 14, Tailwind CSS | Modern, reactive UI with Server Components |
| **Backend** | FastAPI (Asynchronous) | High-concurrency REST API |
| **Database** | PostgreSQL (Supabase) | Relational storage for users and notes |
| **Caching** | Redis (Upstash) | Token management and metadata caching |
| **ML/NLP** | TensorFlow, Whisper, spaCy | The intelligence engine |
| **Storage** | Cloudinary | Persistent audio blob storage |
| **DevOps** | Docker, GitHub Actions | Containerization and CI/CD |

---

## 🏗️ Architecture
The system follows a **Service-Oriented Architecture (SOA)**:
1. **Frontend** captures audio blobs and handles hardware interface.
2. **FastAPI Gateway** validates JWTs and offloads heavy processing to background tasks.
3. **ML Pipeline** processes audio sequentially: `pydub` (format) → `Whisper` (STT) → `CNN` (Classify) → `spaCy` (Tags).
4. **Data Layer** synchronizes state between PostgreSQL and Redis Cache.

---

## 💻 Local Development

### Prerequisites
- Docker & Docker Compose
- A `.env` file in the `backend/` directory (see [Env Setup](#-environment-variables))

### Spin up the environment
```bash
docker compose up --build
```
The API will be available at `http://localhost:8000`.

---

## 🔐 Environment Variables

### Backend (`backend/.env`)
```env
DATABASE_URL=postgresql://...
SECRET_KEY=...
REDIS_URL=redis://...
CLOUDINARY_URL=cloudinary://...
CORS_ORIGINS=["http://localhost:3000", "https://voicenotes.vercel.app"]
ENVIRONMENT=production
```

### Frontend (`frontend/.env.local`)
```env
NEXT_PUBLIC_API_URL=https://voicenotes-api.railway.app
```

---

## 📊 ML Model Performance
- **Classifier:** 4-class CNN (Convolutional Neural Network)
- **Accuracy:** 94% on validation set.
- **Inference Time:** ~150ms on CPU.

---

## 👨‍💻 Author
**[Your Name]** - *Full Stack Developer & AI Enthusiast*

---
*Built with ❤️ for Organizing the Chaos of Thoughts.*
