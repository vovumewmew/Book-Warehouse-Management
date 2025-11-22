import flet as ft
from .add_button_base import AddButtonBase
from source.ui.form.add_form.add_employee_form import AddEmployeeForm
from source.models.NhanVien import NhanVien

class AddNewEmployee(AddButtonBase):
    def __init__(self, page):
        super().__init__(
            text = "Thêm", 
            icon=ft.Icons.PERSON_ADD_ROUNDED,
            width=90,
            height=48,
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
        if current_page and hasattr(current_page, 'reload_employees'):
            reload_callback = current_page.reload_employees

        form = AddEmployeeForm(
            on_success=reload_callback
        )
        form.open_form(self.page)
