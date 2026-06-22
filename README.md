# AI Data Science Tutor – Personalized 3-Month Learning Platform

An AI-powered, personalized learning management system designed to teach Data Science step-by-step. The platform enforces mastery-based learning by locking subsequent modules until the student passes both the multiple-choice quiz and the coding assignment of the current week. It includes a live AI Tutor (powered by the Gemini API) to explain concepts and solve doubts, a milestone badge system, and dynamic PDF certificate generation.

---

## 🌟 Key Features

* **User Authentication**: Student registration and login with secure password hashing (bcrypt) and session management (JWT tokens).
* **Interactive Dashboard**: Displays current targets, overall course completion percentage, learning streak counts, and statistics (lessons completed, quiz average, and earned badges).
* **Mastery-Based Progression**: Enforces learning lock loops:
  $$\text{Lesson } N \longrightarrow \text{Quiz } N \text{ (Score } \ge 70\%) \text{ \& Assignment } N \text{ (Score } \ge 70\%) \longrightarrow \text{Unlock Lesson } N+1$$
* **Context-Aware AI Tutor**: An embedded chat assistant that answers student queries on the fly using the exact lesson content as prompt context.
* **AI Coding Evaluator**: Automatically evaluates python script submissions, returns scores, pass/fail status, and line-by-line constructive feedback.
* **Badge & Milestone System**: Unlocks digital awards (e.g. *Python Beginner*, *Data Cleaning Specialist*, *Visualization Master*, *ML Explorer*, *Data Science Expert*) upon completing target milestones.
* **Certificate Generator**: Dynamically generates and compiles landscape PDF certificates of completion using vector coordinates and typography in `reportlab`.

---

## 🛠️ Technology Stack

* **Backend**: Python FastAPI, SQLAlchemy (Async/PostgreSQL driver), Uvicorn, Pydantic, Passlib, ReportLab.
* **Frontend**: React.js (Vite, custom Vanilla CSS design system, private routing, lucide-react icons, marked.js markdown parsing).
* **Database**: PostgreSQL 15.
* **Infrastructure**: Docker & Docker Compose (Multi-container architecture).
* **AI Integration**: Gemini 2.5 Flash API (via direct HTTP endpoint with mock fallback utilities for offline development).

---

## 🗂️ Project Structure

```text
AI Tutour/
├── docker-compose.yml         # Container coordinator
├── .env                       # Environment credentials
├── README.md                  # Project documentation
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI main entrypoint
│   │   ├── models.py          # SQLAlchemy ORM models
│   │   ├── database.py        # Async session configuration
│   │   ├── seed.py            # Database seeder (12 weeks of data)
│   │   ├── routers/           # Endpoint controllers
│   │   └── services/          # Gemini AI and Certificate helper services
│   ├── Dockerfile
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/        # Shared Navbar/Sidebar/Chat UI elements
    │   ├── pages/             # Dashboard, Course, Assignment, Quiz, Profile
    │   ├── index.css          # Glassmorphism dark-theme layout css
    │   └── App.jsx            # Routing and React state context
    ├── Dockerfile
    └── package.json
```

---

## 🚀 Setup & Installation

### Prerequisites
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
* [Git](https://git-scm.com/) installed.

### 1. Configure the Environment
Open the `.env` file in the project folder and insert your Gemini API Key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key
```
*(If you do not have an API key, you can leave it blank. The system will automatically run in **Simulated Offline Mode** with mock grading and tutoring so you can still test all features and workflows!)*

### 2. Run with Docker Compose
Navigate to the project root and launch the multi-container environment:
```bash
docker compose up --build -d
```

This will automatically build the images, spin up PostgreSQL, initialize the tables, seed the 12-week Data Science curriculum, and start the frontend development server.

### 3. Access URL Ports
* **React Web Frontend**: [http://localhost:5173](http://localhost:5173)
* **FastAPI Backend Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **PostgreSQL Database**: Exposed locally on host port `5433` (maps to internal container `5432` to avoid local DB port conflicts).
