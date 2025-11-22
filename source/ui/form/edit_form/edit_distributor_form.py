import flet as ft
from source.ui.form.edit_form.edit_form_base import EditFormBase
from source.models.NhaPhanPhoi import NhaPhanPhoi
from source.services.NhaPhanPhoiService import NhaPhanPhoiService
from util.get_absolute_path import get_absolute_path


class EditDistributorForm(EditFormBase):
    def __init__(self, npp: NhaPhanPhoi, npp_service: NhaPhanPhoiService, on_success=None, on_close=None):
        super().__init__(title="Chỉnh sửa nhà phân phối", on_submit=self.submit_form, on_close=on_close)
        self.npp_service = npp_service
        self.on_success = on_success
        self._npp = npp

        # --- Fields ---
        self.id_field = self.add_field("Mã nhà phân phối", value=npp.ID_NguonXuat, read_only=True)
        self.name_field = self.add_field("Tên nhà phân phối", value=npp.TenCoSo)
        self.address_field = self.add_field("Địa chỉ", value=npp.DiaChi)
        self.phone_field = self.add_field("Số điện thoại", value=npp.SoDienThoai)
        self.email_field = self.add_field("Email", value=npp.Email)

        # --- Image ---
        self.image_file = npp.HinhAnh or get_absolute_path(
            "source/ui/picture/contributors_pic/contributor_default_pic.jpg"
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
        for field in [
            self.name_field,
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
                "ID_NguonXuat": self._npp.ID_NguonXuat,  # readonly
                "TenCoSo": self.name_field.value.strip(),
                "DiaChi": self.address_field.value.strip(),
                "SoDienThoai": self.phone_field.value.strip(),
                "Email": self.email_field.value.strip(),
            }

            # --- Tạo đối tượng NhaPhanPhoi mới ---
            tinh_kha_dung = "Khả dụng"
            trang_thai_npp = "Hoạt Động" if tinh_kha_dung == "Khả dụng" else "Ngừng hoạt động"

            npp = NhaPhanPhoi(
                ID_NguonXuat=data["ID_NguonXuat"],
                TenCoSo=data["TenCoSo"],
                DiaChi=data["DiaChi"],
                SoDienThoai=data["SoDienThoai"],
                Email=data["Email"],
                TrangThaiNPP=trang_thai_npp,
                TinhKhaDung=tinh_kha_dung,
                HinhAnh=self.image_file
            )

            # --- Cập nhật DB ---
            result = self.npp_service.update(npp)
            if result:
                if self.on_success:
                    self.on_success(npp)
                self.close()
            else:
                return self._show_error("Không thể cập nhật nhà phân phối. Kiểm tra dữ liệu hoặc DB.", self.name_field)

        except ValueError as ve:
            # Map lỗi xuống field tương ứng
            msg = str(ve)
            field = None
            if "Mã nhà phân phối" in msg: field = self.id_field
            elif "Tên cơ sở" in msg: field = self.name_field
            elif "Địa chỉ" in msg: field = self.address_field
            elif "Số điện thoại" in msg: field = self.phone_field
            elif "Email" in msg: field = self.email_field

            self._show_error(msg, field)

        except Exception as ex:
            self._show_error(f"Lỗi không xác định: {ex}", self.name_field)
