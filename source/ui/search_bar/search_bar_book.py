# source/ui/search/search_bar_book.py
import flet as ft
from .search_bar_base import SearchBarBase
from source.ui.Table.books_table import BookTable
from source.dao.SachDAO import SachDAO
from config.db_connection import DatabaseConnection

class SearchBarBook(SearchBarBase):
    def __init__(self, page: ft.Page, books_container: ft.Column, width=300):
        super().__init__(placeholder="Tìm sách...", width=width, on_search=self.search_books)
        self.page = page
        self.books_container = books_container
        self.books_cache = []  # cache dữ liệu 

        # Lần đầu load dữ liệu
        self.load_books_from_db()

    def load_books_from_db(self):
        db = DatabaseConnection()
        self.books_cache = SachDAO(db).get_all()
        db.disconnect()

    def search_books(self, query: str):
        books = self.books_cache  # filter từ cache
        if query:
            q = query.lower()
            books = [
                b for b in books
                if q in b.TenSach.lower()
                or q in b.TacGia.lower()
                or q in b.TheLoai.lower()
                or q in b.ID_Sach.lower()
            ]
        self.books_container.controls.clear()
        self.books_container.controls.append(BookTable(books, page=self.page, columns=3))
        self.page.update()
