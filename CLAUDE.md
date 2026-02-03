# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

- **Install Dependencies**: `pip install -r requirements.txt`
- **Run Server**: `python run_server.py`
  - Starts the application at `http://localhost:8000`
  - Alternative: `uvicorn backend.main:app --reload`
- **Testing**:
  - Currently, there is no formal test runner (like pytest) configured.
  - Test API endpoints using `curl`:
    ```bash
    curl -X POST http://localhost:8000/api/generate-blog \
      -H "Content-Type: application/json" \
      -d '{"url":"https://youtube.com/watch?v=dQw4w9WgXcQ","language":"en"}'
    ```

## Architecture

- **Stack**: Python (FastAPI) backend with a vanilla JavaScript/HTML frontend.
- **Frontend**:
  - `index.html`: Main single-page application entry point.
  - Uses Tailwind CSS (via CDN or build) and vanilla JS for logic.
- **Backend** (`backend/`):
  - `backend/main.py`: FastAPI application entry point and route definitions.
  - `backend/llm_service.py`: Interface with Nebius AI for text generation.
  - `backend/youtube_service.py`: Fetches video transcripts using `youtube-transcript-api`.
  - `backend/auth_dependencies.py` & `credits_service.py`: Manages user credits and authentication.
- **Utils**:
  - `utils/blog_generator.py`: Contains the core logic for processing transcripts into blog posts.
- **Deployment**:
  - `api/index.py`: Adapter for Vercel serverless deployment.
  - `run_server.py`: Script for local execution (standard entry point).

## Code Style

- **Python**: Follow PEP 8.
- **JavaScript**: ES6+ standards.
- **Error Handling**: The backend uses FastAPI's exception handling. Ensure API errors return structured JSON responses.
- **Async**: The backend is async (FastAPI); use `async/await` for I/O operations (API calls, DB access).
