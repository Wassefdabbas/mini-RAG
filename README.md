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

Then add your API key to the `.env` file Like:

```env
OPENAI_API_KEY=your_api_key
```