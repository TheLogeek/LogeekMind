[Homepage](index.md) | [Features](features.md) | [Getting Started](getting-started.md) | [API Setup](api-setup.md) | [Troubleshooting & FAQ](troubleshooting.md)

# 🛠️ Technology & Architecture (v2.0)

LogeekMind v2.0 has been re-architected with a decoupled frontend and backend for better performance, scalability, and developer experience.

---

## Frontend

The entire frontend is built with modern web technologies, providing a fast, responsive, and interactive user experience.

-   **Framework:** [Next.js](https://nextjs.org/) (with App Router)
-   **Language:** [TypeScript](https://www.typescriptlang.org/)
-   **UI Library:** [React](https://reactjs.org/)
-   **Styling:** CSS Modules
-   **Progressive Web App (PWA):** Enabled via `next-pwa` for an installable, app-like experience.

---

## Backend

The backend is a robust Python server that handles all business logic, AI processing, and communication with third-party services.

-   **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Assumed)
-   **Language:** Python
-   **Function:** Serves a REST API that the Next.js frontend consumes. It manages all interactions with AI models and the database.

---

## 🔹 Database & Authentication

User management and data storage are handled by Supabase.

-   **Service:** [Supabase](https://supabase.io/)
-   **Features Used:**
    -   **Authentication:** Manages user sign-up, sign-in, and password resets via JWT.
    -   **Database:** PostgreSQL database for storing user profiles, usage logs, and other application data.

---

## 🔹 AI & Third-Party Services

LogeekMind integrates with several best-in-class AI services to power its features.

-   **Core AI Processing (AI Teacher, Quizzes, Summaries, Exams, Course Outlines):** Groq Cloud (Llama-3, Mixtral)
-   **Homework Assistant AI:** Google's Gemini API
-   **Audio Transcription (Audio-to-Text):** OpenAI's Whisper API
-   **Text-to-Speech (Notes-to-Audio):** gTTS (Google Text-to-Speech)

---

## 🚀 Deployment

-   **Frontend (Next.js):** Deployed on [Vercel](https://vercel.com/) for optimal performance and CI/CD.
-   **Backend (Python):** Render
-   **Database (Supabase):** Managed cloud platform.