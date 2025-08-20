from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import asyncio # Library.add_book metodu async olduğu için gerekli

# classes.py dosyasından Library ve Book sınıflarını içe aktarıyoruz.
# Bu, kütüphane mantığını API katmanında yeniden kullanmamızı sağlar.
from classes import Library, Book

# FastAPI uygulamasını başlatır. Meta verileri (başlık, açıklama, sürüm) ayarlanır.
app = FastAPI(
    title="Kütüphane Yönetim API'si",
    description="Kitap ekleme, listeleme, silme ve arama işlemleri için RESTful API.",
    version="1.0.0"
)

# Library sınıfının bir örneğini oluştururuz.
# Bu örnek, API'nin arka planda kitapları yönetmek için kullanacağı kütüphane nesnesidir.
# 'library.json' dosyasını kullanarak kitap verilerini kalıcı hale getirir.
library = Library()

# Pydantic modeli: API'den alınacak ISBN verisini tanımlar.
# Bu model, POST /books isteği için giriş verisinin yapısını doğrular.
class ISBNInput(BaseModel):
    """
    POST /books isteği için ISBN giriş modeli.
    isbn: Eklenecek kitabın ISBN numarası (ör: "978-0321765723").
    """
    isbn: str

# Pydantic modeli: API'nin döndüreceği Book verisini tanımlar.
# Bu model, Book nesnelerinin JSON'a nasıl dönüştürüleceğini tanımlar.
class BookOutput(BaseModel):
    """
    API yanıtlarında kullanılacak kitap modeli.
    """
    title: str
    author: str
    isbn: str

    class Config:
        # FastAPI'nin Book sınıfının Pydantic modeli olarak kabul edilmesini sağlar.
        # Bu sayede Book nesneleri doğrudan döndürülebilir ve JSON'a dönüştürülebilir.
        from_attributes = True

# GET /books endpoint'i
@app.get("/books", response_model=List[BookOutput], summary="Tüm kitapları listele")
async def get_all_books():
    """
    Kütüphanedeki tüm kitapların listesini JSON formatında döndürür.
    """
    # Library sınıfındaki 'books' özelliğini kullanarak tüm kitapları alır.
    return library.books

# POST /books endpoint'i
@app.post("/books", response_model=BookOutput, status_code=201, summary="Yeni kitap ekle")
async def add_new_book(isbn_input: ISBNInput):  # Endpoint adı add_new_book olarak düzeltildi
    """
    Yeni bir kitabı kütüphaneye ekler.
    Open Library API'den ISBN numarasına göre kitap bilgilerini çeker (Aşama 2 mantığı).
    """
    try:
        new_book = await library.add_book_from_api(isbn_input.isbn.strip())
    except Exception as e:
        # Ağ hatası, API hatası gibi beklenmedik durumlarda
        raise HTTPException(
            status_code=400,
            detail=f"Kitap eklenemedi veya ISBN '{isbn_input.isbn}' ile kitap bulunamadı. Hata: {str(e)}"
        )

    if new_book is None:
        # API kitap bulamadıysa veya duplicate ISBN varsa
        raise HTTPException(
            status_code=400,
            detail=f"Kitap eklenemedi veya ISBN '{isbn_input.isbn}' ile kitap bulunamadı."
        )

    return new_book.to_dict()

# DELETE /books/{isbn} endpoint'i
@app.delete("/books/{isbn}", status_code=204, summary="Kitap sil")
async def remove_book(isbn: str):
    """
    Belirtilen ISBN numarasına sahip kitabı kütüphaneden siler.
    
    Args:
        isbn (str): Silinecek kitabın ISBN numarası.
    
    Raises:
        HTTPException: Belirtilen ISBN ile kitap bulunamazsa (404 Not Found).
    """
    # Library sınıfındaki 'remove_book' metodunu çağırırız.
    # Bu metod silme işleminin başarılı olup olmadığını kontrol eder.
    if not library.remove_book(isbn.strip()):
        # Eğer kitap bulunamazsa 'remove_book' False döndürür.
        raise HTTPException(status_code=404, detail=f"ISBN '{isbn}' numaralı kitap kütüphanede bulunamadı.")
    
    return

