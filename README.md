# LearnTwin AI Core

Offline desktop AI learning companion backend for the LearnTwin AI project.

## Overview

This repository contains the FastAPI-based AI core and digital twin integration layer.

Responsibilities:
- FastAPI REST API surface for observation ingestion and recommendations
- Digital twin state management
- Ollama integration using Qwen2.5-VL
- ChromaDB semantic retrieval
- SQLAlchemy models for PostgreSQL persistence

## Architecture

Observation Layer → Digital Twin → Recommendation Engine

The backend exposes REST contracts for external modules to:
- post observations
- refresh and query digital twin state
- request learning recommendations

## Quickstart

1. Create a Python virtual environment
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment variables in `.env`
   ```text
   DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/learntwin
   OLLAMA_API_URL=http://127.0.0.1:11434
   OLLAMA_MODEL=qwen2.5-vl
   CHROMA_PERSIST_DIR=.chromadb
   ```
4. Start the application
   ```bash
   uvicorn app.main:app --reload
   ```

## API Contracts

- `POST /api/v1/observations`
- `GET /api/v1/digital-twin/{user_id}`
- `POST /api/v1/digital-twin/{user_id}/refresh`
- `POST /api/v1/recommendations/{user_id}`
- `GET /api/v1/recommendations/{user_id}/history`
- `GET /api/v1/status`
