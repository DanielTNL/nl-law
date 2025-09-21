import os, glob, json, re
from lxml import etree
from pathlib import Path

BWB_DIR = Path("data/bwb")
OUT = Path("data/out"); OUT.mkdir(parents=True, exist_ok=True)

def clean_text(txt: str) -> str:
    return re.sub(r"\s+", " ", (txt or "").strip())

def extract_articles(xml_path: str):
    tree = etree.parse(xml_path)
    ns = tree.getroot().nsmap
    bwbr = tree.findtext(".//{*}regelingIdentificatie/{*}regelingCode") or ""
    titel = (tree.findtext(".//{*}officieleTitel")
             or tree.findtext(".//{*}citeertitel") or bwbr)
    # geldigheidsdatum veldnamen kunnen per regeling verschillen; we vangen de meest voorkomende
    versie_datum = (tree.findtext(".//{*}geldigOp")
                    or tree.findtext(".//{*}inwerkingtredingsdatum")
                    or "geldend")
    for art in tree.findall(".//{*}artikel", ns):
        art_num = art.findtext(".//{*}artikelnummer") or ""
        leden = art.findall(".//{*}lid", ns) or []
        if leden:
            for lid in leden:
                lidnr = lid.get("nummer") or ""
                text = clean_text(" ".join(lid.itertext()))
                if not text: continue
                yield {
                    "bwbr": bwbr, "titel": titel, "artikel": art_num, "lid": lidnr,
                    "versie_van": versie_datum, "text": text,
                    "bron_url": f"https://wetten.overheid.nl/{bwbr}/{versie_datum}#Artikel{art_num}",
                }
        else:
            text = clean_text(" ".join(art.itertext()))
            if not text: continue
            yield {
                "bwbr": bwbr, "titel": titel, "artikel": art_num, "lid": "",
                "versie_van": versie_datum, "text": text,
                "bron_url": f"https://wetten.overheid.nl/{bwbr}/{versie_datum}#Artikel{art_num}",
            }

def main():
    outpath = OUT / "bwb_articles.jsonl"
    count = 0
    with open(outpath, "w", encoding="utf-8") as w:
        for xml in glob.glob(str(BWB_DIR / "**/*.xml"), recursive=True):
            for rec in extract_articles(xml):
                rec["id"] = f'{rec["bwbr"]}_art_{rec["artikel"]}_lid_{rec["lid"] or "0"}_{rec["versie_van"]}'
                w.write(json.dumps(rec, ensure_ascii=False) + "\n")
                count += 1
    print("Records written:", count, "→", outpath)

if __name__ == "__main__":
    main()
