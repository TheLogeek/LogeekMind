[Homepage](index.md) | [Features](features.md) | [Getting Started](getting-started.md) | [Technology Used](tech.md) | [Troubleshooting & FAQ](troubleshooting.md)

# 🔑 API Key Setup (v2.0)

LogeekMind integrates with several services that require API keys to function. This guide explains how they are configured.

---

## Service-Side Keys (Admin Setup)

For the application to run, the backend server needs keys for Supabase and the AI models (Gemini, Whisper, etc.). These are configured as environment variables on the server where the Python backend is deployed.

-   `SUPABASE_URL`: Your Supabase project URL.
-   `SUPABASE_KEY`: Your Supabase service role key.
-   `GEMINI_API_KEY`: Your Google Gemini API key, primarily used for the Homework Assistant.
-   `GROQ_API_KEY`: Your Groq Cloud API key, used for core AI features like AI Teacher, Smart Quiz, Summarizer, Exam Simulator, and Course Outline Generator.
-   `OPENAI_API_KEY`: Your OpenAI API key for Whisper transcription (if used).

These are **not** exposed to the frontend.

---