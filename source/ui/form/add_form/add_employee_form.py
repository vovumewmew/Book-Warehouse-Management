import flet as ft
from decimal import Decimal
from .add_form_base import AddFormBase
from source.models.NhanVien import NhanVien
from source.services.NhanVienService import NhanVienService
from source.dao.NhanVienDAO import NhanVienDAO
from config.db_connection import DatabaseConnection
from util.get_absolute_path import get_absolute_path
from util.dialog_utils import show_error_dialog


class AddEmployeeForm(AddFormBase):
    def __init__(self, on_submit=None, on_close=None, on_success=None):
        super().__init__(title="Thêm nhân viên", on_submit=on_submit, on_close=on_close)
        self.on_success = on_success
        self.image_file = None

        # --- Kết nối DB, DAO, Service ---
        self.db = DatabaseConnection()
        nhanvien_dao = NhanVienDAO(self.db)
        self.nhanvien_service = NhanVienService(nhanvien_dao)

        # --- Các trường nhập liệu ---
        self.id_nhan_vien_field = self.add_field("Mã nhân viên")
        self.ten_nhan_vien_field = self.add_field("Tên nhân viên")
        self.so_dien_thoai_field = self.add_field("Số điện thoại")
        self.email_field = self.add_field("Email")

        # --- Dropdown Giới tính ---
        self.gioi_tinh_field = ft.Dropdown(
            label="Giới tính",
            options=[
                ft.dropdown.Option("Nam"),
                ft.dropdown.Option("Nữ"),
            ],
            value="Nam",
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
            value="Nhân viên kiểm kê kho",
            width=450,
            border_color=self.default_border_color,
            focused_border_color=self.default_focused_border_color,
            bgcolor=self.default_field_bgcolor,
            color=self.default_field_color,
            border_radius=12,
        )

                # --- Thêm tất cả field vào layout có sẵn ---
                # --- Chèn 2 dropdown lên trước ô SĐT và Email ---
        # Xóa SĐT và Email khỏi fields_column (nếu đã có)
        if self.so_dien_thoai_field in self.fields_column.controls:
            self.fields_column.controls.remove(self.so_dien_thoai_field)
        if self.email_field in self.fields_column.controls:
            self.fields_column.controls.remove(self.email_field)

        # Thêm lại theo đúng thứ tự mong muốn
        self.fields_column.controls.extend([
            self.gioi_tinh_field,
            self.chuc_vu_field,
            self.so_dien_thoai_field,
            self.email_field,
        ])


        # --- Xóa lỗi khi focus ---
        for field in [
            self.id_nhan_vien_field,
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
            self.page.update()
        return callback

    # Chọn ảnh
    def pick_image(self, e):
        self.file_picker = ft.FilePicker(on_result=self.image_picked)
        self.file_picker.allowed_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]
        self.page.overlay.append(self.file_picker)
        self.file_picker.pick_files(allow_multiple=False)

    def image_picked(self, e: ft.FilePickerResultEvent):
        if e.files:
            self.image_file = e.files[0].path
            self.image_preview.content = ft.Image(
                src=self.image_file, width=120, height=120, fit=ft.ImageFit.COVER
            )
            self.image_preview.update()

    # Hiển thị lỗi
    def show_error_dialog(self, message: str, field=None):
        if field:
            field.error_text = message
            self.page.update()
        else:
            snack = ft.SnackBar(
                content=ft.Text(message, color="white"),
                bgcolor="#F44336",
                duration=4000
            )
            self.page.snack_bar = snack
            snack.open = True
            self.page.update()

    def _close_and_reload(self, data_to_pass):
        """Đóng form và kích hoạt callback on_success để reload trang."""
        # Đóng form hiện tại
        if self.page and self in self.page.overlay:
            self.page.overlay.remove(self)
        
        # Gọi on_success (nếu có) để reload trang
        if self.on_success:
            self.on_success(data_to_pass)
        self.page.update()

    # Xử lý khi bấm "Lưu"
    def _handle_submit(self, e):
        try:
            data = {
                "ID_NhanVien": self.id_nhan_vien_field.value.strip(),
                "HoTen": self.ten_nhan_vien_field.value.strip(),
                "GioiTinh": self.gioi_tinh_field.value,
                "ChucVu": self.chuc_vu_field.value,
                "SoDienThoai": self.so_dien_thoai_field.value.strip(),
                "Email": self.email_field.value.strip(),
            }

            nhanvien = NhanVien(
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

            self.nhanvien_service.create(nhanvien)
            self._close_and_reload(nhanvien) # ✅ Đóng form và reload nếu create() không ném lỗi

        except ValueError as ve:
            msg = str(ve)
            field = None
            if "đã tồn tại" in msg:
                show_error_dialog(self.page, "Lỗi Trùng Lặp", msg)
                self.id_nhan_vien_field.error_text = "Mã này đã được sử dụng"
                self.page.update()
                return
            if "Mã nhân viên" in msg: field = self.id_nhan_vien_field
            elif "Tên nhân viên" in msg: field = self.ten_nhan_vien_field
            elif "Giới tính" in msg: field = self.gioi_tinh_field
            elif "Chức vụ" in msg: field = self.chuc_vu_field
            elif "Số điện thoại" in msg: field = self.so_dien_thoai_field
            elif "Email" in msg: field = self.email_field

            if field:
                field.error_text = msg
                self.page.update()
            else:
                self.show_error_dialog(msg)

        except Exception as ex:
            self.show_error_dialog(f"Lỗi không xác định: {ex}")
