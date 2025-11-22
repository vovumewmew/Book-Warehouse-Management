import flet as ft
from .edit_button_base import EditButtonBase
from source.ui.form.edit_form.edit_distributor_form import EditDistributorForm

class EditDistributorButton(EditButtonBase):
    def __init__(self, distributor, npp_service, page: ft.Page):
        """
        distributor: đối tượng NhaPhanPhoi cần sửa
        npp_service: service (NhaPhanPhoiService) có method update(...)
        page: ft.Page hiện tại (để đặt page.dialog / snack_bar)
        """
        # tạo nút base với callback là method _open_edit_form
        super().__init__(text="Sửa", on_edit=self._open_edit_form)
        self.distributor = distributor
        self.npp_service = npp_service
        self.page = page

    def _open_edit_form(self, e):
        if not (self.distributor and self.npp_service and self.page):
            print("Thiếu distributor / service / page để mở form chỉnh sửa")
            return

        def on_success(updated_distributor):
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Đã cập nhật nhà phân phối '{updated_distributor.TenCoSo}'"),
                bgcolor="#4CAF50",
                duration=2500
            )
            self.page.snack_bar.open = True
            self.page.update()

            if hasattr(self.page, "dialog") and self.page.dialog:
                try:
                    self.page.dialog.open = False
                except:
                    pass
                self.page.update()

        def on_close(ev=None):
            if hasattr(self.page, "dialog") and self.page.dialog:
                try:
                    self.page.dialog.open = False
                except:
                    pass
                self.page.update()

        # Khởi tạo EditDistributorForm
        form = EditDistributorForm(
            npp=self.distributor,          # trực tiếp đối tượng NhaPhanPhoi
            npp_service=self.npp_service,
            on_success=on_success,
            on_close=on_close
        )
        form.open_form(self.page)
