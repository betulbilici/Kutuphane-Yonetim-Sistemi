import pytest
import os
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import httpx

from api import app, library
from classes import Book

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def setup_test_library():
    test_file = "test_api_library.json"
    test_books = [
        {"title": "1984", "author": "George Orwell", "isbn": "978-0451524935"},
        {"title": "Python Programming", "author": "John Doe", "isbn": "978-1234567890"}
    ]
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(test_books, f, indent=4, ensure_ascii=False)
    original_data_file = library.data_file
    original_books = library._books.copy()
    library.data_file = test_file
    library.load_books()
    yield library
    if os.path.exists(test_file):
        os.remove(test_file)
    library.data_file = original_data_file
    library._books = original_books

@pytest.fixture
def empty_library():
    test_file = "test_empty_library.json"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("[]")
    original_data_file = library.data_file
    original_books = library._books.copy()
    library.data_file = test_file
    library.load_books()
    yield library
    if os.path.exists(test_file):
        os.remove(test_file)
    library.data_file = original_data_file
    library._books = original_books

class TestGetBooks:
    def test_get_books_empty(self, client, empty_library):
        response = client.get("/books")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_books_with_data(self, client, setup_test_library):
        response = client.get("/books")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] == "1984"

class TestPostBooks:
    @pytest.mark.asyncio
    async def test_add_book_success(self, client, empty_library):
        with patch.object(library, 'add_book_from_api', new_callable=AsyncMock) as mock_add_book_from_api:
            expected_book = Book("Mocked Test Book", "Mocked Author", "9780123456789")
            mock_add_book_from_api.return_value = expected_book
            response = client.post("/books", json={"isbn": "9780123456789"})
            assert response.status_code == 201
            data = response.json()
            assert data["title"] == expected_book.title

    @pytest.mark.asyncio
    async def test_add_book_network_error(self, client, empty_library):
        with patch.object(library, 'add_book_from_api', new_callable=AsyncMock) as mock_add_book_from_api:
            mock_add_book_from_api.side_effect = Exception("Simulated network error")
            response = client.post("/books", json={"isbn": "9780123456789"})
            assert response.status_code == 400
            assert "9780123456789" in response.json()["detail"]

class TestAPIIntegration:
    @pytest.mark.asyncio
    async def test_full_crud_cycle(self, client, empty_library):
        response = client.get("/books")
        assert response.status_code == 200
        assert len(response.json()) == 0

        with patch.object(library, 'add_book_from_api', new_callable=AsyncMock) as mock_add_book_from_api:
            def mock_add_book_side_effect(isbn):
                book = Book("Integration Test Book", "Test Author", isbn)
                library._books.append(book)
                return book
            mock_add_book_from_api.side_effect = mock_add_book_side_effect
            response = client.post("/books", json={"isbn": "9780123456789"})
            assert response.status_code == 201

        response = client.get("/books")
        assert response.status_code == 200
        books = response.json()
        assert len(books) == 1
        assert books[0]["isbn"] == "9780123456789"

        response = client.delete("/books/9780123456789")
        assert response.status_code == 204

        response = client.get("/books")
        assert response.status_code == 200
        assert len(response.json()) == 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
