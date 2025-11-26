from source.ui.pages.base_page import BasePage
import flet as ft
from config.db_connection import DatabaseConnection
from source.dao.PhieuXuatSachDAO import PhieuXuatSachDAO
from source.services.PhieuXuatSachService import PhieuXuatSachService
from source.dao.ChiTietPhieuXuatDAO import ChiTietPhieuXuatDAO
from source.services.ChiTietPhieuXuatService import ChiTietPhieuXuatService
from source.dao.SachDAO import SachDAO
from source.services.SachService import SachService
from source.ui.form.display_form.export_receipt_form import ExportReceiptForm
from source.ui.button.add_button.add_new_export_receipt import AddNewExportReceipt
from source.ui.search_bar.search_bar_export_receipt import SearchBarExportReceipt
from util.dialog_utils import show_success_dialog

class ExportReceiptPage(BasePage):
    def __init__(self, page: ft.Page, change_page_func, **kwargs):
        super().__init__("Phiếu Xuất Sách")

        self.page = page
        self.change_page = change_page_func
        self.sidebar_button = kwargs.get("sidebar_button")

        # Khởi tạo Service (PHẢI LÀM TRƯỚC)
        db = DatabaseConnection()
        phieuxuat_dao = PhieuXuatSachDAO(db)
        chitiet_dao = ChiTietPhieuXuatDAO(db)
        sach_dao = SachDAO(db)
        self.phieuxuat_service = PhieuXuatSachService(phieuxuat_dao)
        self.chitiet_service = ChiTietPhieuXuatService(chitiet_dao)
        self.sach_service = SachService(sach_dao)
        self.phieuxuat_service.set_chitiet_service(self.chitiet_service) # Liên kết 2 service
        self.phieuxuat_service.set_sach_service(self.sach_service) # Liên kết service sách

        # --- Nút thêm phiếu xuất ---
        add_button = AddNewExportReceipt(
            page=self.page,
            on_add_callback=self.load_receipts # Tải lại bảng sau khi thêm
        )

        # --- Nút refresh ---
        refresh_button = ft.IconButton(
            icon=ft.Icons.REFRESH,
            icon_color=ft.Colors.WHITE,
            bgcolor="#A94F8B",
            width=40,
            height=40,
            tooltip="Làm mới",
            on_click=lambda e: self.sidebar_button.on_click_callback(self.sidebar_button) if self.sidebar_button else None,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        )

        # --- Thanh tìm kiếm ---
        search_bar = SearchBarExportReceipt(
            page=self.page,
            service=self.phieuxuat_service,
            on_search_result=self.display_search_results
        )

        # --- Header ---
        # Cập nhật header sau khi super().__init__ đã được gọi
        self.header_action = ft.Row([add_button, refresh_button, search_bar], spacing=10)

        # Container để chứa bảng, giúp việc thay thế dễ dàng
        self.table_container = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

        # Tạo DataTable
        self.receipt_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Mã Phiếu", weight="bold")),
                ft.DataColumn(ft.Text("Nhân viên", weight="bold")),
                ft.DataColumn(ft.Text("Nhà phân phối", weight="bold")),
                ft.DataColumn(ft.Text("Ngày Xuất", weight="bold")),
                ft.DataColumn(ft.Text("Tổng SL", weight="bold"), numeric=True),
                ft.DataColumn(ft.Text("Tổng Tiền", weight="bold"), numeric=True),
            ],
            rows=[],
            column_spacing=20,
            border=ft.border.all(1, "#A94F8B"),
            border_radius=ft.border_radius.all(10),
            heading_row_color=ft.Colors.with_opacity(0.1, "#A94F8B"),
            data_row_color={"hovered": "#F6EFFF"},
        )

    def build_content(self):
        """Xây dựng nội dung chính của trang."""
        self.load_receipts() # Tải dữ liệu ban đầu

        return ft.Column(
            [
                ft.Divider(height=20, color="transparent"),
                ft.Container(
                    self.table_container,
                    expand=True,
                    padding=10
                )
            ],
            spacing=10,
            expand=True,
        )

    def load_receipts(self, receipts=None):
        """Tải dữ liệu phiếu xuất và cập nhật DataTable."""
        # Giả sử PhieuXuatSachService và model đã được cập nhật tương tự PhieuNhap
        if receipts is None:
            receipts = self.phieuxuat_service.get_all()
        
        # Tạo một DataTable mới với dữ liệu mới
        new_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Mã Phiếu", weight="bold")),
                ft.DataColumn(ft.Text("Nhân viên", weight="bold")),
                ft.DataColumn(ft.Text("Nhà phân phối", weight="bold")),
                ft.DataColumn(ft.Text("Ngày Xuất", weight="bold")),
                ft.DataColumn(ft.Text("Tổng SL", weight="bold"), numeric=True),
                ft.DataColumn(ft.Text("Tổng Tiền", weight="bold"), numeric=True),
            ],
            rows=[],
            column_spacing=20,
            border=ft.border.all(1, "#A94F8B"),
            border_radius=ft.border_radius.all(10),
            heading_row_color=ft.Colors.with_opacity(0.1, "#A94F8B"),
            data_row_color={"hovered": "#F6EFFF"},
        )

        for receipt in receipts:
            # Tính toán lại tổng số lượng và tổng tiền từ chi tiết
            total_quantity = sum(detail.SoLuong for detail in receipt.Danhsachchitietxuat)
            total_price = sum(detail.ThanhTien for detail in receipt.Danhsachchitietxuat)

            new_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(receipt.ID_PhieuXuat)),
                        ft.DataCell(ft.Text(getattr(receipt, 'TenNhanVien', 'N/A'))),
                        ft.DataCell(ft.Text(getattr(receipt, 'TenNhaPhanPhoi', 'N/A'))),
                        ft.DataCell(ft.Text(receipt.NgayXuat.strftime('%d/%m/%Y'))),
                        ft.DataCell(ft.Text(f"{total_quantity}")),
                        ft.DataCell(ft.Text(f"{total_price:,.0f} VNĐ")),
                    ],
                    on_select_changed=lambda e, r=receipt: self.show_receipt_details(r)
                )
            )

        # Thay thế bảng cũ bằng bảng mới trong container
        self.table_container.controls.clear()
        self.table_container.controls.append(new_table)

        if self.page:
            self.page.update()

    def display_search_results(self, results):
        """Hiển thị kết quả tìm kiếm trên bảng."""
        self.load_receipts(receipts=results)

    def show_receipt_details(self, receipt):
        """Hiển thị form chi tiết phiếu xuất."""
        def on_form_close(success_message: str = None):
            self.load_receipts() # Tải lại dữ liệu khi form đóng
            if success_message:
                show_success_dialog(self.page, "Thành công", success_message)

        receipt_form = ExportReceiptForm(receipt, page=self.page, on_close=on_form_close)
        self.page.overlay.append(receipt_form)
        self.page.update()
