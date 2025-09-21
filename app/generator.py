import os, textwrap
from typing import List, Dict
from openai import OpenAI

# Use Responses API (compatible with openai==1.47.0)
MODEL = os.getenv("CHAT_MODEL", "gpt-4.1-mini")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def _context(hits: List[Dict]) -> str:
    parts = []
    for h in hits[:5]:
        line1 = f"{h['titel']} (BWBR {h['bwbr']}, art. {h['artikel']}, lid {h['lid']}, versie {h['versie_van']})"
        line2 = h["text"]
        parts.append(f"- {line1}\n  {line2}\n  Bron: {h['bron_url']}")
    return "\n".join(parts)

async def answer(question: str, hits: List[Dict]) -> str:
    ctx = _context(hits)
    prompt = textwrap.dedent(f"""
    Jij bent een Nederlandse juridisch assistent. Beantwoord de vraag kort, feitelijk en met verwijzing
    naar relevante bepalingen. Citeer artikel- en lidnummers. Antwoord in het Nederlands.

    Vraag:
    {question}

    Context (passages uit gevonden artikelen):
    {ctx}

    Schrijf eerst 2–4 zinnen als antwoord. Zet daaronder "Bronnen:" met opsomming van titels + artikel/lid + URL.
    """).strip()

    resp = client.responses.create(model=MODEL, input=prompt)
    return resp.output_text.strip()
