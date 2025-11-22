import flet as ft

from source.ui.sidebar.sidebar_button_home import SidebarButtonHome
from source.ui.sidebar.sidebar_button_books import SidebarButtonBooks
from source.ui.sidebar.sidebar_button_employees import SidebarButtonEmployees
from source.ui.sidebar.sidebar_button_contributors import SidebarButtonContributors
from source.ui.sidebar.sidebar_button_suppliers import SidebarButtonSuppliers
from source.ui.sidebar.sidebar_button_import_receipt import SidebarButtonImportReceipt
from source.ui.sidebar.sidebar_button_export_receipt import SidebarButtonExportReceipt

from source.ui.pages.available_page.home_page import HomePage
from source.ui.pages.available_page.books_page import BooksPage
from source.ui.pages.available_page.employees_page import EmployeesPage
from source.ui.pages.available_page.distributor_page import DistributorsPage
from source.ui.pages.available_page.suppliers_page import SuppliersPage
from source.ui.pages.available_page.export_receipt_page import ExportReceiptPage
from source.ui.pages.available_page.import_receipt_page import ImportReceiptPage
from source.ui.pages.unavailable_page.unavailable_book_page import UnavailableBooksPage

def main(page: ft.Page):
    page.title = "Rounded Page"
    page.window_width = 1600
    page.window_height = 800
    page.bgcolor = "#FBEFF3"

    # --- Quản lý trạng thái nút chọn ---
    selected_button = {"current": None}

    # --- Khai báo các nút sidebar trước để có thể tham chiếu ---
    btn_home = SidebarButtonHome(on_click=lambda btn: on_button_click(btn))
    btn_books = SidebarButtonBooks(on_click=lambda btn: on_button_click(btn))
    btn_employees = SidebarButtonEmployees(on_click=lambda btn: on_button_click(btn))
    btn_distributors = SidebarButtonContributors(on_click=lambda btn: on_button_click(btn))
    btn_suppliers = SidebarButtonSuppliers(on_click=lambda btn: on_button_click(btn))
    btn_import_receipt = SidebarButtonImportReceipt(on_click=lambda btn: on_button_click(btn))
    btn_export_receipt = SidebarButtonExportReceipt(on_click=lambda btn: on_button_click(btn))

    # --- "Bản đồ" liên kết Page và Nút Sidebar ---
    page_to_button_map = {
        HomePage: btn_home,
        BooksPage: btn_books,
        EmployeesPage: btn_employees,
        DistributorsPage: btn_distributors,
        SuppliersPage: btn_suppliers,
        ImportReceiptPage: btn_import_receipt,
        ExportReceiptPage: btn_export_receipt,
    }

    # --- Container trung gian để hiển thị page ---
    MainFrame = ft.Container(expand=True, key="main_frame")

    # --- Hàm quản lý việc chọn nút ---
    def set_selected_button(button_to_select):
        # Bỏ chọn nút cũ
        if selected_button["current"] and selected_button["current"] != button_to_select:
            selected_button["current"].set_selected(False)
        
        # Chọn nút mới
        if button_to_select:
            button_to_select.set_selected(True)
            selected_button["current"] = button_to_select
        page.update()

    # --- Hàm quản lý việc thay đổi trang ---
    def change_page(target_page_class, **kwargs):
        """Hàm trung tâm để thay đổi nội dung của MainFrame."""
        if not target_page_class:
            return
        
        # Đồng bộ hóa sidebar
        button_to_select = page_to_button_map.get(target_page_class)
        set_selected_button(button_to_select)

        # Thêm các tham số cần thiết vào kwargs
        kwargs.update({"page": page, "change_page_func": change_page, "sidebar_button": selected_button["current"]})
        MainFrame.content = target_page_class(**kwargs).build()
        page.update()

    # --- Hàm click nút sidebar ---
    def on_button_click(button):
        # Tìm trang tương ứng với nút được nhấn
        target_page = next((page_class for page_class, btn in page_to_button_map.items() if btn == button), None)
        change_page(target_page)


    # === Sidebar trắng bên trái ===
    sidebar = ft.Container(
        width=200,
        height=560,
        border_radius=ft.border_radius.all(18),
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_center,
            end=ft.alignment.bottom_center,
            colors=["#FFFFFF", "#FAFAFA", "#F7F5F8"]
        ),
        shadow=ft.BoxShadow(
            blur_radius=25,
            spread_radius=-8,
            color="rgba(0,0,0,0.10)",
            offset=(5, 10)
        ),
        margin=ft.margin.only(left=20),
        padding=20,
        content=ft.Column(
            [
                ft.Text("📚 Book Manager", size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(height=10, color="transparent"),
                btn_home,
                btn_books,
                btn_employees,
                btn_distributors,
                btn_suppliers,
                btn_import_receipt,
                btn_export_receipt,
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            spacing=5,
        )
    )

    # === Main container (sidebar + MainFrame) ===
    main_container = ft.Container(
        width=1200,
        height=600,
        bgcolor="#FFEAF3",
        border_radius=ft.border_radius.all(18),
        padding=20,
        content=ft.Row(
            [
                sidebar,
                ft.VerticalDivider(width=20, color="transparent"),
                MainFrame  # gắn container trung gian MainFrame
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

    # === Thêm main container vào page ===
    page.add(
        ft.Row(
            [main_container],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

    # --- Gán mặc định Trang chủ SAU KHI đã add mọi thứ vào page ---
    set_selected_button(btn_home)
    change_page(HomePage) # hiển thị page mặc định

ft.app(target=main, view=ft.AppView.FLET_APP)
