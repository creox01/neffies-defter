# Neffies Defter

Sektörel know-how akışı. Robot haftada 2-3 kez kaynakları tarar, Cem'in sesinde taslak yazar, Notion'a düşürür. Sen onaylarsın, site kendini günceller.

İki iş vardır. Toplama taslak üretir. Yayın onaylananı siteye taşır. İkisi de GitHub Actions üzerinde kendiliğinden çalışır.

---

## Kurulum, sırayla

### 1. Boş depo aç
GitHub'da yeni bir depo: `neffies-defter`. README ekleme, boş bırak.

### 2. İçeriği push et
Bu klasörün içinde, terminalde:

```
git init
git add .
git commit -m "neffies defter ilk kurulum"
git branch -M main
git remote add origin https://github.com/KULLANICI/neffies-defter.git
git push -u origin main
```

`KULLANICI` yerine kendi GitHub kullanıcı adın.

### 3. Üç anahtarı üret

**Anthropic API anahtarı**
console.anthropic.com, API keys, Create key. Kopyala. Ücretli, bu hacimde maliyet küçük.

**Unsplash Access Key**
unsplash.com/developers, New Application, Access Key'i kopyala. Ücretsiz.

**Notion entegrasyon token'ı**
notion.so/my-integrations, New integration, internal, secret'i kopyala.

### 4. Notion veritabanını entegrasyonla paylaş
Defter veritabanını aç, sağ üst menü, Connections, 3. adımda oluşturduğun entegrasyonu ekle. Sonra veritabanının ID'sini al: tarayıcıdaki URL'de `notion.so/...?v=...` öncesindeki 32 karakterlik kısım. Bu `NOTION_DB_ID`.

### 5. Anahtarları depoya secret olarak gir
Depo, Settings, Secrets and variables, Actions, New repository secret. Dört tane gir:

- `ANTHROPIC_API_KEY`
- `UNSPLASH_ACCESS_KEY`
- `NOTION_TOKEN`
- `NOTION_DB_ID`

Bunlar şifreli durur, kodda açık yazmaz.

### 6. GitHub Pages'i aç
Depo, Settings, Pages, Source: GitHub Actions seç. Kendi domainini Custom domain alanına gir, DNS'te CNAME kaydını GitHub'a yönlendir.

---

## Test et

1. Depo, Actions, **toplama**, Run workflow. Birkaç dakika sonra Notion Defter'de Taslak satırları belirir.
2. Bir taslağı aç, oku. İyiyse Durum'u **Onaylandı**'ya çevir.
3. Actions, **yayın**, Run workflow. Site yayına girer, satır Yayında olur.

Kurulumdan sonra ikisi de kendi takvimiyle çalışır. Toplama Pazartesi, Çarşamba, Cuma. Yayın altı saatte bir. Elle çalıştırmak her zaman mümkün.

---

## Çalışma mantığı

- Tek doğru kaynak Notion'dur. Site her yayında Notion'dan baştan üretilir, kopya tutulmaz.
- Robot uydurmaz. Kaynakta olmayan sayı veya alıntı yazıya girmez. Kurallar `scripts/voice_spec.md` içinde.
- Bir feed çalışmazsa o feed atlanır, çalışma durmaz. Anahtar eksikse iş baştan durur.

## Dosyalar

```
scripts/voice_spec.md   sesin ve yazım kuralları, robotun beyni
scripts/sources.py      kaynak feed listesi
scripts/ingest.py       toplama isi
scripts/publish.py      yayin isi
scripts/render.py       Notion satirlarini HTML'e ceviren render
site/templates/         site sablonlari
site/assets/            logo ve stil
```

Kaynak eklemek için `scripts/sources.py`. Sesi değiştirmek için `scripts/voice_spec.md`. İkisi de düz metin, korkmadan düzenle.
