# NL Law Bot (BWB RAG)

FastAPI + Qdrant + OpenAI to answer NL law questions with citations (wetten.nl links).

## Quick start (Codespaces)
1) Open repo in **GitHub Codespaces** → create `.env` from `.env.example` with your keys.
2) Put BWB XML files in `data/bwb/` (drag-drop in Codespaces).
3) `pip install -r requirements.txt`
4) `python -m app.ingest_bwb` → builds `data/out/bwb_articles.jsonl`
5) `python -m app.retriever` → indexes to Qdrant
6) `uvicorn app.api:app --reload --port 8080`
7) Open `web/index.html`, set hash to your backend URL, e.g. `index.html#https://<codespaces-url>`

## Deploy (Fly.io)
- Create a Fly app; set repo secrets:
  - `FLY_API_TOKEN`, `OPENAI_API_KEY`, `QDRANT_URL`, `QDRANT_API_KEY`
- Push to main → GitHub Action deploys.
- Host `web/` on GitHub Pages and point it to your Fly URL via hash `#`.

## Nightly updates
- Workflow `nightly-update.yml` calls `app/update_sru.py` (extend to re-index changed BWBRs).
