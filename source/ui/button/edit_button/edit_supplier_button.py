import flet as ft
from .edit_button_base import EditButtonBase
from source.ui.form.edit_form.edit_supplier_form import EditSupplierForm

class EditSupplierButton(EditButtonBase):
    def __init__(self, supplier, supplier_service, page: ft.Page):
        """
        supplier: đối tượng NguonNhapSach cần sửa
        supplier_service: NguonNhapSachService có method update(...)
        page: ft.Page hiện tại (để đặt page.dialog / snack_bar)
        """
        super().__init__(text="Sửa", on_edit=self._open_edit_form)
        self.supplier = supplier
        self.supplier_service = supplier_service
        self.page = page

    def _open_edit_form(self, e):
        if not (self.supplier and self.supplier_service and self.page):
            print("Thiếu supplier / service / page để mở form chỉnh sửa")
            return

        def on_success(updated_supplier):
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Đã cập nhật nhà cung cấp '{updated_supplier.TenCoSo}'"),
                bgcolor="#4CAF50",
                duration=2500
            )
            self.page.snack_bar.open = True
            self.page.update()

            # Đóng dialog nếu đang mở
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

        # Khởi tạo EditSupplierForm
        form = EditSupplierForm(
            supplier=self.supplier,
            supplier_service=self.supplier_service,
            on_success=on_success,
            on_close=on_close
        )
        form.open_form(self.page)
