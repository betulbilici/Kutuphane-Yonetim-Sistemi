
# Kütüphane Yönetim Sistemi

Bu proje, Global AI Hub Python 202 Bootcamp'i kapsamında geliştirilmiş, Nesne Yönelimli Programlama (OOP), Harici API Kullanımı ve FastAPI ile kendi API'nizi oluşturma konularını birleştiren kapsamlı bir kütüphane yönetim sistemidir.

Proje üç ana aşamadan oluşur:
- **Aşama 1:** OOP ile terminal tabanlı kütüphane uygulaması
- **Aşama 2:** Open Library API entegrasyonu ile kitap bilgilerini otomatik çekme
- **Aşama 3:** FastAPI ile web tabanlı RESTful API servisi

## 📦 Kurulum

### Adımlar
1. Depoyu klonlayın:
```bash
git clone https://github.com/betulbilici/Kutuphane-Yonetim-Sistemi.git
cd kutuphane-yonetim-sistemi
```

2. Sanal ortam oluşturun ve aktif edin:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

## 🚀 Kullanım

### Aşama 1 & 2: Terminal Uygulaması
Terminal tabanlı kütüphane yönetim sistemini çalıştırmak için:
```bash
python main.py
```

**Menü Seçenekleri:**
1. 📚 Kitabı ISBN ile API'den Ekle
2. 📝 Kitabı Manuel Olarak Ekle
3. 🗑️ Kitap Sil (ISBN ile)
4. 📋 Kitapları Listele
5. 🔍 Kitap Ara (ISBN ile)
6. 🔎 Kitap Ara (Başlık/Yazar ile)
7. 📊 Kütüphane İstatistikleri
8. 🚪 Çıkış

### Aşama 3: API Sunucusu
FastAPI tabanlı web servisini başlatmak için:
```bash
uvicorn api:app --reload
```

Sunucu varsayılan olarak http://127.0.0.1:8000 adresinde çalışacaktır.

## 📚 API Dokümantasyonu

### Interaktif Dokümantasyon
- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

### Endpoint'ler

#### GET /books
**Açıklama:** Kütüphanedeki tüm kitapları listeler

**Yanıt:**
```json
[
  {
    "title": "1984",
    "author": "George Orwell",
    "isbn": "978-0451524935"
  }
]
```

#### POST /books
**Açıklama:** ISBN numarası ile yeni kitap ekler (Open Library API'den otomatik veri çeker)

**İstek Gövdesi:**
```json
{
  "isbn": "978-0321765723"
}
```

**Başarılı Yanıt (201):**
```json
{
  "title": "Design Patterns",
  "author": "Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides",
  "isbn": "978-0321765723"
}
```

#### DELETE /books/{isbn}
**Açıklama:** Belirtilen ISBN numarasına sahip kitabı siler

**Parametre:**
- `isbn` (path): Silinecek kitabın ISBN numarası

**Başarılı Yanıt:** 204 No Content

## 🧪 Testler

Proje kapsamlı testlerle desteklenmiştir:

### Sınıf Testleri
```bash
pytest test_classes.py -v
```

### API Testleri
```bash
pytest test_api.py -v
```

### Tüm Testler
```bash
pytest
```

## 📁 Proje Yapısı

```
kutuphane-yonetim-sistemi/
├── api.py              # FastAPI uygulaması
├── classes.py          # Book ve Library sınıfları
├── main.py             # Terminal uygulaması
├── library.json        # Veri deposu (otomatik oluşturulur)
├── requirements.txt    # Bağımlılıklar
├── test_api.py         # API testleri
├── test_classes.py     # Sınıf testleri
└── README.md           Bu dosya
```

## 🔧 Teknolojiler

- **Python 3.8+** - Programlama dili
- **FastAPI** - Web framework
- **Pydantic** - Veri doğrulama
- **HTTPX** - HTTP istemcisi (async)
- **Pytest** - Test framework
- **Uvicorn** - ASGI sunucu


---



