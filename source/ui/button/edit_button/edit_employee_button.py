import flet as ft
from .edit_button_base import EditButtonBase
from source.ui.form.edit_form.edit_employee_form import EditEmployeeForm


class EditEmployeeButton(EditButtonBase):
    def __init__(self, nhanvien, nhanvien_service, page: ft.Page):
        """
        nhanvien: đối tượng NhanVien cần sửa
        nhanvien_service: service có method update(...)
        page: ft.Page hiện tại (để đặt page.dialog / snack_bar)
        reload_callback: hàm reload danh sách sau khi cập nhật
        """
        super().__init__(text="Sửa", on_edit=self._open_edit_form)
        self.nhanvien = nhanvien
        self.nhanvien_service = nhanvien_service
        self.page = page

    # ======================================================
    def _open_edit_form(self, e):
        if not (self.nhanvien and self.nhanvien_service and self.page):
            print("Thiếu nhân viên / service / page để mở form chỉnh sửa")
            return

        # --- Callback khi sửa thành công ---
        def on_success(updated_nv):
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"✅ Đã cập nhật nhân viên '{updated_nv.HoTen}'"),
                bgcolor="#4CAF50",
                duration=2500
            )
            self.page.snack_bar.open = True
            self.page.update()

            # Đóng dialog sau khi thành công
            if hasattr(self.page, "dialog") and self.page.dialog:
                try:
                    self.page.dialog.open = False
                except:
                    pass
                self.page.update()

        # --- Callback khi đóng form mà không lưu ---
        def on_close(ev=None):
            if hasattr(self.page, "dialog") and self.page.dialog:
                try:
                    self.page.dialog.open = False
                except:
                    pass
                self.page.update()

        # --- Mở form sửa ---
        form = EditEmployeeForm(
            nhanvien=self.nhanvien,
            nhanvien_service=self.nhanvien_service,
            on_success=on_success,
            on_close=on_close
        )
        form.open_form(self.page)
