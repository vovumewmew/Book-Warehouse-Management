from source.ui.pages.base_page import BasePage
import flet as ft
import datetime

# Import các trang đích để điều hướng
from source.ui.pages.available_page.books_page import BooksPage
from source.ui.pages.available_page.employees_page import EmployeesPage
from source.ui.pages.available_page.suppliers_page import SuppliersPage
from source.ui.pages.available_page.distributor_page import DistributorsPage
from source.ui.pages.available_page.import_receipt_page import ImportReceiptPage
from source.ui.pages.available_page.export_receipt_page import ExportReceiptPage
from config.db_connection import DatabaseConnection
from source.dao.SachDAO import SachDAO
from source.services.SachService import SachService
from source.dao.NhanVienDAO import NhanVienDAO
from source.services.NhanVienService import NhanVienService
from source.dao.PhieuNhapSachDAO import PhieuNhapSachDAO
from source.services.PhieuNhapSachService import PhieuNhapSachService
from source.dao.NguonNhapSachDAO import NguonNhapSachDAO
from source.services.NguonNhapSachService import NguonNhapSachService
from source.dao.NhaPhanPhoiDAO import NhaPhanPhoiDAO
from source.services.NhaPhanPhoiService import NhaPhanPhoiService
from source.dao.PhieuXuatSachDAO import PhieuXuatSachDAO
from source.services.PhieuXuatSachService import PhieuXuatSachService
from source.ui.card.dashboard_card import DashboardCard
from source.ui.chart.monthly_chart import MonthlyChart
from source.ui.chart.category_pie_chart import CategoryPieChart
from source.ui.chart.top_partners_chart import TopPartnersChart

class HomePage(BasePage):
    def __init__(self, **kwargs):
        # Lấy change_page_func từ kwargs và lưu lại
        self.change_page = kwargs.get("change_page_func")
        super().__init__("Trang chủ") # Không truyền kwargs vào lớp cha nữa
        self.db = DatabaseConnection()
        
        # Khởi tạo các service cần thiết
        self.sach_service = SachService(SachDAO(self.db))
        self.nhanvien_service = NhanVienService(NhanVienDAO(self.db))
        
        phieunhap_dao = PhieuNhapSachDAO(self.db)
        self.phieunhap_service = PhieuNhapSachService(phieunhap_dao)

        phieuxuat_dao = PhieuXuatSachDAO(self.db)
        self.phieuxuat_service = PhieuXuatSachService(phieuxuat_dao)

        self.nhacungcap_service = NguonNhapSachService(NguonNhapSachDAO(self.db))
        self.nhaphanphoi_service = NhaPhanPhoiService(NhaPhanPhoiDAO(self.db))

    def _format_currency(self, value):
        """Hàm tiện ích để định dạng số tiền lớn."""
        if value >= 1_000_000_000:
            return f"{value / 1_000_000_000:.1f} Tỷ"
        if value >= 1_000_000:
            return f"{value / 1_000_000:.1f} Tr"
        if value >= 1_000:
            return f"{value / 1_000:.1f} K"
        return str(value)

    def build_content(self):
        # Lấy dữ liệu thống kê
        total_books = self.sach_service.count_books()
        total_employees = self.nhanvien_service.get_total_employee()
        low_stock_count = self.sach_service.count_low_stock_books()
        out_of_stock_count = self.sach_service.count_out_of_stock_books()
        total_stock_value = self.sach_service.get_total_stock_value()
        imports_this_month = self.phieunhap_service.count_current_month()
        exports_this_month = self.phieuxuat_service.count_current_month()
        total_suppliers = self.nhacungcap_service.count_all()
        total_distributors = self.nhaphanphoi_service.count_all()
        cost_this_month = self.phieunhap_service.get_current_month_cost()
        revenue_this_month = self.phieuxuat_service.get_current_month_revenue()

        # Lấy dữ liệu cho biểu đồ
        current_year = datetime.date.today().year
        import_stats = self.phieunhap_service.get_monthly_statistics(current_year)
        export_stats = self.phieuxuat_service.get_monthly_statistics(current_year)
        category_stats = self.sach_service.get_category_statistics()
        top_suppliers = self.phieunhap_service.get_top_suppliers(5)
        top_distributors = self.nhaphanphoi_service.get_top_distributors_by_orders(5)



        # Tạo các thẻ dashboard
        card_total_books = DashboardCard(
            title="Tổng đầu sách",
            value=str(total_books),
            icon=ft.Icon(ft.Icons.BOOK_ROUNDED, color=ft.Colors.WHITE, size=28),
            color="#A94F8B",
            on_click=lambda e: self.change_page(BooksPage) if self.change_page else None
        )

        card_total_employees = DashboardCard(
            title="Tổng nhân viên",
            value=str(total_employees),
            icon=ft.Icon(ft.Icons.GROUP_ROUNDED, color=ft.Colors.WHITE, size=28),
            color="#5D5FEF",
            on_click=lambda e: self.change_page(EmployeesPage) if self.change_page else None
        )

        card_low_stock = DashboardCard(
            title="Sách sắp hết",
            value=str(low_stock_count),
            icon=ft.Icon(ft.Icons.WARNING_ROUNDED, color=ft.Colors.WHITE, size=28),
            color="#F4A261",
            on_click=lambda e: self.change_page(BooksPage, initial_filter="low_stock") if self.change_page else None
        )

        card_out_of_stock = DashboardCard(
            title="Sách đã hết hàng",
            value=str(out_of_stock_count),
            icon=ft.Icon(ft.Icons.BOOKMARK_REMOVE_ROUNDED, color=ft.Colors.WHITE, size=28),
            color="#B53471", # Màu đỏ sẫm
            on_click=lambda e: self.change_page(BooksPage, initial_filter="out_of_stock") if self.change_page else None
        )


        card_total_value = DashboardCard(
            title="Tổng giá trị kho",
            value=self._format_currency(total_stock_value),
            icon=ft.Icon(ft.Icons.MONETIZATION_ON_ROUNDED, color=ft.Colors.WHITE, size=28),
            color="#2A9D8F",
        )

        card_total_suppliers = DashboardCard(
            title="Tổng nhà cung cấp",
            value=str(total_suppliers),
            icon=ft.Icon(ft.Icons.FACTORY_ROUNDED, color=ft.Colors.WHITE, size=28),
            color="#6D5A72",
            on_click=lambda e: self.change_page(SuppliersPage) if self.change_page else None
        )

        card_total_distributors = DashboardCard(
            title="Tổng nhà phân phối",
            value=str(total_distributors),
            icon=ft.Icon(ft.Icons.STORE_ROUNDED, color=ft.Colors.WHITE, size=28),
            color="#C08261",
            on_click=lambda e: self.change_page(DistributorsPage) if self.change_page else None
        )

        card_imports_month = DashboardCard(
            title="Phiếu nhập tháng này",
            value=str(imports_this_month),
            icon=ft.Icon(ft.Icons.INPUT_ROUNDED, color=ft.Colors.WHITE, size=28),
            color="#E76F51",
            on_click=lambda e: self.change_page(ImportReceiptPage) if self.change_page else None
        )

        card_exports_month = DashboardCard(
            title="Phiếu xuất tháng này",
            value=str(exports_this_month),
            icon=ft.Icon(ft.Icons.OUTPUT_ROUNDED, color=ft.Colors.WHITE, size=28),
            color="#264653",
            on_click=lambda e: self.change_page(ExportReceiptPage) if self.change_page else None
        )

        card_cost_month = DashboardCard(
            title="Chi phí nhập tháng này",
            value=self._format_currency(cost_this_month),
            icon=ft.Icon(ft.Icons.ARROW_DOWNWARD_ROUNDED, color=ft.Colors.WHITE, size=28),
            color="#E76F51",
            on_click=lambda e: self.change_page(ImportReceiptPage) if self.change_page else None
        )

        card_revenue_month = DashboardCard(
            title="Doanh thu xuất tháng này",
            value=self._format_currency(revenue_this_month),
            icon=ft.Icon(ft.Icons.ARROW_UPWARD_ROUNDED, color=ft.Colors.WHITE, size=28),
            color="#264653",
            on_click=lambda e: self.change_page(ExportReceiptPage) if self.change_page else None
        )

        card_imports_month.width = 260
        card_exports_month.width = 260
        card_cost_month.width = 260
        card_revenue_month.width = 260

        return ft.Column(
            [
                ft.Text("TỔNG QUAN KHO SÁCH", size=18, weight=ft.FontWeight.BOLD, color="#A94F8B"),
                ft.Row(
                    [card_total_books, card_total_employees, card_low_stock, card_out_of_stock, card_total_value, card_total_suppliers, card_total_distributors],
                    spacing=20,
                    wrap=True, # Tự động xuống hàng nếu không đủ chỗ
                ),
                ft.Divider(height=25, color="transparent"),
                
                ft.Text("HOẠT ĐỘNG TRONG THÁNG", size=18, weight=ft.FontWeight.BOLD, color="#A94F8B"),
                ft.Column(
                    [
                        ft.Row(
                            [card_imports_month, card_exports_month], spacing=20, wrap=True
                        ),
                        ft.Row(
                            [card_cost_month, card_revenue_month], spacing=20, wrap=True
                        )
                    ],
                    spacing=20
                ),
                ft.Divider(height=30, color="transparent"),
                ft.Text("PHÂN TÍCH CHI TIẾT", size=18, weight=ft.FontWeight.BOLD, color="#A94F8B"),
                # --- Hàng biểu đồ mới ---
                ft.Row(
                    [
                        CategoryPieChart(data=category_stats),
                        TopPartnersChart(top_suppliers=top_suppliers, top_distributors=top_distributors)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER, spacing=0, wrap=True
                ),
                ft.Divider(height=15, color="transparent"),
                # --- Biểu đồ ---
                ft.Row(
                    [MonthlyChart(import_data=import_stats, export_data=export_stats)],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
            ],
            spacing=10,
            expand=True,
            scroll=ft.ScrollMode.AUTO
        )
