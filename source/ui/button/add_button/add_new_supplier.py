import flet as ft
from .add_button_base import AddButtonBase
from source.models.NguonNhapSach import NguonNhapSach
from source.ui.form.add_form.add_supplier_form import AddSupplierForm

class AddNewSupplier(AddButtonBase):
    def __init__(self, page):
        super().__init__(
            text = "Thêm",
            width=90,
            height=48,
            icon = ft.Icons.ADD_BUSINESS_ROUNDED,
            page=page,
            on_click=self.open_add_form,
        ) 
        self.page = page

    def open_add_form(self, e):
        # Tìm trang hiện tại để lấy hàm reload
        main_frame = self.page.get_control("main_frame")
        current_page = main_frame.content if main_frame else None
        
        # Hàm reload sẽ được truyền vào on_success
        reload_callback = None
        if current_page and hasattr(current_page, 'reload_suppliers'):
            reload_callback = current_page.reload_suppliers

        form = AddSupplierForm(
            on_success=reload_callback
        )
        form.open_form(self.page)