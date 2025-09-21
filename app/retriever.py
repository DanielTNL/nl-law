import json, httpx, asyncio
from typing import List, Dict
from qdrant_client import QdrantClient
from qdrant_client.http import models
from app.settings import QDRANT_URL, QDRANT_API_KEY, OPENAI_API_KEY, COLLECTION, EMBED_MODEL

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

def ensure_collection():
    client.recreate_collection(
        COLLECTION,
        vectors_config=models.VectorParams(size=3072, distance=models.Distance.COSINE)
    )

async def embed_texts(texts: List[str]) -> List[List[float]]:
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    async with httpx.AsyncClient(timeout=120) as s:
        r = await s.post(
            "https://api.openai.com/v1/embeddings",
            headers=headers,
            json={"model": EMBED_MODEL, "input": texts}
        )
        r.raise_for_status()
        data = r.json()["data"]
        return [d["embedding"] for d in data]

def batch(it, n=64):
    buf=[]
    for x in it:
        buf.append(x)
        if len(buf)==n:
            yield buf; buf=[]
    if buf: yield buf

async def index_jsonl(path="data/out/bwb_articles.jsonl"):
    ensure_collection()
    with open(path, "r", encoding="utf-8") as f:
        for chunk in batch((json.loads(l) for l in f), 64):
            vecs = await embed_texts([c["text"] for c in chunk])
            points = []
            for c, v in zip(chunk, vecs):
                points.append(models.PointStruct(id=c["id"], vector=v, payload=c))
            client.upsert(COLLECTION, points=points)
    print("Index built.")

async def semantic_search(query: str, top_k=5) -> List[Dict]:
    vec = (await embed_texts([query]))[0]
    res = client.search(COLLECTION, query_vector=vec, limit=top_k, with_payload=True, score_threshold=0.2)
    out=[]
    for r in res:
        p = r.payload
        out.append({
            "id": p.get("id"),
            "text": p["text"],
            "titel": p["titel"],
            "bwbr": p["bwbr"],
            "artikel": p["artikel"],
            "lid": p["lid"],
            "versie_van": p["versie_van"],
            "bron_url": p["bron_url"],
            "score": r.score
        })
    return out

if __name__ == "__main__":
    asyncio.run(index_jsonl())
