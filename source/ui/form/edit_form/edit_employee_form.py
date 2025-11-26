import flet as ft
from decimal import Decimal
from .edit_form_base import EditFormBase
from source.models.NhanVien import NhanVien
from source.services.NhanVienService import NhanVienService
from util.dialog_utils import show_success_dialog, show_error_dialog
from util.get_absolute_path import get_absolute_path


class EditEmployeeForm(EditFormBase):
    def __init__(self, nhanvien: NhanVien, nhanvien_service: NhanVienService, on_close=None, on_success=None):
        super().__init__(title="Sửa thông tin nhân viên", on_submit=self.submit_form, on_close=on_close)
        self.nhanvien_service = nhanvien_service
        self.on_success = on_success
        self._nhanvien = nhanvien

        self._nhanvien = nhanvien

        # --- Hiển thị ảnh hiện tại ---
        # --- Gán ảnh thật của nhân viên vào image_preview có sẵn từ EditFormBase ---
        self.image_file = nhanvien.HinhAnh or get_absolute_path(
            "source/ui/picture/employee_pic/default_employee_pic.jpg"
        )

        # Gán lại nội dung của image_preview (đã có sẵn trong EditFormBase)
        self.image_preview.content = ft.Image(
            src=self.image_file,
            width=120,
            height=120,
            fit=ft.ImageFit.COVER,
            border_radius=ft.border_radius.all(10),
        )

        # --- Các trường nhập liệu ---
        self.id_nhan_vien_field = self.add_field("Mã nhân viên", value=nhanvien.ID_NhanVien, read_only=True)
        self.ten_nhan_vien_field = self.add_field("Tên nhân viên", value=nhanvien.HoTen)
        self.so_dien_thoai_field = self.add_field("Số điện thoại", value=nhanvien.SoDienThoai)
        self.email_field = self.add_field("Email", value=nhanvien.Email)

        # --- Dropdown Giới tính ---
        self.gioi_tinh_field = ft.Dropdown(
            label="Giới tính",
            options=[
                ft.dropdown.Option("Nam"),
                ft.dropdown.Option("Nữ"),
            ],
            value=nhanvien.GioiTinh,
            width=450,
            border_color=self.default_border_color,
            focused_border_color=self.default_focused_border_color,
            bgcolor=self.default_field_bgcolor,
            color=self.default_field_color,
            border_radius=12,
        )

        # --- Dropdown Chức vụ ---
        roles = self.nhanvien_service.get_all_roles()
        if not roles:
            roles = [
                "Quản lý kho sách",
                "Nhân viên nhập sách",
                "Nhân viên xuất sách",
                "Nhân viên kiểm kê kho",
            ]
        self.chuc_vu_field = ft.Dropdown(
            label="Chức vụ",
            options=[ft.dropdown.Option(role) for role in roles],
            value=nhanvien.ChucVu,
            width=450,
            border_color=self.default_border_color,
            focused_border_color=self.default_focused_border_color,
            bgcolor=self.default_field_bgcolor,
            color=self.default_field_color,
            border_radius=12,
        )

        # Sắp xếp lại thứ tự hiển thị
        if self.so_dien_thoai_field in self.fields_column.controls:
            self.fields_column.controls.remove(self.so_dien_thoai_field)
        if self.email_field in self.fields_column.controls:
            self.fields_column.controls.remove(self.email_field)

        self.fields_column.controls.extend([
            self.gioi_tinh_field,
            self.chuc_vu_field,
            self.so_dien_thoai_field,
            self.email_field,
        ])

        # --- Clear lỗi khi focus ---
        for field in [
            self.ten_nhan_vien_field,
            self.gioi_tinh_field,
            self.chuc_vu_field,
            self.so_dien_thoai_field,
            self.email_field,
        ]:
            field.on_focus = self.make_clear_error_callback(field)

    # Xóa lỗi khi focus
    def make_clear_error_callback(self, field):
        def callback(e):
            field.error_text = None
            field.update()
        return callback

    # Hiển thị lỗi lên textfield hoặc console
    def _show_error(self, message: str, field: ft.TextField = None):
        if field:
            field.error_text = message
            field.update()
        else:
            print(f"⚠️ {message}")

    # Xử lý khi nhấn nút "Lưu"
    def submit_form(self, e, data=None):
        try:
            data = {
                "ID_NhanVien": self._nhanvien.ID_NhanVien,
                "HoTen": self.ten_nhan_vien_field.value.strip(),
                "GioiTinh": self.gioi_tinh_field.value,
                "ChucVu": self.chuc_vu_field.value,
                "SoDienThoai": self.so_dien_thoai_field.value.strip(),
                "Email": self.email_field.value.strip(),
            }

            updated_nv = NhanVien(
                ID_NhanVien=data["ID_NhanVien"],
                HoTen=data["HoTen"],
                GioiTinh=data["GioiTinh"],
                ChucVu=data["ChucVu"],
                SoDienThoai=data["SoDienThoai"],
                Email=data["Email"],
                TrangThaiNhanVien="Đang làm việc",
                HinhAnh=self.image_file or get_absolute_path(
                    "source/ui/picture/employee_pic/default_employee_pic.jpg"
                ),
            )

            result = self.nhanvien_service.update(updated_nv)
            if result:
                show_success_dialog(
                    self.page, "Thành công", f"Đã cập nhật nhân viên '{updated_nv.HoTen}' thành công!",
                    on_close=self.close
                )
            else:
                show_error_dialog(self.page, "Lỗi", "Không thể cập nhật thông tin nhân viên. Kiểm tra dữ liệu hoặc DB")

        except ValueError as ve:
            msg = str(ve)
            field = None
            if "Tên nhân viên" in msg: field = self.ten_nhan_vien_field
            elif "Giới tính" in msg: field = self.gioi_tinh_field
            elif "Chức vụ" in msg: field = self.chuc_vu_field
            elif "Số điện thoại" in msg: field = self.so_dien_thoai_field
            elif "Email" in msg: field = self.email_field

            self._show_error(msg, field)

        except Exception as ex:
            show_error_dialog(self.page, "Lỗi không xác định", str(ex))
