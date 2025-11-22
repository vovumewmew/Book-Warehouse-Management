import flet as ft
from source.ui.button.edit_button.edit_button_base import EditButtonBase
from source.ui.form.edit_form.edit_export_receipt_form import EditExportReceiptForm

class EditExportReceiptButton(EditButtonBase):
    def __init__(self, page: ft.Page, receipt, on_edit_callback=None):
        super().__init__(on_edit=self.open_edit_form)
        self.page = page
        self.receipt = receipt
        self.on_edit_callback = on_edit_callback

    def open_edit_form(self, e):
        """Mở form để sửa phiếu xuất."""
        def on_form_close():
            # Gọi callback để tải lại dữ liệu sau khi sửa
            if self.on_edit_callback:
                self.on_edit_callback()

        edit_form = EditExportReceiptForm(
            page=self.page,
            receipt_data=self.receipt, # Truyền dữ liệu phiếu cần sửa
            on_close=on_form_close
        )
        
        # Thêm form sửa vào overlay của trang
        self.page.overlay.append(edit_form)
        self.page.update()