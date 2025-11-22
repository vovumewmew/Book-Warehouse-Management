import flet as ft
from decimal import Decimal
from .add_form_base import AddFormBase
from source.models.Sach import Sach
from source.services.SachService import SachService
from source.dao.SachDAO import SachDAO
from config.db_connection import DatabaseConnection
from util.get_absolute_path import get_absolute_path
from util.dialog_utils import show_error_dialog
 
class AddBookForm(AddFormBase): 
    def __init__(self, on_submit=None, on_close=None, on_success=None):
        super().__init__(title="Thêm sách", on_submit=on_submit, on_close=on_close)
        self.on_success = on_success

        # --- Các trường nhập liệu ---
        self.id_sach_field = self.add_field("Mã sách")
        self.ten_sach_field = self.add_field("Tên sách")
        self.tac_gia_field = self.add_field("Tác giả")
        self.the_loai_field = self.add_field("Thể loại")
        self.nam_xuat_ban_field = self.add_field("Năm xuất bản")
        self.nha_xuat_ban_field = self.add_field("Nhà xuất bản")
        self.ngon_ngu_field = self.add_field("Ngôn ngữ")
        self.so_luong_field = self.add_field("Số lượng")
        self.gia_field = self.add_field("Giá", prefix_text="₫")

        # --- Thêm ảnh ---
        self.image_file = None

        # --- DB/DAO/Service ---
        self.db = DatabaseConnection()
        conn = self.db.connect()
        sach_dao = SachDAO(self.db)
        self.sach_service = SachService(sach_dao)

        # --- Clear lỗi khi focus ---
        for field in [
            self.id_sach_field,
            self.ten_sach_field,
            self.tac_gia_field,
            self.the_loai_field,
            self.nam_xuat_ban_field,
            self.nha_xuat_ban_field,
            self.ngon_ngu_field,
            self.so_luong_field,
            self.gia_field,
        ]:
            field.on_focus = self.make_clear_error_callback(field)

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
            self.image_preview.src = self.image_file
            self.page.update()

    def show_error_dialog(self, message: str, field=None):
        """
        Hiển thị thông báo lỗi.
        Nếu field được chỉ định, hiển thị lỗi trực tiếp trên field.
        Nếu không, hiển thị SnackBar đỏ trên page.
        """
        if field:
            field.error_text = message
            self.page.update()
        else:
            # SnackBar đỏ thay cho AlertDialog
            snack = ft.SnackBar(
                content=ft.Text(message, color="white"),
                bgcolor="#F44336",  # đỏ
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

    def _handle_submit(self, e):
        try:
            # Lấy dữ liệu từ field
            data = {
                "ID_Sach": self.id_sach_field.value.strip(),
                "TenSach": self.ten_sach_field.value.strip(),
                "TacGia": self.tac_gia_field.value.strip(),
                "TheLoai": self.the_loai_field.value.strip(),
                "NamXuatBan": self.nam_xuat_ban_field.value.strip(),
                "NhaXuatBan": self.nha_xuat_ban_field.value.strip(),
                "NgonNgu": self.ngon_ngu_field.value.strip(),
                "SoLuong": self.so_luong_field.value.strip(),
                "Gia": self.gia_field.value.strip()
            }
 
            # --- Convert dữ liệu SoLuong và Gia ---
            try:
                so_luong = int(data["SoLuong"] or 0)
            except ValueError:
                self.so_luong_field.error_text = "Số lượng phải là số nguyên!"
                self.page.update()
                return False

            try:
                gia = Decimal(data["Gia"] or 0.0)
            except:
                self.gia_field.error_text = "Giá phải là số hợp lệ!"
                self.page.update()
                return False

            # Tính trạng thái
            trang_thai = "Còn hàng" if so_luong > 0 else "Hết hàng"
            tinh_kha_dung = "Khả dụng" if trang_thai == "Còn hàng" else "Không khả dụng"

            # --- Tạo đối tượng Sach, gọi validate trong model ---
            sach = Sach(
                ID_Sach=data["ID_Sach"],
                TenSach=data["TenSach"],
                TacGia=data["TacGia"],
                TheLoai=data["TheLoai"],
                NamXuatBan=data["NamXuatBan"],
                NhaXuatBan=data["NhaXuatBan"],
                NgonNgu=data["NgonNgu"],
                SoLuong=so_luong,
                Gia=gia,
                TrangThai=trang_thai,
                TinhKhaDung=tinh_kha_dung,
                HinhAnh=self.image_file or get_absolute_path("source/ui/picture/book_pic/default_book.jpg")
            )

            # --- Thêm sách vào DB ---
            self.sach_service.create(sach)
            self._close_and_reload(sach) # ✅ Đóng form và reload nếu create() không ném lỗi

        except ValueError as ve:
            # Map lỗi từ model xuống field
            msg = str(ve)

            # Bắt lỗi trùng lặp từ Service
            if "đã tồn tại" in msg:
                show_error_dialog(self.page, "Lỗi Trùng Lặp", msg)
                self.id_sach_field.error_text = "Mã này đã được sử dụng"
                self.page.update()

            field = None
            if "Mã sách" in msg: field = self.id_sach_field
            elif "Tên sách" in msg: field = self.ten_sach_field
            elif "Tác giả" in msg: field = self.tac_gia_field
            elif "Thể loại" in msg: field = self.the_loai_field
            elif "Năm xuất bản" in msg: field = self.nam_xuat_ban_field
            elif "Nhà xuất bản" in msg: field = self.nha_xuat_ban_field
            elif "Ngôn ngữ" in msg: field = self.ngon_ngu_field
            elif "Số lượng" in msg: field = self.so_luong_field
            elif "Giá" in msg: field = self.gia_field

            if field:
                field.error_text = msg
                self.page.update()

        except Exception as ex:
            self.show_error_dialog(f"Lỗi không xác định: {ex}")
