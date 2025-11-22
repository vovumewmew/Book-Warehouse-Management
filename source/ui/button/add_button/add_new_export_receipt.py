import flet as ft
from source.ui.form.add_form.add_export_receipt_form import AddExportReceiptForm

class AddNewExportReceipt(ft.ElevatedButton):
    def __init__(self, page: ft.Page, on_add_callback=None):
        super().__init__()
        self.page = page
        self.on_add_callback = on_add_callback

        self.text = "Thêm Phiếu Xuất"
        self.bgcolor = "#A94F8B"
        self.color = ft.Colors.WHITE
        self.icon = ft.Icons.ADD_ROUNDED
        self.style = ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
        self.on_click = self.open_add_form

    def open_add_form(self, e):
        """Mở form để thêm phiếu xuất mới."""
        def on_form_close():
            if self.on_add_callback:
                self.on_add_callback()

        add_form = AddExportReceiptForm(
            page=self.page,
            on_close=on_form_close
        )
        self.page.overlay.append(add_form)
        self.page.update()