import flet as ft
from source.ui.form.add_form.add_book_form import AddBookForm
from source.models.Sach import Sach
from .add_button_base import AddButtonBase

class AddNewBook(AddButtonBase):
    """Nút Thêm sách mới"""

    def __init__(self, page):
        super().__init__(
            text="Thêm",
            icon=ft.Icons.BOOKMARK_ADD_ROUNDED,
            width=90,
            height=48,
            page=page,
            on_click=self.open_add_form
        )
        self.page = page

    def open_add_form(self, e):
        # Tìm trang hiện tại để lấy hàm reload
        main_frame = self.page.get_control("main_frame")
        current_page = main_frame.content if main_frame else None
        
        # Hàm reload sẽ được truyền vào on_success
        reload_callback = None
        if current_page and hasattr(current_page, 'reload_books'):
            reload_callback = current_page.reload_books

        form = AddBookForm(
            on_success=reload_callback # Truyền hàm reload vào form
        )
        form.page = self.page
        form.open_form(self.page)
