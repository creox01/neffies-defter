"""Atmosfer gorseli. Unsplash, ucretsiz lisans, atif korunur."""
import os
import requests


def search(query):
    """Konuya uygun tek atmosfer gorseli doner. Sonuc yoksa fail fast."""
    key = os.environ["UNSPLASH_ACCESS_KEY"]  # yoksa fail fast
    r = requests.get(
        "https://api.unsplash.com/search/photos",
        params={"query": query, "per_page": 1, "orientation": "landscape"},
        headers={"Authorization": f"Client-ID {key}"},
        timeout=30,
    )
    r.raise_for_status()
    results = r.json()["results"]
    if not results:
        raise RuntimeError(f"Unsplash sonuc bulamadi: {query}")
    img = results[0]
    return {
        "url": img["urls"]["regular"],
        "credit": img["user"]["name"],
        "link": img["links"]["html"],
    }
