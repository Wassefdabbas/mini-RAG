# mini-RAG

mini-RAG is a minimal Retrieval-Augmented Generation (RAG) service for uploading files, chunking content, and storing the processed data in MongoDB.

## Requirements

- Python 3.11
- uv
- Docker Desktop or Docker Engine with Docker Compose
- MongoDB Compass for browsing data

## Setup

```bash
git clone https://github.com/Wassefdabbas/mini-RAG.git
cd mini-RAG
uv sync
```

## Run With Docker

Start MongoDB with Docker Compose:

```bash
docker compose -f docker/docker-compose.yml up -d --build
```

The MongoDB container exposes port `27007` on your machine and maps to `27017` inside the container.

If you are using Docker Desktop, make sure Docker is running before you execute the command above.

## Configuration

Copy the example environment file and set the required values:

```bash
cp .env.example .env
```

```env
APP_NAME=mini-RAG
APP_VERSION=1.0.0
OPENAI_API_KEY=your_api_key
MONGODB_URI=mongodb://localhost:27007
MONGODB_DATABASE=mini_rag
MONGO_INITDB_ROOT_USERNAME=your_username
MONGO_INITDB_ROOT_PASSWORD=your_password
FILE_ALLOWED_TYPES=["pdf","txt","md"]
FILE_MAX_SIZE=10485760
FILE_DEFAULT_CHUNK_SIZE=4096
```

## Running the Application

Start the FastAPI development server:

```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

## API

Once the server is running:

- Health check: `GET /api/v1/health`
- Upload file: `POST /api/v1/data/upload/{project_id}`
- Process files: `POST /api/v1/data/process/{project_id}`
- Swagger UI: `http://127.0.0.1:5000/docs`

### Upload file

Send a multipart form request with a `file` field.

### Process files

Send a JSON body like this:

```json
{
	"file_id": null,
	"chunk_size": 100,
	"overlap_size": 20,
	"do_reset": false
}
```

If `file_id` is omitted or null, the API processes all uploaded files for the project.

## View Data In MongoDB Compass

To inspect the stored data, connect MongoDB Compass to:

```text
mongodb://your_username:your_password@localhost:27007/?authSource=admin
```

Then open the `mini_rag` database and inspect the `projects`, `assets`, and `chunks` collections.