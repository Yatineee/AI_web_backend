# 🧠 ScrollSanity – Backend Service

This is the backend module of the *Short Video Behavior Intervention Assistant*. Built with **FastAPI**, integrated with **Novita GPT (DeepSeek)** for emotional intervention generation, and uses **SQLite** for data persistence. It analyzes users’ scrolling behavior and provides gentle, personalized psychological guidance.

---

## 🚀 Quick Start (Development)

### 1️⃣ Install Dependencies

```bash
# (Recommended) Use virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2️⃣ Run the Server

```bash
uvicorn main:app --reload
```

Default access: [http://localhost:8000](http://localhost:8000)  
Interactive API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧩 API Overview

### POST `/api/intervene`

Receives a session of user short-video behavior, determines whether intervention is needed, and returns a piece of advice.

**Request body example:**

```json
{
  "user_id": "U001",
  "session_start_time": "2025-06-13T21:15:00",
  "session_duration_min": 48.2,
  "active_period_label": "night",
  "avg_video_duration_sec": 31.5,
  "switch_frequency": 3.1,
  "content_emotion_score": -0.42,
  "content_type_keywords": ["emotional", "relationship", "doom"],
  "repeated_viewing_ratio": 0.25,
  "skipped_intro_ratio": 0.5,
  "saved_to_favorites": false,
  "3_day_total_watch_time": 433.0,
  "short_video_ratio": 0.85,
  "self_reported_goal": "I want to stay emotionally balanced"
}
```

**Sample response:**

```json
{
  "level": "medium",
  "advice_text": "It's okay to feel overwhelmed sometimes..."
}
```

---

## 🛠 Project Structure

```
backend/
├── main.py                 # FastAPI entry point
├── db.py                   # SQLite engine initialization
├── .env                    # Environment variables (sensitive)
├── config/
│   └── middleware.py       # CORS middleware setup
├── databases/
│   └── session_log.py      # SQLModel: session log model
├── services/
│   └── gpt_client.py       # Novita GPT wrapper logic
├── requirements.txt        # Python dependencies
```

---

## 💡 Key Features

- 🧠 Behavior-based intervention logic (`should_intervene`)
- 💬 Emotional guidance via Novita GPT (DeepSeek)
- 🗂 Session logging with SQLite for persistence
- 🔐 CORS support (enabling connection with frontend simulator)
- ✅ Ready for classifier & psychological label integration

---

## 📌 TODO – Expandable Features

- [ ] Integrate real AI classification model (replace dummy labels)
- [ ] Multi-level advice generation for different mental states
- [ ] Support personalized settings (e.g., tone, user goals)
- [ ] Add GPT reasoning output (e.g., `"reasoning": "..."` field)
