# source/ui/button/edit_button/edit_button_base.py
import flet as ft

class EditButtonBase(ft.ElevatedButton):
    def __init__(self, text: str = "Sửa", on_edit=None):
        """
        on_edit: callable nhận event e -> on_edit(e)
        Đây là nút base generic — KHÔNG import form cụ thể ở đây.
        """
        super().__init__(
            text,
            bgcolor="#A94F8B",
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=30)),
            on_click=self._handle_click
        )
        self.on_edit = on_edit

    def _handle_click(self, e):
        if callable(self.on_edit):
            # chuyển tiếp event cho callback được cung cấp
            self.on_edit(e)
