# mini-RAG

Mini-RAG is a minimal implementation of a Retrieval-Augmented Generation (RAG) system for question answering.

## Requirements

- Python 3.11
- uv

## Setup

```bash
git clone https://github.com/Wassefdabbas/mini-RAG.git
cd mini-RAG

# Creates a virtual environment and installs all dependencies
uv sync
```

## Configuration

### Set up environment variables

```bash
cp .env.example .env
```

Add your API key to the `.env` file:

```env
OPENAI_API_KEY=your_api_key
```

## Running the Application

Start the FastAPI development server:

```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

## API

Once the server is running:

- **Health Check:** http://127.0.0.1:5000/api/v1/health
- **Swagger UI:** http://127.0.0.1:5000/docs