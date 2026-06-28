"""Secim ve yazim. Ses spesifikasyonu sistem talimati olarak kullanilir."""
import json
import os
import pathlib
import anthropic

SELECT_MODEL = "claude-haiku-4-5"
DRAFT_MODEL = "claude-sonnet-4-6"

_SPEC = pathlib.Path(__file__).with_name("voice_spec.md").read_text(encoding="utf-8")
_client = anthropic.Anthropic()  # ANTHROPIC_API_KEY env'den, yoksa fail fast


def _parse_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


def select(candidates):
    """Adaylardan yazilmaya degerleri secer. candidates: [{title, summary, source, category}]."""
    listing = "\n".join(
        f"[{i}] ({c['category']}) {c['title']} :: {c['summary'][:200]}"
        for i, c in enumerate(candidates)
    )
    system = (
        _SPEC + "\n\nGOREV: Asagidaki adaylardan en fazla 2 tanesini sec. "
        "Bir aday ancak bir kategoriye net oturuyorsa, somut bir Neffies cikarimi varsa "
        "ve genel gecer trend tekrari degilse secilir. Hicbiri uygun degilse bos liste don. "
        "SADECE JSON don, baska metin yok: "
        '[{"index": 0, "kategori": "...", "kiyi": "Fransa kıyısı|Ege kıyısı|İki kıyı"}]'
    )
    msg = _client.messages.create(
        model=SELECT_MODEL, max_tokens=600,
        system=system,
        messages=[{"role": "user", "content": listing}],
    )
    return _parse_json(msg.content[0].text)


def draft(item):
    """Secilen tek bir adayi senin sesinde tam yaziya cevirir."""
    user = (
        f"Kategori: {item['kategori']}\nKıyı: {item['kiyi']}\n"
        f"Kaynak yayin: {item['source']}\nKaynak baglanti: {item['link']}\n"
        f"Haber basligi: {item['title']}\nHaber ozeti: {item['summary']}\n\n"
        "Bu gelismeyi ses spesifikasyonuna gore tam yaziya cevir. "
        "image_query kurali: Unsplash stok aramasi icin EN FAZLA 2 genel ingilizce kelime. "
        "Ozel isim, yer adi, bolge adi, uzum ya da sarap adi YASAK. Sadece genel atmosfer terimi. "
        "Ornekler: open fire, wine cellar, stone courtyard, fresh bread, cozy room. "
        "SADECE JSON don, baska metin yok: "
        '{"baslik": "...", "govde": "paragraflar, bos satirla ayrilmis", '
        '"image_query": "iki kelimelik genel atmosfer"}'
    )
    msg = _client.messages.create(
        model=DRAFT_MODEL, max_tokens=1500,
        system=_SPEC,
        messages=[{"role": "user", "content": user}],
    )
    return _parse_json(msg.content[0].text)
