import flet as ft
from config.db_connection import DatabaseConnection
from source.dao.NhaPhanPhoiDAO import NhaPhanPhoiDAO
from source.ui.pages.base_page import BasePage
from source.ui.Table.distributor_table import DistributorTable

class UnavailableDistributorsPage(BasePage):
    def __init__(self, page: ft.Page, change_page_func, **kwargs):
        """
        Khởi tạo trang nhà phân phối không khả dụng.
        :param page: Đối tượng ft.Page
        :param change_page_func: Hàm để yêu cầu thay đổi trang
        """
        self.page = page
        self.change_page = change_page_func

        self.distributors_container = ft.Column(spacing=10, expand=True, scroll=ft.ScrollMode.AUTO)
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
            on_click=self.reload_distributors,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        )

        super().__init__(
            "Nhà phân phối đã xóa",
            header_action=ft.Row([back_button, refresh_button], spacing=10)
        )

    def build_content(self):
        db = DatabaseConnection()
        conn = db.connect()
        if not conn:
            return ft.Text("Không thể kết nối cơ sở dữ liệu", color="red")

        distributors = NhaPhanPhoiDAO(db).get_all_unavailable()
        db.disconnect()

        self.distributors_container.controls.clear()
        self.distributors_container.controls.append(DistributorTable(distributors, page=self.page, columns=3, mode="unavailable"))

        return self.distributors_container

    def go_back(self, e):
        from source.ui.pages.available_page.distributor_page import DistributorsPage
        self.change_page(DistributorsPage)

    def reload_distributors(self, e=None):
        self.build_content()
        page_to_update = self.page if not e else e.control.page
        if page_to_update:
            page_to_update.update()