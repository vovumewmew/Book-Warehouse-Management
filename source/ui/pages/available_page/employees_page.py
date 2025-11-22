# source/ui/pages/employees_page.py
import flet as ft
from config.db_connection import DatabaseConnection
from source.ui.pages.base_page import BasePage
from source.ui.Table.employees_table import EmployeeTable
from source.dao.NhanVienDAO import NhanVienDAO
from source.ui.button.add_button.add_new_employee import AddNewEmployee
from source.ui.search_bar.search_bar_employee import SearchBarEmployee
from util.excel_generator import ExcelGenerator
from source.services.NhanVienService import NhanVienService

class EmployeesPage(BasePage):
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
        nhanvien_dao = NhanVienDAO(db)
        self.nhanvien_service = NhanVienService(nhanvien_dao)

        # --- Container table ---
        self.employees_container = ft.Column(spacing=10, expand=True, scroll=ft.ScrollMode.AUTO)
        self.content_body = self.build_content()

        # --- Nút thêm nhân viên ---
        add_button = AddNewEmployee(
            page=self.page,
        )
        add_button.page = self.page
        search_bar = SearchBarEmployee(
            page=self.page, 
            employees_container=self.employees_container, 
            width=300
        )

        # --- Nút refresh ---
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

        # --- Nút "Xem đã xóa" ---
        trash_button = ft.IconButton(
            icon=ft.Icons.DELETE_SWEEP_ROUNDED,
            icon_color=ft.Colors.WHITE,
            bgcolor="#A94F8B",
            width=40,
            height=40,
            tooltip="Xem nhân viên đã xóa",
            on_click=self.show_unavailable_employees,
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
            "Nhân Viên",
            header_action=ft.Row([trash_button, add_button, refresh_button, export_excel_button, search_bar], spacing=10)
        )

    def build_content(self):
        db = DatabaseConnection()
        conn = db.connect()
        if not conn:
            return ft.Text("Không thể kết nối cơ sở dữ liệu", color="red")

        employees = NhanVienDAO(db).get_all()
        db.disconnect()

        self.employees_container.controls.clear()
        self.employees_container.controls.append(EmployeeTable(employees, page=self.page, columns=3))

        return ft.Container(
            expand=True,
            content=ft.Column(
                [
                    ft.Divider(height=20, color="transparent"),
                    self.employees_container
                ],
                spacing=10,
                expand=True,
                scroll=ft.ScrollMode.AUTO
            )
        )

    def reload_employees(self, e=None):
        db = DatabaseConnection()
        employees = NhanVienDAO(db).get_all()
        db.disconnect()

        self.employees_container.controls.clear()
        page_to_update = getattr(e.control, "page", self.page)
        self.employees_container.controls.append(EmployeeTable(employees, page=page_to_update, columns=3))
        if page_to_update:
            page_to_update.update()

    def show_unavailable_employees(self, e):
        """Hiển thị trang nhân viên không khả dụng."""
        from source.ui.pages.unavailable_page.unavailable_employees_page import UnavailableEmployeesPage
        self.change_page(UnavailableEmployeesPage)

    def export_to_excel(self, e):
        """Mở hộp thoại lưu file để xuất Excel."""
        self.file_picker.save_file(
            dialog_title="Lưu file Excel",
            file_name="DanhSachNhanVien.xlsx",
            allowed_extensions=["xlsx"]
        )

    def save_excel_result(self, e: ft.FilePickerResultEvent):
        """Callback sau khi người dùng chọn nơi lưu file."""
        if e.path:
            page = e.page
            all_employees = self.nhanvien_service.get_all()
            if self.excel_generator.generate_employees_excel(all_employees, e.path):
                page.snack_bar = ft.SnackBar(content=ft.Text(f"Đã lưu file Excel thành công!"), bgcolor="#2A9D8F")
            else:
                page.snack_bar = ft.SnackBar(content=ft.Text("Lỗi: Không thể tạo file Excel."), bgcolor=ft.colors.ERROR)
            page.snack_bar.open = True
            page.update()
