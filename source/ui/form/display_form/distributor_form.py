import flet as ft
from source.ui.form.display_form.display_form_base import DisplayFormBase
from source.ui.button.edit_button.edit_distributor_button import EditDistributorButton
from source.ui.button.delete_button.delete_distributor_button import DeleteDistributorButton
from source.services.NhaPhanPhoiService import NhaPhanPhoiService
from source.dao.NhaPhanPhoiDAO import NhaPhanPhoiDAO
from config.db_connection import DatabaseConnection
from util.dialog_utils import show_success_dialog, show_error_dialog

class DistributorForm(DisplayFormBase):
    def __init__(self, npp, page: ft.Page = None, on_close=None, mode="available", **kwargs):
        self.page = page
        self._npp = npp
        self.mode = mode

        # --- Khởi tạo DAO & Service trước ---
        db_conn = DatabaseConnection()
        self.npp_dao = NhaPhanPhoiDAO(db_conn)
        self.npp_service = NhaPhanPhoiService(self.npp_dao)

        # --- Mapping label → attribute ---
        self.label_to_attr = {
            "Mã nhà phân phối": "ID_NguonXuat",
            "Tên cơ sở": "TenCoSo",
            "Địa chỉ": "DiaChi",
            "Số điện thoại": "SoDienThoai",
            "Email": "Email",
            "Trạng thái NPP": "TrangThaiNPP",
            "Tính khả dụng": "TinhKhaDung",
        }

        # --- Tạo fields hiển thị từ object npp ---
        fields = {label: getattr(npp, attr, "") for label, attr in self.label_to_attr.items()}

        # --- Gọi super().__init__() sau khi đã có service ---
        super().__init__(
            title=f"{npp.TenCoSo}",
            fields=fields,
            width=450,
            height=550,
            on_close=on_close
        )

    def build_form(self):
        container = super().build_form()
        # Lấy nút "Đóng" ban đầu ra và thay thế bằng một Row chứa các nút hành động
        close_button = container.content.controls.pop()

        action_buttons = []
        if self.mode == "unavailable":
            restore_button = ft.ElevatedButton("Phục hồi", on_click=self.restore_action, color=ft.Colors.WHITE, bgcolor="#A94F8B")
            delete_permanently_button = ft.ElevatedButton("Xóa vĩnh viễn", on_click=self.delete_permanently_action, color=ft.Colors.WHITE, bgcolor="#A94F8B")
            action_buttons.extend([restore_button, delete_permanently_button])
        else: # mode == "available"
            edit_button = EditDistributorButton(distributor=self._npp, npp_service=self.npp_service, page=self.page)
            delete_button = DeleteDistributorButton(page=self.page, on_delete=self._handle_delete)
            action_buttons.extend([edit_button, delete_button])

        action_buttons.append(close_button)

        buttons_row = ft.Row(
            controls=action_buttons,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        )
        container.content.controls.append(buttons_row)

        return container
    
    def _handle_close(self, e):
        super()._handle_close(e)

    def _handle_delete(self, e):
        """Xử lý sự kiện xóa, hiển thị dialog thành công và đóng form."""
        success = self.npp_service.delete(self._npp.ID_NguonXuat)
        if success:
            show_success_dialog(
                self.page,
                "Thành công",
                f"Đã xóa nhà phân phối '{self._npp.TenCoSo}' thành công. Nhà phân phối đã được chuyển vào thùng rác.",
                on_close=lambda: super(DistributorForm, self)._handle_close(e)
            )
        else:
            show_error_dialog(self.page, "Lỗi", "Không thể xóa nhà phân phối. Vui lòng thử lại.")

    def restore_action(self, e):
        def do_restore():
            success = self.npp_service.restore([self._npp.ID_NguonXuat])
            if success:
                show_success_dialog(
                    self.page,
                    "Thành công",
                    f"Đã phục hồi nhà phân phối '{self._npp.TenCoSo}' thành công. Nhà phân phối đã được chuyển về danh sách chính.",
                    on_close=lambda: super(DistributorForm, self)._handle_close(e)
                )
            else:
                show_error_dialog(self.page, "Lỗi", "Không thể phục hồi nhà phân phối. Vui lòng thử lại.")

        self._show_confirmation(
            title="Xác nhận phục hồi",
            message=f"Bạn có chắc chắn muốn phục hồi nhà phân phối '{self._npp.TenCoSo}' không?",
            on_confirm=do_restore
        )

    def delete_permanently_action(self, e):
        def do_delete():
            self.npp_service.completely_delete(self._npp.ID_NguonXuat)
            self.show_snackbar(f"Đã xóa vĩnh viễn nhà phân phối '{self._npp.TenCoSo}'.")
            super(DistributorForm, self)._handle_close(e)

        self._show_confirmation(
            title="Xác nhận xóa vĩnh viễn",
            message=f"Hành động này không thể hoàn tác. Bạn có chắc muốn xóa vĩnh viễn nhà phân phối '{self._npp.TenCoSo}' không?",
            on_confirm=do_delete
        )

    def _show_confirmation(self, title: str, message: str, on_confirm):
        """Hiển thị hộp thoại xác nhận chung."""
        confirm_overlay = None
        
        def close_confirmation(e):
            if self.page and self.page.overlay and confirm_overlay in self.page.overlay:
                self.page.overlay.remove(confirm_overlay)
                self.page.update()

        def confirm_action(e):
            close_confirmation(e)
            on_confirm()

        confirm_box = ft.Container(width=400, height=180, padding=20, bgcolor="#C0ABE4", border_radius=18,
            content=ft.Column([
                    ft.Text(title, size=18, weight="bold", color="#72287F"),
                    ft.Text(message, size=14, color="#72287F", max_lines=3),
                    ft.Row([
                            ft.ElevatedButton("Hủy", bgcolor="#914D86", color="white", on_click=close_confirmation),
                            ft.ElevatedButton("Xác nhận", bgcolor="#914D86", color="white", on_click=confirm_action)
                        ], alignment=ft.MainAxisAlignment.END)
                ], spacing=15))

        confirm_overlay = ft.Container(expand=True, bgcolor=ft.Colors.with_opacity(0.4, ft.Colors.BLACK), alignment=ft.alignment.center, content=confirm_box)
        
        self.page.overlay.append(confirm_overlay)
        self.page.update()

    def show_snackbar(self, message: str):
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message))
        self.page.snack_bar.open = True
        self.page.update()

    def update_fields(self):
        """Cập nhật giá trị hiển thị từ self._npp dựa trên label_to_attr"""
        for label, field in zip(self.fields.keys(), self.fields_column.controls):
            attr_name = self.label_to_attr.get(label)
            if not attr_name:
                continue
            value = getattr(self._npp, attr_name, "")
            field.value = str(value)
        if self.page:
            self.fields_column.update()
