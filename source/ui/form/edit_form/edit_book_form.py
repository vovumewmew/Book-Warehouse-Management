# source/ui/form/edit_form/edit_book_form.py
from decimal import Decimal
import flet as ft
from source.ui.form.edit_form.edit_form_base import EditFormBase
from source.models.Sach import Sach
from source.services.SachService import SachService
from util.get_absolute_path import get_absolute_path

class EditBookForm(EditFormBase):
    def __init__(self, sach: Sach, sach_service: SachService, on_success=None, on_close=None):
        super().__init__(title="Chỉnh sửa sách", on_submit=self.submit_form, on_close=on_close)
        self.sach_service = sach_service
        self.on_success = on_success
        self._sach = sach

        # --- Fields ---
        self.id_field = self.add_field("Mã sách", value=sach.ID_Sach, read_only=True)
        self.name_field = self.add_field("Tên sách", value=sach.TenSach)
        self.author_field = self.add_field("Tác giả", value=sach.TacGia)
        self.category_field = self.add_field("Thể loại", value=sach.TheLoai)
        self.language_field = self.add_field("Ngôn ngữ", value=sach.NgonNgu)
        self.year_field = self.add_field("Năm xuất bản", value=sach.NamXuatBan)
        self.publisher_field = self.add_field("Nhà xuất bản", value=sach.NhaXuatBan)
        self.quantity_field = self.add_field("Số lượng", value=str(sach.SoLuong))
        self.price_field = self.add_field("Giá", value=str(sach.Gia))

        self.image_file = sach.HinhAnh or get_absolute_path(
            "source/ui/picture/book_pic/default_book.jpg"
        )

        # Gán lại nội dung của image_preview (đã có sẵn trong EditFormBase)
        self.image_preview.content = ft.Image(
            src=self.image_file,
            width=120,
            height=120,
            fit=ft.ImageFit.COVER,
            border_radius=ft.border_radius.all(10),
        )

        # --- Clear lỗi khi focus ---
        for field in [self.name_field, self.author_field, self.category_field,
                      self.language_field, self.year_field, self.publisher_field,
                      self.quantity_field, self.price_field]:
            field.on_focus = self.make_clear_error_callback(field)

    def make_clear_error_callback(self, field: ft.TextField):
        def callback(e):
            field.error_text = None
            field.update()  # chỉ update field thôi
        return callback

    def _show_error(self, message: str, field: ft.TextField = None):
        if field:
            field.error_text = message
            field.update()  # chỉ cập nhật field
        else:
            print(f"⚠️ {message}")

    def submit_form(self, e, data=None):
        try:
            data = {
                "ID_Sach": self._sach.ID_Sach,  # readonly
                "TenSach": self.name_field.value.strip(),
                "TacGia": self.author_field.value.strip(),
                "TheLoai": self.category_field.value.strip(),
                "NamXuatBan": self.year_field.value.strip(),
                "NhaXuatBan": self.publisher_field.value.strip(),
                "NgonNgu": self.language_field.value.strip(),
                "SoLuong": self.quantity_field.value.strip(),
                "Gia": self.price_field.value.strip(),
            }

            # --- Validate ---
            try:
                so_luong = int(data["SoLuong"] or 0)
                self.quantity_field.error_text = None
            except ValueError:
                return self._show_error("Số lượng phải là số nguyên!", self.quantity_field)

            try:
                gia = Decimal(data["Gia"] or 0)
                self.price_field.error_text = None
            except:
                return self._show_error("Giá phải hợp lệ!", self.price_field)

            # --- Tính trạng thái ---
            trang_thai = "Còn hàng" if so_luong > 0 else "Hết hàng"
            tinh_kha_dung = "Khả dụng" if trang_thai == "Còn hàng" else "Không khả dụng"

            # --- Tạo object Sach ---
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
                HinhAnh=self.image_file or "source/ui/picture/book_pic/default_book.jpg"
            )

            # --- Update DB ---
            if self.sach_service.update(sach):
                if self.on_success:
                    self.on_success(sach)   # reload page ngoài form
                self.close()                # chỉ đóng form khi update thành công
            else:
                return self._show_error("Không thể cập nhật sách. Kiểm tra dữ liệu hoặc DB.", self.name_field)

        except ValueError as ve:
            msg = str(ve)
            field = None
            if "Mã sách" in msg: field = self.id_field
            elif "Tên sách" in msg: field = self.name_field
            elif "Tác giả" in msg: field = self.author_field
            elif "Thể loại" in msg: field = self.category_field
            elif "Năm xuất bản" in msg: field = self.year_field
            elif "Nhà xuất bản" in msg: field = self.publisher_field
            elif "Ngôn ngữ" in msg: field = self.language_field
            elif "Số lượng" in msg: field = self.quantity_field
            elif "Giá" in msg: field = self.price_field

            self._show_error(msg, field)

        except Exception as ex:
            self._show_error(f"Lỗi không xác định: {ex}", self.name_field)
