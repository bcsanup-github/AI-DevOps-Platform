# AI DevOps Assistant

A self-hosted AI assistant with login, per-user chat history and a local LLM.

- **FastAPI** backend (login/register, chat, history)
- **Ollama** local LLM (default model `llama3.2:1b`)
- **PostgreSQL** for users and chat history
- **Docker Compose** for local runs, **Kubernetes (k3s)** + **Terraform (Azure)** for deployment
- **GitHub Actions** builds the image and rolls out the deployment

## Run locally (Docker Compose)

```bash
# 1. Create your env file (first time only), then edit the passwords / SECRET_KEY
cp .env.example .env

# 2. Build and start everything
docker compose up -d --build

# 3. Download the model into Ollama (first time only, ~1.3 GB)
docker exec -it ai-ollama ollama pull llama3.2:1b

# 4. Open the app
#    http://localhost:8000  -> "Create account", then chat
```

Useful commands:

```bash
docker compose logs -f backend    # backend logs
docker compose down               # stop (data is kept in volumes)
docker compose down -v            # stop AND delete the database + models
```

> Using a different model? Set `OLLAMA_MODEL` in `.env` and `ollama pull` that same model.

## Run the backend without Docker (development)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate            # Windows  (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt

# Use SQLite and an Ollama running on your machine
set DATABASE_URL=sqlite:///./dev.db
set OLLAMA_HOST=http://localhost:11434
uvicorn app.main:app --reload
```

## Environment variables

| Name | Purpose |
|---|---|
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` / `POSTGRES_HOST` / `POSTGRES_PORT` | Database connection |
| `DATABASE_URL` | Optional, overrides the Postgres settings (e.g. `sqlite:///./dev.db`) |
| `OLLAMA_HOST` | Ollama URL (`http://ollama:11434` in Compose, `http://ai-ollama:11434` in k8s) |
| `OLLAMA_MODEL` | Model name, must be pulled into Ollama |
| `SECRET_KEY` | Signs the login cookie. Use a long random value in production |

## Deploy to Kubernetes

```bash
kubectl create secret generic backend-secret --from-literal=SECRET_KEY=$(openssl rand -hex 32)
kubectl apply -f k8s/
kubectl exec -it deploy/ollama -- ollama pull llama3.2:1b
```
