# source/ui/button/edit_button/edit_book_button.py
import flet as ft
from .edit_button_base import EditButtonBase
from source.ui.form.edit_form.edit_book_form import EditBookForm

class EditBookButton(EditButtonBase):
    def __init__(self, book, sach_service, page: ft.Page):
        """
        book: đối tượng Sach cần sửa
        sach_service: service (SachService) có method update(...)
        page: ft.Page hiện tại (để đặt page.dialog / snack_bar)
        reload_callback: hàm để reload danh sách / giao diện sau khi cập nhật
        """
        # tạo nút base với callback là method _open_edit_form
        super().__init__(text="Sửa", on_edit=self._open_edit_form)
        self.book = book
        self.sach_service = sach_service
        self.page = page

    def _open_edit_form(self, e):
        if not (self.book and self.sach_service and self.page):
            print("Thiếu book / service / page để mở form chỉnh sửa")
            return

        def on_success(updated_book):
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Đã cập nhật sách '{updated_book.TenSach}'"),
                bgcolor="#4CAF50",
                duration=2500
            )
            self.page.snack_bar.open = True
            self.page.update()

            if hasattr(self.page, "dialog") and self.page.dialog:
                try:
                    self.page.dialog.open = False
                except:
                    pass
                self.page.update() 

        def on_close(ev=None):
            if hasattr(self.page, "dialog") and self.page.dialog:
                try:
                    self.page.dialog.open = False
                except:
                    pass
                self.page.update()

        # Khởi tạo EditBookForm đúng cách
        form = EditBookForm(
            self.book,                 # trực tiếp đối tượng Sach
            sach_service=self.sach_service,
            on_success=on_success,
            on_close=on_close
        )
        form.open_form(self.page)
