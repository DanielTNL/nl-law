import asyncio, datetime, httpx, re
from lxml import etree

SRU = "https://zoekservice.overheid.nl/sru/Search"

def sru_query(from_date: str):
    q = f"modificatie>={from_date}"
    return f"{SRU}?operation=searchRetrieve&version=1.2&x-connection=BWB&maximumRecords=100&query={q}"

async def fetch_sru(url: str) -> str:
    async with httpx.AsyncClient(timeout=60) as s:
        r = await s.get(url)
        r.raise_for_status()
        return r.text

def parse_sru(xml_text: str):
    root = etree.fromstring(xml_text.encode("utf-8"))
    ns = root.nsmap
    ids = []
    for rec in root.findall(".//{*}recordData", ns):
        txt = "".join(rec.itertext())
        m = re.search(r"(BWBR\d+)", txt)
        if m: ids.append(m.group(1))
    return sorted(set(ids))

async def update_since(days_back=1):
    since = (datetime.date.today()-datetime.timedelta(days=days_back)).isoformat()
    url = sru_query(since)
    xml = await fetch_sru(url)
    bwbrs = parse_sru(xml)
    print("Gewijzigde regelingen sinds", since, "→", bwbrs)
    # TODO: download relevante XML's, opnieuw parsen, re-indexen.

if __name__ == "__main__":
    asyncio.run(update_since(1))
