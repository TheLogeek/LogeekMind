[Homepage](index.md) | [Features](features.md) | [Getting Started](getting-started.md) | [Technology Used](tech.md) | [Troubleshooting & FAQ](troubleshooting.md)

# 🔑 API Key Setup (v2.0)

LogeekMind integrates with several services that require API keys to function. This guide explains how they are configured.

---

## Service-Side Keys (Admin Setup)

For the application to run, the backend server needs keys for Supabase and the AI models (Gemini, Whisper, etc.). These are configured as environment variables on the server where the Python backend is deployed.

-   `SUPABASE_URL`: Your Supabase project URL.
-   `SUPABASE_KEY`: Your Supabase service role key.
-   `GEMINI_API_KEY`: Your default Google Gemini API key for AI features.
-   `OPENAI_API_KEY`: Your OpenAI API key for Whisper transcription.

These are **not** exposed to the frontend.

---

## User-Provided Gemini Key (Optional)

For AI-powered features like the AI Teacher, Smart Quiz, and Summarizer, the application can use a globally configured Gemini API key (set up by the admin).

However, to ensure uninterrupted access and avoid hitting shared usage limits, users have the option to provide their own Gemini API key directly in the user interface.

### How it Works

-   When you use an AI feature, you will see an input field labeled **"Your Gemini API Key (Optional)"**.
-   If you provide your own key, your request to the AI will be processed using your key instead of the shared one.
-   This key is stored temporarily in your browser's session or local storage for convenience. It is **never** saved on our servers.

### How to Get Your Own Gemini API Key

You can follow these steps to get a free Gemini API key from Google AI Studio.

1.  **Go to Google AI Studio:** Visit [aistudio.google.com](https://aistudio.google.com).
2.  **Get API Key:** Click the "**Get API Key**" button.
3.  **Create a New Project:** You may need to create a new Google Cloud project to associate with your key.
4.  **Generate & Copy:** Create and copy your new API key.
5.  **Paste into LogeekMind:** Paste this key into the input field when using an AI feature in the app.

This gives you direct, personal access to the AI models without relying on a shared key.