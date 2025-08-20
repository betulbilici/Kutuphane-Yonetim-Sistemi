import asyncio
from classes import Book, Library

def display_menu():
    """Kütüphane yönetim sistemi menüsünü ekrana basar."""
    print("\n     Kütüphane Yönetim Sistemi")
    print("=" * 50)
    print("1. Kitabı ISBN ile API'den Ekle") # API tabanlı ekleme
    print("2. Kitabı Manuel Olarak Ekle")      # Manuel ekleme
    print("3. Kitap Sil (ISBN ile)")
    print("4. Kitapları Listele")
    print("5. Kitap Ara (ISBN ile)")
    print("6. Kitap Ara (Başlık/Yazar ile)")
    print("7. Kütüphane İstatistikleri")
    print("8. Çıkış")
    print("-" * 50)

async def add_book_from_api_menu(library: Library):
    """
    Kullanıcıdan ISBN alarak yeni kitabı Open Library API'den çekip ekler.
    """
    isbn = input("\nEklemek istediğiniz kitabın ISBN numarasını girin: ").strip()
    await library.add_book_from_api(isbn)

def add_book_manual_menu(library: Library):
    """
    Kullanıcıdan manuel olarak kitap bilgilerini alarak kitap ekler.
    """
    print("\nYeni Kitap Bilgileri (Manuel Giriş):")
    title = input("Kitap Başlığı: ").strip()
    author = input("Yazar: ").strip()
    isbn = input("ISBN: ").strip()

    if not title or not author or not isbn:
        print("Hata: Kitap bilgileri eksik. Lütfen tekrar deneyin.")
        return

    new_book = Book(title, author, isbn)
    library.add_book_manual(new_book)

def remove_book_menu(library: Library):
    """Kullanıcıdan ISBN alarak kitap siler."""
    isbn = input("\nSilinecek kitabın ISBN numarasını girin: ").strip()
    if isbn:
        book = library.find_book(isbn) 
        if book:
            print(f"Silinecek kitap: {book}")
            confirm = input("Bu kitabı silmek istediğinizden emin misiniz? (e/h): ").lower()
            if confirm == 'e':
                library.remove_book(isbn)
            else:
                print("Silme işlemi iptal edildi.")
        else:
            pass
    else:
        print("Geçersiz ISBN!")

def search_book_isbn_menu(library: Library):
    """Kullanıcıdan ISBN alarak kitap arar."""
    isbn = input("\nAranacak kitabın ISBN numarasını girin: ").strip()
    if isbn:
        library.find_book(isbn) 
    else:
        print("Geçersiz ISBN!")

def search_book_text_menu(library: Library):
    """Kullanıcıdan arama terimi alarak başlık veya yazara göre kitap arar."""
    query = input("\nArama terimi girin (başlık veya yazar): ").strip()
    if query:
        library.search_books(query) 
    else:
        print("Geçersiz arama terimi!")

def show_statistics(library: Library):
    """Kütüphane istatistiklerini gösterir."""
    count = library.get_book_count()
    print(f"\n KÜTÜPHANE İSTATİSTİKLERİ")
    print("-" * 30)
    print(f"Toplam Kitap Sayısı: {count}")

    if count > 0:
        authors = library.get_author_statistics()
        print(f"Farklı Yazar Sayısı: {len(authors)}")
        print("\nEn Çok Kitabı Olan Yazarlar:")
        # Yazar istatistiklerini azalan sıraya göre sırala ve ilk 3'ü göster
        sorted_authors = sorted(authors.items(), key=lambda x: x[1], reverse=True)[:3]
        for i, (author, book_count) in enumerate(sorted_authors, 1):
            print(f"  {i}. {author}: {book_count} kitap")
    else:
        print("İstatistikleri gösterebilmek için kütüphanede kitap bulunmamaktadır.")

    print("-" * 30)

async def main():
    """Ana uygulama döngüsü."""
    library = Library() # Varsayılan olarak 'library.json' kullanır

    while True:
        try:
            display_menu()
            choice = input("Seçiminizi yapın (1-8): ").strip() 
            if choice == '1':
                await add_book_from_api_menu(library) 
            elif choice == '2':
                add_book_manual_menu(library)        
            elif choice == '3':
                remove_book_menu(library)
            elif choice == '4': 
                library.list_books()
            elif choice == '5': 
                search_book_isbn_menu(library)
            elif choice == '6': 
                search_book_text_menu(library)
            elif choice == '7': 
                show_statistics(library)
            elif choice == '8': 
                print("Çıkış yapılıyor...")
                break
            else:
                print("Geçersiz seçim. Lütfen 1-8 arasında bir değer girin.")
        except Exception as e:
            print(f"Beklenmeyen bir hata oluştu: {e}")

if __name__ == "__main__":
    # main fonksiyonunu eşzamansız olarak çalıştırır
    asyncio.run(main())

