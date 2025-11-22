# source/ui/pages/suppliers_page.py
import flet as ft
from source.ui.pages.base_page import BasePage
from config.db_connection import DatabaseConnection
from source.dao.NguonNhapSachDAO import NguonNhapSachDAO
from source.ui.Table.supplier_table import SupplierTable
from source.ui.button.add_button.add_new_supplier import AddNewSupplier
from source.ui.search_bar.search_bar_supplier import SearchBarSupplier
from util.excel_generator import ExcelGenerator
from source.services.NguonNhapSachService import NguonNhapSachService

class SuppliersPage(BasePage):
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
        supplier_dao = NguonNhapSachDAO(db)
        self.supplier_service = NguonNhapSachService(supplier_dao)

        # --- Container table ---
        self.supplier_container = ft.Column(spacing=10, expand=True, scroll=ft.ScrollMode.AUTO)
        self.content_body = self.build_content()

        search_bar = SearchBarSupplier(
            page=self.page, 
            supplier_container=self.supplier_container,
            width=300
        )

        # --- Nút thêm nhà cung cấp ---
        add_button = AddNewSupplier(
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
            on_click=self.reload_suppliers,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        )

        # --- Nút "Xem đã xóa" ---
        trash_button = ft.IconButton(
            icon=ft.Icons.DELETE_SWEEP_ROUNDED,
            icon_color=ft.Colors.WHITE,
            bgcolor="#A94F8B",
            width=40,
            height=40,
            tooltip="Xem nhà cung cấp đã xóa",
            on_click=self.show_unavailable_suppliers,
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
            "Nhà cung cấp",
            header_action=ft.Row([trash_button, add_button, refresh_button, export_excel_button, search_bar], spacing=10)
        )

    def build_content(self):
        db = DatabaseConnection()
        conn = db.connect()
        if not conn:
            return ft.Text("Không thể kết nối cơ sở dữ liệu", color="red")

        ncc = NguonNhapSachDAO(db).get_all()
        db.disconnect()

        self.supplier_container.controls.clear()
        self.supplier_container.controls.append(SupplierTable(ncc, page=self.page, columns=3))

        return ft.Container(
            expand=True,
            content=ft.Column(
                [
                    ft.Divider(height=20, color="transparent"),
                    self.supplier_container
                ],
                spacing=10,
                expand=True,
                scroll=ft.ScrollMode.AUTO
            )
        )

    def reload_suppliers(self, e=None):
        db = DatabaseConnection()
        ncc = NguonNhapSachDAO(db).get_all()
        db.disconnect()

        self.supplier_container.controls.clear()
        page_to_update = getattr(e.control, "page", self.page)
        self.supplier_container.controls.append(SupplierTable(ncc, page=page_to_update, columns=3))
        if page_to_update:
            page_to_update.update()

    def show_unavailable_suppliers(self, e):
        """Hiển thị trang nhà cung cấp không khả dụng."""
        from source.ui.pages.unavailable_page.unavailable_suppliers_page import UnavailableSuppliersPage
        self.change_page(UnavailableSuppliersPage)

    def export_to_excel(self, e):
        """Mở hộp thoại lưu file để xuất Excel."""
        self.file_picker.save_file(
            dialog_title="Lưu file Excel",
            file_name="DanhSachNhaCungCap.xlsx",
            allowed_extensions=["xlsx"]
        )

    def save_excel_result(self, e: ft.FilePickerResultEvent):
        """Callback sau khi người dùng chọn nơi lưu file."""
        if e.path:
            page = e.page
            all_suppliers = self.supplier_service.get_all()
            if self.excel_generator.generate_suppliers_excel(all_suppliers, e.path):
                page.snack_bar = ft.SnackBar(content=ft.Text(f"Đã lưu file Excel thành công!"), bgcolor="#2A9D8F")
            else:
                page.snack_bar = ft.SnackBar(content=ft.Text("Lỗi: Không thể tạo file Excel."), bgcolor=ft.colors.ERROR)
            page.snack_bar.open = True
            page.update()
