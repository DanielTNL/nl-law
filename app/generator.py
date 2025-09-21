from typing import List, Dict
import httpx
from app.settings import OPENAI_API_KEY, GEN_MODEL

SYSTEM = (
"Je bent een juridisch assistent. Antwoord bondig en precies in het Nederlands. "
"Gebruik alleen informatie uit de meegeleverde passages. "
"Geef altijd bronverwijzingen met (Titel, art., lid, versie) en de link."
)

def format_citations(hits: List[Dict]) -> str:
    lines=[]
    for h in hits:
        lid = f", lid {h['lid']}" if h['lid'] else ""
        lines.append(f"- [{h['titel']}, art. {h['artikel']}{lid}, versie {h['versie_van']}]({h['bron_url']})")
    return "\n".join(lines)

async def answer(query: str, hits: List[Dict]) -> str:
    context = "\n\n".join([f"[{i+1}] {h['text']}" for i,h in enumerate(hits)])
    user = (
        f"Vraag: {query}\n\n"
        f"Relevante passages:\n{context}\n\n"
        "Instructies:\n"
        "- Geef eerst een kort antwoord (2–4 zinnen).\n"
        "- Voeg daarna 'Relevante bepalingen' toe met bullets.\n"
        "- Citeer alleen uit de passages; geen aannames.\n"
    )
    async with httpx.AsyncClient(timeout=120) as s:
        r = await s.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={
                "model": GEN_MODEL,
                "temperature": 0.2,
                "messages": [
                    {"role":"system","content":SYSTEM},
                    {"role":"user","content":user}
                ]
            }
        )
        r.raise_for_status()
        out = r.json()["choices"][0]["message"]["content"]
    cites = format_citations(hits)
    return f"{out}\n\n**Relevante bepalingen**\n{cites}"
