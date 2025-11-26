import flet as ft
from .add_form_base import AddFormBase
from source.models.NguonNhapSach import NguonNhapSach
from source.services.NguonNhapSachService import NguonNhapSachService
from source.dao.NguonNhapSachDAO import NguonNhapSachDAO
from config.db_connection import DatabaseConnection
from util.get_absolute_path import get_absolute_path
from util.dialog_utils import show_error_dialog, show_success_dialog

class AddSupplierForm(AddFormBase):
    def __init__(self, on_submit=None, on_close=None, on_success=None):
        super().__init__(title="Thêm nhà cung cấp", on_submit=on_submit, on_close=on_close)
        self.on_success = on_success

        # --- Các trường nhập liệu ---
        self.id_npp_field = self.add_field("Mã nhà cung cấp")
        self.ten_co_so_field = self.add_field("Tên nhà cung cấp")
        self.hinh_thuc_nhap_field = self.add_field("Hình thức nhập")
        self.dia_chi_field = self.add_field("Địa chỉ")
        self.so_dien_thoai_field = self.add_field("Số điện thoại")
        self.email_field = self.add_field("Email")

        # --- Thêm ảnh ---
        self.image_file = None

        # --- DB/DAO/Service ---
        self.db = DatabaseConnection()
        ncc_dao = NguonNhapSachDAO(self.db)
        self.ncc_service = NguonNhapSachService(ncc_dao)

        # --- Clear lỗi khi focus ---
        for field in [
            self.id_npp_field,
            self.ten_co_so_field,
            self.hinh_thuc_nhap_field,
            self.dia_chi_field,
            self.so_dien_thoai_field,
            self.email_field,
        ]:
            field.on_focus = self.make_clear_error_callback(field)

    def make_clear_error_callback(self, field):
        def callback(e):
            field.error_text = None
            self.page.update()
        return callback

    # Chọn ảnh
    def pick_image(self, e):
        self.image_picker = ft.FilePicker(on_result=self.image_picked)
        self.page.overlay.append(self.image_picker)
        self.file_picker.allowed_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]
        self.image_picker.pick_files(allow_multiple=False)

    def image_picked(self, e: ft.FilePickerResultEvent):
        if e.files:
            self.image_file = e.files[0].path
            self.image_preview.src = self.image_file
            self.page.update()

    # Hiển thị lỗi trên TextField hoặc SnackBar
    def show_error_dialog(self, message: str, field: ft.TextField = None):
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

    # Xử lý submit
    def _handle_submit(self, e):
        try:
            data = {
                "ID_NguonNhap": self.id_npp_field.value.strip(),
                "TenCoSo": self.ten_co_so_field.value.strip(),
                "HinhThucNhap": self.hinh_thuc_nhap_field.value.strip(),
                "DiaChi": self.dia_chi_field.value.strip(),
                "SoDienThoai": self.so_dien_thoai_field.value.strip(),
                "Email": self.email_field.value.strip(),
            }

            tinh_kha_dung = "Khả dụng"
            trang_thai_ncc = "Hoạt Động" if tinh_kha_dung == "Khả dụng" else "Ngừng hoạt động"

            # Tạo đối tượng NhaPhanPhoi
            ncc = NguonNhapSach(
                ID_NguonNhap=data["ID_NguonNhap"],
                TenCoSo=data["TenCoSo"],
                HinhThucNhap=data["HinhThucNhap"],
                DiaChi=data["DiaChi"],
                SoDienThoai=data["SoDienThoai"],
                Email=data["Email"],
                TrangThaiNCC=trang_thai_ncc,
                TinhKhaDung=tinh_kha_dung,
                HinhAnh=self.image_file or get_absolute_path("source/ui/picture/supplier_pic/supplier_default_pic.jpg")
            )

            self.ncc_service.create(ncc)
            
            show_success_dialog(
                self.page, "Thành công", f"Đã thêm nhà cung cấp '{ncc.TenCoSo}' thành công!",
                on_close=lambda: self._close_and_reload(ncc)
            )

        except ValueError as ve:
            # Map lỗi model xuống field
            msg = str(ve)
            field = None
            if "đã tồn tại" in msg:
                show_error_dialog(self.page, "Lỗi Trùng Lặp", msg)
                self.id_npp_field.error_text = "Mã này đã được sử dụng"
                self.page.update()
                return

            if "Mã nhà cung cấp" in msg: field = self.id_npp_field
            elif "Tên nhà cung cấp" in msg: field = self.ten_co_so_field
            elif "Hình thức nhập" in msg: field = self.hinh_thuc_nhap_field
            elif "Địa chỉ" in msg: field = self.dia_chi_field
            elif "Số điện thoại" in msg: field = self.so_dien_thoai_field
            elif "Email" in msg: field = self.email_field
            if field:
                self.show_error_dialog(msg, field)
            else:
                self.show_error_dialog(msg)

        except Exception as ex:
            self.show_error_dialog(f"Lỗi không xác định: {ex}")
