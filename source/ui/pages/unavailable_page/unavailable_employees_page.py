import flet as ft
from config.db_connection import DatabaseConnection
from source.dao.NhanVienDAO import NhanVienDAO
from source.ui.pages.base_page import BasePage
from source.ui.Table.employees_table import EmployeeTable

class UnavailableEmployeesPage(BasePage):
    def __init__(self, page: ft.Page, change_page_func, **kwargs):
        """
        Khởi tạo trang nhân viên không khả dụng.
        :param page: Đối tượng ft.Page
        :param change_page_func: Hàm để yêu cầu thay đổi trang
        """
        self.page = page
        self.change_page = change_page_func

        self.employees_container = ft.Column(spacing=10, expand=True, scroll=ft.ScrollMode.AUTO)
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
            on_click=self.reload_employees,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        )

        super().__init__(
            "Nhân viên đã xóa",
            header_action=ft.Row([back_button, refresh_button], spacing=10)
        )

    def build_content(self):
        db = DatabaseConnection()
        conn = db.connect()
        if not conn:
            return ft.Text("Không thể kết nối cơ sở dữ liệu", color="red")

        employees = NhanVienDAO(db).get_all_unavailable()
        db.disconnect()

        self.employees_container.controls.clear()
        self.employees_container.controls.append(EmployeeTable(employees, page=self.page, columns=3, mode="unavailable"))

        return self.employees_container

    def go_back(self, e):
        from source.ui.pages.available_page.employees_page import EmployeesPage
        self.change_page(EmployeesPage)

    def reload_employees(self, e=None):
        self.build_content()
        page_to_update = self.page if not e else e.control.page
        if page_to_update:
            page_to_update.update()