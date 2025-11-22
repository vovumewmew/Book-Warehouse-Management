# source/ui/pages/distributors_page.py
import flet as ft
from source.ui.pages.base_page import BasePage
from config.db_connection import DatabaseConnection
from source.dao.NhaPhanPhoiDAO import NhaPhanPhoiDAO
from source.ui.Table.distributor_table import DistributorTable
from source.ui.button.add_button.add_new_distributor import AddNewDistributor
from source.ui.search_bar.search_bar_distributor import SearchBarDistributor
from util.excel_generator import ExcelGenerator
from source.services.NhaPhanPhoiService import NhaPhanPhoiService

class DistributorsPage(BasePage):
    def __init__(self, page: ft.Page, change_page_func, **kwargs):
        self.page = page  # đảm bảo page luôn có giá trị
        self.change_page = change_page_func

        # --- File Picker để lưu Excel ---
        self.file_picker = ft.FilePicker(on_result=self.save_excel_result)
        if self.page:
            self.page.overlay.append(self.file_picker)

        self.excel_generator = ExcelGenerator()

        # --- Khởi tạo Service ---
        db = DatabaseConnection()
        distributor_dao = NhaPhanPhoiDAO(db)
        self.distributor_service = NhaPhanPhoiService(distributor_dao)

        # --- Container table ---
        self.distributors_container = ft.Column(spacing=10, expand=True, scroll=ft.ScrollMode.AUTO)
        self.content_body = self.build_content()

        search_bar = SearchBarDistributor(
            page=self.page, 
            distributors_container=self.distributors_container,
            width=300
        )

        # --- Nút thêm nhà phân phối ---
        add_button = AddNewDistributor(
            page=self.page,
        )
        add_button.page = self.page

        # --- Nút refresh ---
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

        # --- Nút "Xem đã xóa" ---
        trash_button = ft.IconButton(
            icon=ft.Icons.DELETE_SWEEP_ROUNDED,
            icon_color=ft.Colors.WHITE,
            bgcolor="#A94F8B",
            width=40,
            height=40,
            tooltip="Xem nhà phân phối đã xóa",
            on_click=self.show_unavailable_distributors,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        )

        # --- Nút Xuất Excel ---
        export_excel_button = ft.IconButton(
            icon=ft.Icons.TABLE_VIEW_ROUNDED,
            icon_color=ft.Colors.WHITE,
            bgcolor="#2A9D8F",
            width=40,
            height=40,
            tooltip="Xuất ra file Excel",
            on_click=self.export_to_excel,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        )

        # --- Header gồm 2 nút ---
        super().__init__(
            "Nhà phân phối",
            header_action=ft.Row([trash_button, add_button, refresh_button, export_excel_button, search_bar], spacing=10)
        )

    def build_content(self):
        db = DatabaseConnection()
        conn = db.connect()
        if not conn:
            return ft.Text("Không thể kết nối cơ sở dữ liệu", color="red")

        npp = NhaPhanPhoiDAO(db).get_all()
        db.disconnect()

        self.distributors_container.controls.clear()
        self.distributors_container.controls.append(DistributorTable(npp, page=self.page, columns=3))

        return ft.Container(
            expand=True,
            content=ft.Column(
                [
                    ft.Divider(height=20, color="transparent"),
                    self.distributors_container
                ],
                spacing=10,
                expand=True,
                scroll=ft.ScrollMode.AUTO
            )
        )

    def reload_distributors(self, e=None):
        db = DatabaseConnection()
        npp = NhaPhanPhoiDAO(db).get_all()
        db.disconnect()

        self.distributors_container.controls.clear()
        page_to_update = getattr(e.control, "page", self.page)
        self.distributors_container.controls.append(DistributorTable(npp, page=page_to_update, columns=3))
        if page_to_update:
            page_to_update.update()

    def show_unavailable_distributors(self, e):
        """Hiển thị trang nhà phân phối không khả dụng."""
        from source.ui.pages.unavailable_page.unavailable_distributors_page import UnavailableDistributorsPage
        self.change_page(UnavailableDistributorsPage)

    def export_to_excel(self, e):
        """Mở hộp thoại lưu file để xuất Excel."""
        self.file_picker.save_file(
            dialog_title="Lưu file Excel",
            file_name="DanhSachNhaPhanPhoi.xlsx",
            allowed_extensions=["xlsx"]
        )

    def save_excel_result(self, e: ft.FilePickerResultEvent):
        """Callback sau khi người dùng chọn nơi lưu file."""
        if e.path:
            page = e.page
            all_distributors = self.distributor_service.get_all()
            if self.excel_generator.generate_distributors_excel(all_distributors, e.path):
                page.snack_bar = ft.SnackBar(content=ft.Text(f"Đã lưu file Excel thành công!"), bgcolor="#2A9D8F")
            else:
                page.snack_bar = ft.SnackBar(content=ft.Text("Lỗi: Không thể tạo file Excel."), bgcolor=ft.colors.ERROR)
            page.snack_bar.open = True
            page.update()
