[Homepage](index.md) | [Features](features.md) | [Technology Used](tech.md) | [API Setup](api-setup.md) | [Troubleshooting & FAQ](troubleshooting.md)

# 🚀 Getting Started with LogeekMind v2.0

LogeekMind has been rebuilt with a modern, scalable architecture. The frontend is now a Next.js application, and it communicates with a separate Python backend.

## Architecture Overview
- **Frontend:** A [Next.js](https://nextjs.org/) and [React](https://reactjs.org/) application.
- **Backend:** A Python server (using [FastAPI](https://fastapi.tiangolo.com/)) that handles all AI processing and business logic.
- **Database & Auth:** [Supabase](https://supabase.com/) is used for user authentication and database storage.

---

## 🛠️ Local Development Setup

To run LogeekMind locally, you need to run both the backend and frontend servers.

### 1. Backend Setup

First, get the Python backend server running.

1.  **Navigate to the backend directory:**
    ```sh
    # Assuming you are in the root 'LogeekMind_2.0' directory
    cd backend
    ```
2.  **Create and activate a virtual environment:**
    ```sh
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```
3.  **Install requirements:**
    ```sh
    pip install -r requirements.txt
    ```
4.  **Environment Variables:** Create a file named `.env` in the `backend` directory and add your API keys.
    ```
    # LogeekMind_2.0/backend/.env

    SUPABASE_URL=YOUR_SUPABASE_URL
    SUPABASE_KEY=YOUR_SUPABASE_KEY
    GEMINI_API_KEY=YOUR_GOOGLE_GEMINI_API_KEY
    GROQ_API_KEY=YOUR_GROQ_CLOUD_API_KEY
    ```
5.  **Run the server:**
    ```sh
    uvicorn main:app --reload
    ```
    The backend should now be running at `http://127.0.0.1:8000`.

### 2. Frontend Setup

With the backend running, set up the Next.js frontend in a **new terminal window**.

1.  **Navigate to the frontend directory:**
    ```sh
    # Assuming you are in the root 'LogeekMind_2.0' directory
    cd frontend
    ```
2.  **Install dependencies:**
    ```sh
    npm install
    ```
3.  **Environment Variables:** For authentication to work, you must create a file named `.env.local` in the `frontend` directory and add your Supabase keys.
    ```
    # LogeekMind_2.0/frontend/.env.local

    NEXT_PUBLIC_SUPABASE_URL=YOUR_SUPABASE_URL
    NEXT_PUBLIC_SUPABASE_ANON_KEY=YOUR_SUPABASE_ANON_KEY
    ```
4.  **Run the app:**
    ```sh
    npm run dev
    ```
    Open [http://localhost:3000](http://localhost:3000) in your browser to see the application.