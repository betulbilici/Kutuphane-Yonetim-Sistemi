Kütüphane Yönetim Sistemi
Bu proje, Global AI Hub Python 202 Bootcamp'i kapsamında geliştirilmiş, Nesne Yönelimli Programlama (OOP), Harici API Kullanımı ve FastAPI ile kendi API'nizi oluşturma konularını birleştiren bir kütüphane yönetim sistemidir.

Proje üç ana aşamadan oluşur:

Aşama 1: OOP ile Terminalde Çalışan Kütüphane: Kitapları ekleme, silme, listeleme ve arama gibi temel kütüphane işlemlerini komut satırında gerçekleştiren bir uygulama. Kitap verileri library.json dosyasında kalıcı olarak saklanır.

Aşama 2: Harici API ile Veri Zenginleştirme: Kitap ekleme işlevini geliştirerek, kullanıcıdan sadece ISBN numarası alır ve Open Library Books API'den kitap başlığı ile yazar bilgilerini otomatik olarak çeker.

Aşama 3: FastAPI ile Kendi API'nizi Oluşturma: Kütüphane mantığını bir web servisine dönüştürerek, GET /books, POST /books ve DELETE /books/{isbn} gibi RESTful API endpoint'leri sunar.

Kurulum
Projeyi yerel makinenizde çalıştırmak için aşağıdaki adımları takip edin:

Depoyu Klonlayın:

git clone <proje_depo_linki>
cd <proje_klasörü>

(Yukarıdaki <proje_depo_linki> ve <proje_klasörü> yerine kendi GitHub deponuzun URL'sini ve klasör adını yazmanız gerekmektedir.)

Sanal Ortam Oluşturun (Önerilen):
Python bağımlılıklarını izole etmek için bir sanal ortam oluşturmak iyi bir uygulamadır.

python -m venv venv

Sanal Ortamı Aktif Edin:

Windows:

.\venv\Scripts\activate

macOS/Linux:

source venv/bin/activate

Bağımlılıkları Kurun:
requirements.txt dosyasındaki tüm gerekli kütüphaneleri kurun:

pip install -r requirements.txt

Kullanım (Usage)
Aşama 1 ve 2: Terminal Uygulaması
Terminal uygulamasını çalıştırmak için:

python main.py

Uygulama çalıştıktan sonra, komut satırında etkileşimli bir menü ile karşılaşacaksınız. ISBN ile kitap ekleme işlevi, Aşama 2'deki API entegrasyonu sayesinde otomatik olarak Open Library'den bilgi çekecektir.

Aşama 3: API Sunucusu
API sunucusunu başlatmak için:

uvicorn api:app --reload

Sunucu varsayılan olarak http://127.0.0.1:8000 adresinde çalışacaktır.

API dokümantasyonuna ve etkileşimli test arayüzüne (Swagger UI) erişmek için tarayıcınızda şu adresi ziyaret edin:

Swagger UI: http://127.0.0.1:8000/docs

ReDoc: http://127.0.0.1:8000/redoc

API Dokümantasyonu (FastAPI)
FastAPI otomatik olarak etkileşimli API dokümantasyonu sağlar. /docs adresinde bulabileceğiniz ana endpoint'ler şunlardır:

GET /books
Açıklama: Kütüphanedeki tüm kitapların listesini döndürür.

Yanıt: List[BookOutput] (Kitap nesnelerinin JSON listesi)

POST /books
Açıklama: Yeni bir kitabı kütüphaneye ekler. Gönderilen ISBN'e göre Open Library API'sinden kitap bilgilerini çeker.

İstek Gövdesi (Request Body):

{
  "isbn": "978-0321765723"
}

Yanıt (Başarılı): 201 Created, BookOutput (Eklenen kitabın JSON bilgileri)

Yanıt (Hatalı): 400 Bad Request (Kitap zaten varsa veya ISBN bulunamazsa)

DELETE /books/{isbn}
Açıklama: Belirtilen ISBN'e sahip kitabı kütüphaneden siler.

Parametreler:

isbn (path): Silinecek kitabın ISBN numarası.

Yanıt (Başarılı): 204 No Content

Yanıt (Hatalı): 404 Not Found (Kitap bulunamazsa)

Test Senaryoları
Projenin farklı aşamaları için Pytest kullanılarak testler yazılmıştır. Testleri çalıştırmak için:

pytest

veya belirli bir test dosyasını çalıştırmak için:

pytest test_book_manager.py
pytest test_api.py

Bonus: Commit Geçmişi Önerisi
Projenin geliştirme aşamalarını yansıtmak için anlamlı commit mesajları kullanılması önerilir. Örneğin:

"Aşama 1: Book ve Library sınıfları oluşturuldu"

"Aşama 1: main.py terminal uygulaması eklendi"

"Aşama 1: Pytest için temel testler yazıldı"

"Aşama 2: httpx ve Open Library API entegrasyonu tamamlandı"

"Aşama 2: API hata yönetimi eklendi"

"Aşama 2: API entegrasyonu için testler güncellendi"

"Aşama 3: FastAPI uygulaması ve temel endpointler oluşturuldu"

"Aşama 3: Pydantic modelleri ve API testleri eklendi"

"requirements.txt ve README.md güncellendi"