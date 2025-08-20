import json
import httpx
import os
from typing import List, Optional

# Book sınıfı, bir kitabı temsil eder.
class Book:
    def __init__(self, title: str, author: str, isbn: str):
        """
        Book sınıfının yapıcı metodu.
        Args:
            title (str): Kitabın başlığı.
            author (str): Kitabın yazarı.
            isbn (str): Kitabın ISBN numarası (benzersiz kimlik).
        """
        self.title = title
        self.author = author
        self.isbn = isbn

    def __str__(self) -> str:
        """
        Kitap bilgilerini okunabilir bir string formatında döndürür.
        Örn: "Ulysses by James Joyce (ISBN: 978-0199535675)"
        """
        return f"{self.title} by {self.author} (ISBN: {self.isbn})"

    def to_dict(self) -> dict:
        """
        Book nesnesini bir sözlüğe dönüştürür. JSON'a kaydetmek için kullanılır.
        """
        return {"title": self.title, "author": self.author, "isbn": self.isbn}

    @classmethod
    def from_dict(cls, data: dict):
        """
        Sözlükten bir Book nesnesi oluşturur. JSON'dan yüklemek için kullanılır.
        Args:
            data (dict): Kitap bilgilerini içeren sözlük.
        Returns:
            Book: Oluşturulan Book nesnesi.
        """
        return cls(data['title'], data['author'], data['isbn'])

# Library sınıfı, tüm kütüphane operasyonlarını yönetir.
class Library:
    def __init__(self, data_file: str = 'library.json'):
        """
        Library sınıfının yapıcı metodu.
        Args:
            data_file (str): Kitap verilerinin saklanacağı JSON dosyasının adı. Varsayılan 'library.json'.
        """
        self.data_file = data_file
        self._books: List[Book] = []
        self.load_books() # Uygulama başladığında kitapları yükle

    @property
    def books(self) -> List[Book]:
        """Kütüphanedeki kitapların listesini döndürür."""
        return self._books

    def load_books(self) -> bool:
        """
        library.json dosyasından kitapları yükler. Dosya yoksa veya boşsa, boş bir liste ile başlar.
        Returns:
            bool: Yükleme başarılıysa True, aksi takdirde False.
        """
        if not os.path.exists(self.data_file):
            # Dosya yoksa, boş bir liste ile başla ve hata döndürme
            self._books = []
            return False
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._books = [Book.from_dict(book_data) for book_data in data]
            return True
        except json.JSONDecodeError:
            print(f"Hata: {self.data_file} dosyası bozuk veya boş. Yeni bir dosya oluşturulacak.")
            self._books = [] # Dosya bozuksa, boş liste ile başla
            return False
        except FileNotFoundError: # Bu aslında os.path.exists kontrolü nedeniyle buraya gelmemeli
            self._books = []
            return False
        except Exception as e:
            print(f"Veri yükleme hatası: {e}")
            self._books = []
            return False

    def save_books(self) -> bool:
        """
        Kütüphanedeki tüm kitap listesini JSON dosyasına yazar.
        Returns:
            bool: Kaydetme başarılıysa True, aksi takdirde False.
        """
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump([book.to_dict() for book in self.books], f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Veri kaydetme hatası: {e}")
            return False

    def add_book_manual(self, book: Book) -> bool:
        """
        Manuel olarak bir Book nesnesini kütüphaneye ekler ve dosyayı günceller.
        Args:
            book (Book): Eklenecek Book nesnesi.
        Returns:
            bool: Kitap başarıyla eklendiyse True, aksi takdirde False.
        """
        if not book.isbn.strip() or not book.title.strip() or not book.author.strip():
            print("Hata: Kitap bilgileri (başlık, yazar, ISBN) boş olamaz.")
            return False

        if any(b.isbn == book.isbn for b in self._books):
            print(f"Hata: Bu ISBN'ye sahip kitap kütüphanede zaten mevcut: {book.isbn}")
            return False
        
        self._books.append(book)
        self.save_books()
        print(f"Kitap başarıyla manuel olarak eklendi: {book}")
        return True

    async def add_book_from_api(self, isbn: str) -> Optional[Book]:
        """
        Yeni bir Book nesnesini kütüphaneye Open Library API'sinden çekerek ekler.
        Yazar adlarını almak için ek API çağrıları yapabilir.
        Args:
            isbn (str): Eklenecek kitabın ISBN numarası.
        Returns:
            Book: Başarılı olursa eklenen Book nesnesi, aksi takdirde None.
        """
        # ISBN boşsa hata döndür
        if not isbn.strip():
            print("Hata: ISBN boş olamaz.")
            return None

        # Kitap zaten mevcut mu kontrol et
        if any(book.isbn == isbn for book in self.books):
            print(f"Hata: ISBN {isbn} zaten kütüphanede mevcut.")
            return None

        # Open Library API'den kitap bilgilerini çekme
        api_url = f"https://openlibrary.org/isbn/{isbn}.json"
        try:
            # Ana kitap bilgisi için httpx.AsyncClient kullan
            async with httpx.AsyncClient() as main_client:
                response = await main_client.get(api_url, timeout=10.0, follow_redirects=True)
                
                if not response.is_success:
                    if response.status_code == 404:
                        print(f"Hata: Verilen ISBN ({isbn}) ile kitap bulunamadı.")
                    elif response.status_code == 302:
                        print(f"Hata: API isteği bir yönlendirme hatasıyla karşılaştı. ISBN için bilgi alınamadı: {isbn}.")
                    else:
                        print(f"Hata: API'den beklenmeyen durum kodu: {response.status_code} (ISBN: {isbn}).")
                    return None
                
                data = response.json()

            title = data.get('title')
            authors_list = data.get('authors') # Bu bir liste veya None olabilir
            
            author_names = "Bilinmiyor"
            if authors_list:
                fetched_author_names = []
                # Her bir yazar bilgisi için döngü
                for author_info in authors_list:
                    if isinstance(author_info, dict) and 'name' in author_info:
                        # Eğer 'name' doğrudan varsa, kullan
                        fetched_author_names.append(author_info['name'])
                    elif isinstance(author_info, dict) and 'key' in author_info:
                        # Eğer sadece 'key' varsa, yazar detaylarını çekmek için ek API çağrısı yap
                        author_key = author_info['key']
                        author_detail_url = f"https://openlibrary.org{author_key}.json"
                        try:
                            # Yazar detayları için YENİ bir httpx.AsyncClient örneği kullan
                            async with httpx.AsyncClient() as author_client: 
                                author_response = await author_client.get(author_detail_url, timeout=5.0)
                                if author_response.is_success:
                                    author_data = author_response.json()
                                    if 'name' in author_data:
                                        fetched_author_names.append(author_data['name'])
                                    else:
                                        fetched_author_names.append("Bilinmeyen Yazar (Detay Yok)")
                                else:
                                    fetched_author_names.append(f"Bilinmeyen Yazar (API Durum Kodu: {author_response.status_code})")
                        except httpx.RequestError:
                            fetched_author_names.append("Bilinmeyen Yazar (API Hatası)")
                        except json.JSONDecodeError:
                            fetched_author_names.append("Bilinmeyen Yazar (JSON Hatası)")
                    else:
                        fetched_author_names.append("Bilinmeyen Yazar (Geçersiz Format)")
                
                if fetched_author_names:
                    author_names = ", ".join(fetched_author_names)
                else:
                    author_names = "Bilinmiyor (Yazar Bilgisi Yok)"

            if not title:
                print(f"Hata: API'den kitap başlığı alınamadı (ISBN: {isbn}).")
                return None

            new_book = Book(title, author_names, isbn)
            self._books.append(new_book)
            self.save_books()
            print(f"Kitap başarıyla API aracılığıyla eklendi: {new_book}")
            return new_book

        except httpx.RequestError as e:
            print(f"Hata: API isteği başarısız oldu (ağ hatası, DNS sorunu vb.) - {e} (ISBN: {isbn}). Lütfen internet bağlantınızı kontrol edin veya ISBN'i doğrulayın.")
            return None
        except json.JSONDecodeError:
            print(f"Hata: API yanıtı JSON olarak ayrıştırılamadı. Yanlış format veya boş yanıt (ISBN: {isbn}).")
            return None
        except Exception as e:
            print(f"Beklenmeyen bir hata oluştu: {e} (ISBN: {isbn}).")
            return None

    def remove_book(self, isbn: str) -> bool:
        """
        ISBN numarasına göre bir kitabı kütüphaneden siler.
        Args:
            isbn (str): Silinecek kitabın ISBN numarası.
        Returns:
            bool: Kitap başarıyla silindiyse True, bulunamadıysa False.
        """
        initial_len = len(self._books)
        # Sadece belirtilen ISBN'ye sahip olmayan kitapları koru
        self._books = [book for book in self._books if book.isbn != isbn]
        if len(self._books) < initial_len:
            self.save_books()
            print(f"ISBN {isbn} numaralı kitap başarıyla silindi.")
            return True
        else:
            print(f"Hata: ISBN {isbn} numaralı kitap kütüphanede bulunamadı.")
            return False

    def list_books(self) -> List[Book]:
        """
        Kütüphanedeki tüm kitapları listeler.
        Returns:
            list: Book nesnelerinin listesi.
        """
        if not self._books:
            print("Kütüphanede henüz kitap bulunmamaktadır.")
            return []
        else:
            print("\n--- Kütüphanedeki Kitaplar ---")
            for i, book in enumerate(self._books, 1):
                print(f"{i}. {book}")
            print("------------------------------")
            return self._books

    def find_book(self, isbn: str) -> Optional[Book]:
        """
        ISBN ile belirli bir kitabı bulur.
        Args:
            isbn (str): Aranacak kitabın ISBN numarası.
        Returns:
            Book: Bulunan Book nesnesi, bulunamazsa None.
        """
        for book in self._books:
            if book.isbn == isbn:
                print(f"Kitap bulundu: {book}")
                return book
        print(f"ISBN {isbn} numaralı kitap bulunamadı.")
        return None

    def search_books(self, query: str) -> List[Book]:
        """
        Başlık veya yazar adına göre kitapları arar.
        Args:
            query (str): Arama sorgusu.
        Returns:
            List[Book]: Arama sonuçlarına uyan kitapların listesi.
        """
        query = query.lower()
        found_books = [
            book for book in self._books
            if query in book.title.lower() or query in book.author.lower()
        ]
        if found_books:
            print(f"\n'{query}' için {len(found_books)} sonuç bulundu:")
            print("-" * 50)
            for i, book in enumerate(found_books, 1):
                print(f"{i}. {book}")
            print("-" * 50)
        else:
            print(f"'{query}' için sonuç bulunamadı.")
        return found_books

    def get_book_count(self) -> int:
        """Kütüphanedeki toplam kitap sayısını döndürür."""
        return len(self._books)

    def get_author_statistics(self) -> dict:
        """Yazar istatistiklerini (her yazarın kaç kitabı olduğunu) döndürür."""
        authors = {}
        for book in self._books:
            authors[book.author] = authors.get(book.author, 0) + 1
        return authors

    def clear_library(self) -> bool:
        """Tüm kütüphaneyi temizler ve değişiklikleri kaydeder."""
        self._books = []
        self.save_books()
        print("Kütüphanedeki tüm kitaplar silindi.")
        return True
