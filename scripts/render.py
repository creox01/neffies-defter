"""Render: Notion satirlarini public/ altinda statik HTML'e cevirir. Sadece okur."""
import html
import pathlib
import re
import shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
TPL = ROOT / "site" / "templates"
ASSETS = ROOT / "site" / "assets"
PUBLIC = ROOT / "public"

_TR = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosucgiosu")


def slugify(text):
    text = text.translate(_TR).lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text[:60] or "yazi"


def _prop_text(page, name):
    rt = page["properties"][name]["rich_text"]
    return "".join(t["plain_text"] for t in rt)


def _prop_select(page, name):
    val = page["properties"][name]["select"]
    return val["name"] if val else ""


def _prop_title(page):
    t = page["properties"]["Başlık"]["title"]
    return "".join(x["plain_text"] for x in t)


def _prop_date(page):
    d = page["properties"]["Yayın Tarihi"]["date"]
    return d["start"] if d else ""


def _split_gorsel(text):
    parts = [p.strip() for p in text.split("::")]
    url = parts[0] if len(parts) > 0 else ""
    credit = parts[1].replace("/ Unsplash", "").strip() if len(parts) > 1 else ""
    link = parts[2] if len(parts) > 2 else url
    return url, credit, link


def _split_kaynak(text):
    parts = [p.strip() for p in text.split("::")]
    name = parts[0] if parts else text
    link = parts[1] if len(parts) > 1 else ""
    if link:
        return f'{html.escape(name)}, <a href="{html.escape(link)}">bağlantı</a>'
    return html.escape(name)


def build(pages, get_body):
    """pages: Notion sayfalari. get_body: page_id -> [paragraf]. public/ klasorunu kurar."""
    if PUBLIC.exists():
        shutil.rmtree(PUBLIC)
    (PUBLIC / "posts").mkdir(parents=True)
    shutil.copytree(ASSETS, PUBLIC / "assets")

    post_tpl = (TPL / "post.html").read_text(encoding="utf-8")
    index_tpl = (TPL / "index.html").read_text(encoding="utf-8")

    cards = []
    rows = sorted(pages, key=_prop_date, reverse=True)
    for page in rows:
        title = _prop_title(page)
        category = _prop_select(page, "Kategori")
        kiyi = _prop_select(page, "Kıyı")
        date = _prop_date(page)
        sources = _split_kaynak(_prop_text(page, "Kaynaklar"))
        img_url, img_credit, img_link = _split_gorsel(_prop_text(page, "Görsel Bağlantısı"))
        paras = get_body(page["id"])
        slug = slugify(title)
        dateline = f"{date} · {_prop_text(page, 'Kaynaklar').split('::')[0].strip()}"

        body_html = "\n    ".join(f"<p>{html.escape(p)}</p>" for p in paras)
        post = (post_tpl
                .replace("{{TITLE}}", html.escape(title))
                .replace("{{CATEGORY}}", html.escape(category))
                .replace("{{KIYI}}", html.escape(kiyi))
                .replace("{{DATELINE}}", html.escape(dateline))
                .replace("{{IMG_URL}}", html.escape(img_url))
                .replace("{{IMG_QUERY}}", html.escape(category))
                .replace("{{IMG_CREDIT}}", html.escape(img_credit))
                .replace("{{IMG_LINK}}", html.escape(img_link))
                .replace("{{BODY}}", body_html)
                .replace("{{SOURCES}}", sources))
        (PUBLIC / "posts" / f"{slug}.html").write_text(post, encoding="utf-8")

        cards.append(
            f'<a class="card" data-cat="{html.escape(category)}" href="posts/{slug}.html">'
            f'<p class="eyebrow"><span>{html.escape(category)}</span>'
            f'<span class="kiyi">{html.escape(kiyi)}</span></p>'
            f'<h2>{html.escape(title)}</h2>'
            f'<p class="dateline">{html.escape(date)}</p></a>'
        )

    index = index_tpl.replace("{{CARDS}}", "\n".join(cards) or "<p>Henüz yayın yok.</p>")
    (PUBLIC / "index.html").write_text(index, encoding="utf-8")
    return len(rows)
