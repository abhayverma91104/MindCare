# MindCare 🧠 — Student Stress & Burnout Detection System

> **AI-powered mental health companion** combining Machine Learning stress prediction, LSTM emotion detection, and a Gemini-powered safety-filtered chatbot — built for university students.

---

## ✨ Features

| Feature | Details |
|---|---|
| **Stress Prediction** | Logistic Regression, Random Forest, SVM on DASS/PSS questionnaire data |
| **Burnout Score** | Random Forest Regressor outputs a 0-100 burnout risk score |
| **Emotion Detection** | Bidirectional LSTM trained on 400,000+ Kaggle sentences (6 classes) |
| **Gemini Chatbot** | System-prompt engineered, 20-message rolling memory, personality modes |
| **Safety Layer** | Crisis/self-harm keyword detection → emergency response + helpline (iCall: 9152987821) |
| **NLP Analysis** | VADER sentiment + NLTK preprocessing + emotion-to-stress mapping |
| **Dashboard** | Recharts burnout gauge, 7-day trend line, emotion bar chart |
| **Session History** | Persistent chat history and past prediction tracking |
| **Multilingual** | Chat in English, Hindi, Spanish, French, Bengali, Tamil, and more |
| **Personalization** | Recommendations adapt to stress level, emotion, and interaction history |

---

## 🏗️ Architecture

```
Frontend (Next.js + Tailwind)
        │
        │  HTTP/JSON
        ▼
Django REST API (backend/)
  ├── /api/predict    ← ML stress + burnout models
  ├── /api/chat       ← Gemini pipeline
  ├── /api/recommend  ← Personalization engine
  ├── /api/history    ← Session history
  └── /api/config     ← Global UI configuration
        │
        ├── models/ (scikit-learn + Keras LSTM)
        ├── utils/  (NLP analyzer)
        └── backend/chatbot/ (Gemini pipeline + recommendations)
        │
        ▼
SQLite (dev) / MongoDB (prod)
```

**Chatbot Data Flow:**
```
User Input → Emotion Detection (LSTM) → Stress Model → Context Builder
    → Gemini API → Safety Filter → Final Response
```

---

## 🚀 Quick Start (Local)

### Prerequisites
- Python 3.10+
- Node.js 18+
- A [Google Gemini API Key](https://ai.google.dev/)

### 1. Clone & Setup Environment

```bash
git clone <repo-url>
cd MindCare

# Copy and fill in your API key
cp .env.example .env
# Edit .env → set GEMINI_API_KEY=your_key_here
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm   # optional, for spaCy NER
```

### 3. Generate Datasets

```bash
python data/generate_dataset.py
# Creates: data/stress_dataset.csv, data/chat_dataset.csv
```

### 4. Run Feature Engineering

```bash
python data/feature_engineering.py
```

### 5. Train Classical ML Models

```bash
python models/train_classical.py
# Outputs: models/best_classifier.pkl, models/burnout_regressor.pkl, etc.
# Prints accuracy, F1, confusion matrix for all 3 models
```

### 6. Train LSTM (Emotion Detection)

```bash
python models/train_lstm.py
# Outputs: models/lstm_emotion.keras, models/tokenizer.pkl
# Takes ~2-5 minutes on CPU
```

### 7. Start Django Backend

```bash
cd backend
python manage.py migrate
python manage.py runserver
# API running at http://localhost:8000
```

### 8. Start Next.js Frontend

```bash
cd frontend
npm install
npm run dev
# Frontend running at http://localhost:3000
```

### 9. Open Your Browser

- 🏠 **Landing:** http://localhost:3000
- 💬 **Chat:** http://localhost:3000/chat
- 📊 **Dashboard:** http://localhost:3000/dashboard

---

## 📡 API Reference

### `POST /api/predict`
Predicts stress level and burnout score from questionnaire data.

**Request:**
```json
{
  "user_id": "optional-string",
  "dass_stress": 28,
  "dass_anxiety": 22,
  "dass_depression": 18,
  "pss_score": 30,
  "sleep_hours": 4.5,
  "study_hours": 12,
  "social_hours": 1,
  "exercise_freq": 0,
  "caffeine_cups": 4,
  "screen_hours": 8
}
```

**Response:**
```json
{
  "stress_level": "High",
  "burnout_score": 78.3,
  "probabilities": {"High": 0.79, "Low": 0.03, "Moderate": 0.18}
}
```

---

### `POST /api/chat`
Runs the full Gemini chatbot pipeline.

**Request:**
```json
{
  "user_id": "student_001",
  "message": "I feel overwhelmed with exams",
  "personality": "calm",
  "language": "English"
}
```

**Response:**
```json
{
  "response": "That sounds really overwhelming. Let's try something simple...",
  "crisis": false,
  "emotion": "anxious",
  "stress_level": "High",
  "burnout_score": 72.1,
  "personality": "calm"
}
```

---

### `GET /api/recommend?user_id=xxx`
Returns personalized coping strategy recommendations.

---

### `GET /api/history/<user_id>`
Returns the last 50 chat messages and last 10 predictions for the user. Used to populate the Dashboard and History views.

---

### `GET /api/config`
Returns global project configurations, including crisis hotlines, supported languages, chatbot personalities, and UI styling tokens (emotion emojis, stress color mappings).

---

### `GET /api/health`
Health check endpoint.

---

## 🤖 How the Models Work

### Classical ML (Stress Classification)
1. **Features:** DASS-21 subscores, PSS score, sleep/study/social hours, exercise frequency, caffeine intake, screen time
2. **Models:** Logistic Regression (baseline), Random Forest (best performer), SVM (RBF kernel)
3. **Output:** Low / Moderate / High + probability scores
4. **Burnout Regressor:** Random Forest Regressor outputting 0-100 score

### LSTM Emotion Detector
1. **Architecture:** Embedding (64-dim) → BiLSTM (64) → Dropout → BiLSTM (32) → Dense → Softmax
2. **Training:** 400,000+ labeled Kaggle sentences, 6 classes, EarlyStopping
3. **Output:** sadness / joy / love / anger / fear / surprise + confidence score

### Gemini Chatbot Pipeline
1. **System Prompt:** Injects stress level, emotion, burnout score, personality mode
2. **Memory:** Rolling 20-message history maintained per session
3. **Safety:** Regex pattern matching for crisis keywords → immediate override with helpline
4. **Personalities:** coach (motivational) / calm (grounding) / listener (empathetic)

---

## 🐳 Docker Deployment

```bash
# Copy and configure .env
cp .env.example .env

# Build and launch all services
docker-compose up --build

# Services:
#   Frontend  → http://localhost:3000
#   Backend   → http://localhost:8000
#   MongoDB   → mongodb://localhost:27017
```

---

## 📁 Project Structure

```
MindCare/
├── data/
│   ├── generate_dataset.py    # Synthetic data generation (stress + chat)
│   ├── preprocess.py          # Cleaning, scaling, tokenization
│   ├── feature_engineering.py # Composite features + TF-IDF
│   └── text.csv               # Raw emotion text dataset
│
├── models/
│   ├── train_classical.py     # LR + RF + SVM training
│   ├── train_lstm.py          # BiLSTM emotion model training
│   ├── predict.py             # Inference module (used by Django)
│   ├── *.pkl                  # Saved models (rf, svm, lr, scaler, encoders)
│   └── *.keras                # Keras LSTM model artifact
│
├── utils/
│   └── nlp_analyzer.py        # NLTK/VADER NLP + crisis detection
│
├── backend/
│   ├── manage.py
│   ├── mindcare/              # Django project (settings, urls, wsgi)
│   ├── api/                   # DRF views, models, serializers, urls
│   └── chatbot/
│       ├── gemini_pipeline.py # Full Gemini chatbot pipeline
│       └── recommendations.py # Personalization engine
│
├── frontend/
│   └── app/
│       ├── page.tsx           # Landing page
│       ├── chat/page.tsx      # Chat interface (Claude-style)
│       ├── dashboard/page.tsx # Stress dashboard with charts
│       └── history/page.tsx   # Session history & logs
│
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
├── requirements.txt
└── .env.example
```

---

## 🔐 Safety & Ethics

- **No medical advice** — Gemini is system-prompted to never diagnose or prescribe
- **Crisis override** — hard-coded emergency response bypasses Gemini entirely
- **Crisis Helplines:**
  - iCall India: **9152987821**
  - Vandrevala Foundation: **1860-2662-345**
  - International: **befrienders.org**
- **Data privacy** — all data stored locally; no third-party transmission except Gemini API calls

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS v4, Recharts |
| Backend | Python 3.11+, Django 3.2, Django REST Framework |
| ML | scikit-learn 1.3, TensorFlow 2.15 |
| NLP | NLTK (VADER), spaCy |
| LLM | Google Gemini 1.5 Flash API |
| Database | SQLite (dev), MongoDB/djongo (prod) |
| Deployment | Docker, Docker Compose, Gunicorn |

---

*MindCare is not a substitute for professional mental health care. If you are in crisis, please contact a licensed professional immediately.*
