import flet as ft
from source.ui.form.edit_form.edit_form_base import EditFormBase
from source.models.NguonNhapSach import NguonNhapSach
from source.services.NguonNhapSachService import NguonNhapSachService
from util.get_absolute_path import get_absolute_path


class EditSupplierForm(EditFormBase):
    def __init__(self, supplier: NguonNhapSach, supplier_service: NguonNhapSachService, on_success=None, on_close=None):
        super().__init__(title="Chỉnh sửa nhà cung cấp", on_submit=self.submit_form, on_close=on_close)
        self.supplier_service = supplier_service
        self.on_success = on_success
        self._supplier = supplier

        # --- Fields ---
        self.id_field = self.add_field("Mã nhà cung cấp", value=supplier.ID_NguonNhap, read_only=True)
        self.name_field = self.add_field("Tên nhà cung cấp", value=supplier.TenCoSo)
        self.method_field = self.add_field("Hình thức nhập", value=supplier.HinhThucNhap)
        self.address_field = self.add_field("Địa chỉ", value=supplier.DiaChi)
        self.phone_field = self.add_field("Số điện thoại", value=supplier.SoDienThoai)
        self.email_field = self.add_field("Email", value=supplier.Email)

        # --- Image ---
        self.image_file = supplier.HinhAnh or get_absolute_path("source/ui/picture/supplier_pic/supplier_default_pic.jpg")

        # Gán lại image_preview (có sẵn trong EditFormBase)
        self.image_preview.content = ft.Image(
            src=self.image_file,
            width=120,
            height=120,
            fit=ft.ImageFit.COVER,
            border_radius=ft.border_radius.all(10),
        )

        # --- Clear lỗi khi focus ---
        for field in [
            self.name_field,
            self.method_field,
            self.address_field,
            self.phone_field,
            self.email_field
        ]:
            field.on_focus = self.make_clear_error_callback(field)

    def make_clear_error_callback(self, field: ft.TextField):
        def callback(e):
            field.error_text = None
            field.update()
        return callback

    def _show_error(self, message: str, field: ft.TextField = None):
        if field:
            field.error_text = message
            field.update()
        else:
            print(f"⚠️ {message}")

    def submit_form(self, e, data=None):
        try:
            data = {
                "ID_NguonNhap": self._supplier.ID_NguonNhap,  # readonly
                "TenCoSo": self.name_field.value.strip(),
                "HinhThucNhap": self.method_field.value.strip(),
                "DiaChi": self.address_field.value.strip(),
                "SoDienThoai": self.phone_field.value.strip(),
                "Email": self.email_field.value.strip(),
            }

            tinh_kha_dung = "Khả dụng"
            trang_thai_ncc = "Hoạt Động" if tinh_kha_dung == "Khả dụng" else "Ngừng hoạt động"

            # --- Tạo object NguonNhapSach mới ---
            supplier = NguonNhapSach(
                ID_NguonNhap=data["ID_NguonNhap"],
                TenCoSo=data["TenCoSo"],
                HinhThucNhap=data["HinhThucNhap"],
                DiaChi=data["DiaChi"],
                SoDienThoai=data["SoDienThoai"],
                Email=data["Email"],
                TrangThaiNCC=trang_thai_ncc,
                TinhKhaDung=tinh_kha_dung,
                HinhAnh=self.image_file
            )

            # --- Update DB ---
            result = self.supplier_service.update(supplier)
            if result:
                if self.on_success:
                    self.on_success(supplier)
                self.close()
            else:
                return self._show_error("Không thể cập nhật nhà cung cấp. Kiểm tra dữ liệu hoặc DB.", self.name_field)

        except ValueError as ve:
            # Map lỗi xuống field tương ứng
            msg = str(ve)
            field = None
            if "Mã nhà cung cấp" in msg: field = self.id_field
            elif "Tên nhà cung cấp" in msg: field = self.name_field
            elif "Hình thức nhập" in msg: field = self.method_field
            elif "Địa chỉ" in msg: field = self.address_field
            elif "Số điện thoại" in msg: field = self.phone_field
            elif "Email" in msg: field = self.email_field

            self._show_error(msg, field)

        except Exception as ex:
            self._show_error(f"Lỗi không xác định: {ex}", self.name_field)
