import flet as ft
from config.db_connection import DatabaseConnection
from source.dao.NguonNhapSachDAO import NguonNhapSachDAO
from source.ui.pages.base_page import BasePage
from source.ui.Table.supplier_table import SupplierTable

class UnavailableSuppliersPage(BasePage):
    def __init__(self, page: ft.Page, change_page_func, **kwargs):
        """
        Khởi tạo trang nhà cung cấp không khả dụng.
        :param page: Đối tượng ft.Page
        :param change_page_func: Hàm để yêu cầu thay đổi trang
        """
        self.page = page
        self.change_page = change_page_func

        self.suppliers_container = ft.Column(spacing=10, expand=True, scroll=ft.ScrollMode.AUTO)
        self.content_body = self.build_content()

        back_button = ft.IconButton(
            icon=ft.Icons.ARROW_BACK_ROUNDED,
            icon_color=ft.Colors.WHITE,
            bgcolor="#A94F8B",
            width=40,
            height=40,
            tooltip="Quay lại",
            on_click=self.go_back,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        )

        refresh_button = ft.IconButton(
            icon=ft.Icons.REFRESH,
            icon_color=ft.Colors.WHITE,
            bgcolor="#A94F8B",
            width=40,
            height=40,
            tooltip="Làm mới",
            on_click=self.reload_suppliers,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        )

        super().__init__(
            "Nhà cung cấp đã xóa",
            header_action=ft.Row([back_button, refresh_button], spacing=10)
        )

    def build_content(self):
        db = DatabaseConnection()
        conn = db.connect()
        if not conn:
            return ft.Text("Không thể kết nối cơ sở dữ liệu", color="red")

        suppliers = NguonNhapSachDAO(db).get_all_unavailable()
        db.disconnect()

        self.suppliers_container.controls.clear()
        self.suppliers_container.controls.append(SupplierTable(suppliers, page=self.page, columns=3, mode="unavailable"))

        return self.suppliers_container

    def go_back(self, e):
        from source.ui.pages.available_page.suppliers_page import SuppliersPage
        self.change_page(SuppliersPage)

    def reload_suppliers(self, e=None):
        self.build_content()
        page_to_update = self.page if not e else e.control.page
        if page_to_update:
            page_to_update.update()