import pytest
import json
import os
import asyncio
from unittest import mock
from unittest.mock import patch, mock_open, AsyncMock
import httpx
from classes import Book, Library

class TestBook:
    """Book sınıfı için test sınıfı."""
    
    def test_book_init(self):
        """Book nesnesi oluşturma testi."""
        book = Book("1984", "George Orwell", "978-0451524935")
        assert book.title == "1984"
        assert book.author == "George Orwell"
        assert book.isbn == "978-0451524935"
    
    def test_book_str(self):
        """Book __str__ metodu testi."""
        book = Book("1984", "George Orwell", "978-0451524935")
        expected = "1984 by George Orwell (ISBN: 978-0451524935)"
        assert str(book) == expected
    
    def test_book_to_dict(self):
        """Book to_dict metodu testi."""
        book = Book("1984", "George Orwell", "978-0451524935")
        expected = {
            "title": "1984",
            "author": "George Orwell", 
            "isbn": "978-0451524935"
        }
        assert book.to_dict() == expected
    
    def test_book_from_dict(self):
        """Book from_dict metodu testi."""
        data = {
            "title": "1984",
            "author": "George Orwell",
            "isbn": "978-0451524935"
        }
        book = Book.from_dict(data)
        assert book.title == "1984"
        assert book.author == "George Orwell"
        assert book.isbn == "978-0451524935"

class TestLibrary:
    """Library sınıfı için test sınıfı."""
    
    @pytest.fixture
    def temp_library(self):
        """Her test için geçici bir Library nesnesi oluşturur."""
        test_file = "test_library.json"
        library = Library(test_file)
        yield library
        if os.path.exists(test_file):
            os.remove(test_file)
    
    def test_library_init(self, temp_library):
        """Library nesnesi oluşturma testi."""
        assert temp_library.data_file == "test_library.json"
        assert isinstance(temp_library.books, list)
    
    def test_add_book_manual_success(self, temp_library):
        """Manuel kitap ekleme başarı testi."""
        book = Book("Test Kitap", "Test Yazar", "123456789")
        result = temp_library.add_book_manual(book)
        assert result == True
        assert len(temp_library.books) == 1
        assert temp_library.books[0].title == "Test Kitap"
    
    def test_add_book_manual_duplicate_isbn(self, temp_library):
        """Aynı ISBN ile kitap ekleme testi."""
        book1 = Book("Kitap 1", "Yazar 1", "123456789")
        book2 = Book("Kitap 2", "Yazar 2", "123456789")
        
        temp_library.add_book_manual(book1)
        result = temp_library.add_book_manual(book2)
        
        assert result == False
        assert len(temp_library.books) == 1
    
    def test_add_book_manual_empty_fields(self, temp_library):
        """Boş alan ile kitap ekleme testi."""
        book = Book("", "Test Yazar", "123456789")
        result = temp_library.add_book_manual(book)
        assert result == False
        assert len(temp_library.books) == 0
    
    def test_remove_book_success(self, temp_library):
        """Kitap silme başarı testi."""
        book = Book("Test Kitap", "Test Yazar", "123456789")
        temp_library.add_book_manual(book)
        
        result = temp_library.remove_book("123456789")
        assert result == True
        assert len(temp_library.books) == 0
    
    def test_remove_book_not_found(self, temp_library):
        """Olmayan kitap silme testi."""
        result = temp_library.remove_book("nonexistent")
        assert result == False
    
    def test_find_book_success(self, temp_library):
        """Kitap bulma başarı testi."""
        book = Book("Test Kitap", "Test Yazar", "123456789")
        temp_library.add_book_manual(book)
        
        found_book = temp_library.find_book("123456789")
        assert found_book is not None
        assert found_book.title == "Test Kitap"
    
    def test_find_book_not_found(self, temp_library):
        """Olmayan kitap bulma testi."""
        found_book = temp_library.find_book("nonexistent")
        assert found_book is None
    
    def test_search_books_by_title(self, temp_library):
        """Başlığa göre kitap arama testi."""
        book1 = Book("Python Programlama", "Yazar 1", "111")
        book2 = Book("Java Programlama", "Yazar 2", "222")
        book3 = Book("Web Tasarımı", "Yazar 3", "333")
        
        temp_library.add_book_manual(book1)
        temp_library.add_book_manual(book2)
        temp_library.add_book_manual(book3)
        
        results = temp_library.search_books("programlama")
        assert len(results) == 2
        assert any(book.title == "Python Programlama" for book in results)
        assert any(book.title == "Java Programlama" for book in results)
    
    def test_search_books_by_author(self, temp_library):
        """Yazara göre kitap arama testi."""
        book1 = Book("Kitap 1", "George Orwell", "111")
        book2 = Book("Kitap 2", "J.K. Rowling", "222")
        
        temp_library.add_book_manual(book1)
        temp_library.add_book_manual(book2)
        
        results = temp_library.search_books("orwell")
        assert len(results) == 1
        assert results[0].author == "George Orwell"
    
    def test_get_book_count(self, temp_library):
        """Kitap sayısı testi."""
        assert temp_library.get_book_count() == 0
        
        book = Book("Test Kitap", "Test Yazar", "123")
        temp_library.add_book_manual(book)
        assert temp_library.get_book_count() == 1
    
    def test_get_author_statistics(self, temp_library):
        """Yazar istatistikleri testi."""
        book1 = Book("Kitap 1", "George Orwell", "111")
        book2 = Book("Kitap 2", "George Orwell", "222")
        book3 = Book("Kitap 3", "J.K. Rowling", "333")
        
        temp_library.add_book_manual(book1)
        temp_library.add_book_manual(book2)
        temp_library.add_book_manual(book3)
        
        stats = temp_library.get_author_statistics()
        assert stats["George Orwell"] == 2
        assert stats["J.K. Rowling"] == 1
    
    def test_clear_library(self, temp_library):
        """Kütüphane temizleme testi."""
        book = Book("Test Kitap", "Test Yazar", "123")
        temp_library.add_book_manual(book)
        
        result = temp_library.clear_library()
        assert result == True
        assert len(temp_library.books) == 0
    
    @patch("builtins.open", mock_open(read_data='[{"title": "Test", "author": "Author", "isbn": "123"}]'))
    def test_load_books_success(self):
        """Kitap yükleme başarı testi."""
        with patch("os.path.exists", return_value=True):
            library = Library("test.json")
            assert len(library.books) == 1
            assert library.books[0].title == "Test"
    
    @patch("builtins.open", mock_open(read_data='invalid json'))
    def test_load_books_json_error(self):
        """Bozuk JSON ile kitap yükleme testi."""
        with patch("os.path.exists", return_value=True):
            library = Library("test.json")
            assert len(library.books) == 0
    
    def test_load_books_file_not_exists(self):
        """Dosya yokken kitap yükleme testi."""
        with patch("os.path.exists", return_value=False):
            library = Library("nonexistent.json")
            assert len(library.books) == 0

class TestLibraryAPI:
    """Library sınıfının API metodları için test sınıfı."""
    
    @pytest.fixture
    def temp_library(self):
        """Her test için geçici bir Library nesnesi oluşturur."""
        test_file = "test_api_library.json"
        library = Library(test_file)
        yield library
        if os.path.exists(test_file):
            os.remove(test_file)
    
    @pytest.mark.asyncio
    async def test_add_book_from_api_success(self, temp_library):
        """API'den kitap ekleme başarı testi."""
        main_response_data = {
            "title": "Test Book",
            "authors": [{"name": "Test Author"}]
        }
        
        mock_httpx_client_instance = AsyncMock()
        mock_httpx_client_instance.__aenter__.return_value = mock_httpx_client_instance
        mock_httpx_client_instance.__aexit__.return_value = AsyncMock()

        with patch("classes.httpx.AsyncClient", return_value=mock_httpx_client_instance):
            mock_response_get = mock.Mock()
            mock_response_get.is_success = True
            mock_response_get.json.return_value = main_response_data
            mock_httpx_client_instance.get.return_value = mock_response_get
            
            result = await temp_library.add_book_from_api("9780123456789")
            
            assert result is not None
            assert result.title == "Test Book"
            assert result.author == "Test Author"
            assert result.isbn == "9780123456789"
            assert len(temp_library.books) == 1
    
    @pytest.mark.asyncio
    async def test_add_book_from_api_with_author_key(self, temp_library):
        """API'den yazar detayı çekerek kitap ekleme testi."""
        main_response_data = {
            "title": "Test Book",
            "authors": [{"key": "/authors/OL123A"}]
        }
        
        author_response_data = {
            "name": "Detailed Author Name"
        }
        
        mock_httpx_client_instance = AsyncMock()
        mock_httpx_client_instance.__aenter__.return_value = mock_httpx_client_instance
        mock_httpx_client_instance.__aexit__.return_value = AsyncMock()

        with patch("classes.httpx.AsyncClient", return_value=mock_httpx_client_instance):
            main_response_get = mock.Mock()
            main_response_get.is_success = True
            main_response_get.json.return_value = main_response_data
            
            author_response_get = mock.Mock()
            author_response_get.is_success = True
            author_response_get.json.return_value = author_response_data
            
            mock_httpx_client_instance.get.side_effect = [main_response_get, author_response_get]
            
            result = await temp_library.add_book_from_api("9780123456789")
            
            assert result is not None
            assert result.title == "Test Book"
            assert result.author == "Detailed Author Name"
    
    @pytest.mark.asyncio
    async def test_add_book_from_api_not_found(self, temp_library):
        """API'de kitap bulunamama testi."""
        mock_httpx_client_instance = AsyncMock()
        mock_httpx_client_instance.__aenter__.return_value = mock_httpx_client_instance
        mock_httpx_client_instance.__aexit__.return_value = AsyncMock()

        with patch("classes.httpx.AsyncClient", return_value=mock_httpx_client_instance):
            mock_response_get = mock.Mock()
            mock_response_get.is_success = False
            mock_response_get.status_code = 404
            mock_httpx_client_instance.get.return_value = mock_response_get
            
            result = await temp_library.add_book_from_api("nonexistent")
            
            assert result is None
            assert len(temp_library.books) == 0
    
    @pytest.mark.asyncio
    async def test_add_book_from_api_network_error(self, temp_library):
        """API ağ hatası testi."""
        mock_httpx_client_instance = AsyncMock()
        mock_httpx_client_instance.__aenter__.return_value = mock_httpx_client_instance
        mock_httpx_client_instance.__aexit__.return_value = AsyncMock()

        with patch("classes.httpx.AsyncClient", return_value=mock_httpx_client_instance):
            mock_httpx_client_instance.get.side_effect = httpx.RequestError("Network error")
            
            result = await temp_library.add_book_from_api("9780123456789")
            
            assert result is None
            assert len(temp_library.books) == 0
    
    @pytest.mark.asyncio
    async def test_add_book_from_api_empty_isbn(self, temp_library):
        """Boş ISBN ile API'den kitap ekleme testi."""
        result = await temp_library.add_book_from_api("")
        assert result is None
        assert len(temp_library.books) == 0
    
    @pytest.mark.asyncio
    async def test_add_book_from_api_duplicate_isbn(self, temp_library):
        """Aynı ISBN ile API'den kitap ekleme testi."""
        book = Book("Existing Book", "Existing Author", "9780123456789")
        temp_library.add_book_manual(book)
        
        result = await temp_library.add_book_from_api("9780123456789")
        assert result is None
        assert len(temp_library.books) == 1

if __name__ == "__main__":
    pytest.main([__file__])
