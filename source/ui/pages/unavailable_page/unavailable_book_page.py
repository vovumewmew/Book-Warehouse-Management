import flet as ft
from typing import Callable
from config.db_connection import DatabaseConnection
from source.dao.SachDAO import SachDAO
from source.ui.pages.base_page import BasePage
from source.ui.Table.books_table import BookTable

class UnavailableBooksPage(BasePage):
    def __init__(self, page: ft.Page, change_page_func, **kwargs):
        """
        Khởi tạo trang sách không khả dụng.
        :param page: Đối tượng ft.Page
        :param change_page_func: Hàm để yêu cầu thay đổi trang
        """
        self.page = page
        self.change_page = change_page_func

        # --- Container chứa bảng sách ---
        self.books_container = ft.Column(spacing=10, expand=True, scroll=ft.ScrollMode.AUTO)
        self.content_body = self.build_content()

        # --- Nút quay lại ---
        back_button = ft.IconButton(
            icon=ft.Icons.ARROW_BACK_ROUNDED,
            icon_color=ft.Colors.WHITE,
            bgcolor="#A94F8B",
            width=40,
            height=40,
            tooltip="Quay lại",
            on_click=self.go_back,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        )

        # --- Nút làm mới ---
        refresh_button = ft.IconButton(
            icon=ft.Icons.REFRESH,
            icon_color=ft.Colors.WHITE,
            bgcolor="#A94F8B",
            width=40,
            height=40,
            tooltip="Làm mới",
            on_click=self.reload_books,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        )

        # --- Khởi tạo BasePage với tiêu đề và các nút hành động ---
        super().__init__(
            "Sách đã xóa",
            header_action=ft.Row([back_button, refresh_button], spacing=10)
        )

    def build_content(self):
        """Xây dựng nội dung chính của trang, tải dữ liệu sách không khả dụng."""
        db = DatabaseConnection()
        conn = db.connect()
        if not conn:
            return ft.Text("Không thể kết nối cơ sở dữ liệu", color="red")

        # Sử dụng hàm get_unavailable để lấy sách đã xóa
        books = SachDAO(db).get_unavailable()
        db.disconnect()

        self.books_container.controls.clear()
        self.books_container.controls.append(BookTable(books, page=self.page, columns=3, mode="unavailable"))

        return self.books_container

    def go_back(self, e):
        """Yêu cầu MainFrame quay lại trang sách chính."""
        from source.ui.pages.available_page.books_page import BooksPage
        self.change_page(BooksPage)

    def reload_books(self, e=None):
        """Tải lại danh sách sách không khả dụng."""
        self.build_content()
        page_to_update = self.page if not e else e.control.page
        if page_to_update:
            page_to_update.update()
