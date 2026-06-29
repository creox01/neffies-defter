"""Secim ve yazim. Ses spesifikasyonu sistem talimati olarak kullanilir."""
import pathlib
import anthropic

SELECT_MODEL = "claude-haiku-4-5"
DRAFT_MODEL = "claude-sonnet-4-6"

_SPEC = pathlib.Path(__file__).with_name("voice_spec.md").read_text(encoding="utf-8")
_client = anthropic.Anthropic()  # ANTHROPIC_API_KEY env'den, yoksa fail fast

_SELECT_TOOL = {
    "name": "secimleri_bildir",
    "description": "Secilen adaylari yapilandirilmis olarak dondur.",
    "input_schema": {
        "type": "object",
        "properties": {
            "secimler": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "index": {"type": "integer"},
                        "kategori": {"type": "string"},
                        "kiyi": {
                            "type": "string",
                            "enum": ["Fransa kıyısı", "Ege kıyısı", "İki kıyı"],
                        },
                    },
                    "required": ["index", "kategori", "kiyi"],
                },
            }
        },
        "required": ["secimler"],
    },
}

_DRAFT_TOOL = {
    "name": "yaziyi_bildir",
    "description": "Tamamlanan yaziyi yapilandirilmis olarak dondur.",
    "input_schema": {
        "type": "object",
        "properties": {
            "baslik": {"type": "string"},
            "govde": {"type": "string"},
            "image_query": {"type": "string"},
        },
        "required": ["baslik", "govde", "image_query"],
    },
}


def _tool_input(msg, tool_name):
    for block in msg.content:
        if block.type == "tool_use" and block.name == tool_name:
            return block.input
    raise RuntimeError(f"{tool_name} araci cagrilmadi")


def select(candidates):
    """Adaylardan yazilmaya degerleri secer. candidates: [{title, summary, source, category}]."""
    listing = "\n".join(
        f"[{i}] ({c['category']}) {c['title']} :: {c['summary'][:200]}"
        for i, c in enumerate(candidates)
    )
    system = (
        _SPEC + "\n\nGOREV: Asagidaki adaylardan en fazla 2 tanesini sec. "
        "Bir aday ancak bir kategoriye net oturuyorsa, somut bir Neffies cikarimi varsa "
        "ve genel gecer trend tekrari degilse secilir. Hicbiri uygun degilse bos liste don."
    )
    msg = _client.messages.create(
        model=SELECT_MODEL, max_tokens=600,
        system=system,
        tools=[_SELECT_TOOL],
        tool_choice={"type": "tool", "name": "secimleri_bildir"},
        messages=[{"role": "user", "content": listing}],
    )
    return _tool_input(msg, "secimleri_bildir")["secimler"]


def draft(item):
    """Secilen tek bir adayi senin sesinde tam yaziya cevirir."""
    user = (
        f"Kategori: {item['kategori']}\nKıyı: {item['kiyi']}\n"
        f"Kaynak yayin: {item['source']}\nKaynak baglanti: {item['link']}\n"
        f"Haber basligi: {item['title']}\nHaber ozeti: {item['summary']}\n\n"
        "Bu gelismeyi ses spesifikasyonuna gore tam yaziya cevir. "
        "image_query kurali: Unsplash stok aramasi icin EN FAZLA 2 genel ingilizce kelime. "
        "Ozel isim, yer adi, bolge adi, uzum ya da sarap adi YASAK. Sadece genel atmosfer terimi. "
        "Ornekler: open fire, wine cellar, stone courtyard, fresh bread, cozy room."
    )
    msg = _client.messages.create(
        model=DRAFT_MODEL, max_tokens=1500,
        system=_SPEC,
        tools=[_DRAFT_TOOL],
        tool_choice={"type": "tool", "name": "yaziyi_bildir"},
        messages=[{"role": "user", "content": user}],
    )
    return _tool_input(msg, "yaziyi_bildir")
