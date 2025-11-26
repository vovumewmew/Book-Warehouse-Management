# source/ui/pages/books_page.py
import flet as ft
from config.db_connection import DatabaseConnection
from source.ui.pages.base_page import BasePage
from source.ui.Table.books_table import BookTable
from source.dao.SachDAO import SachDAO
from source.services.SachService import SachService
from source.ui.button.add_button.add_new_book import AddNewBook
from source.ui.search_bar.search_bar_book import SearchBarBook
from util.excel_generator import ExcelGenerator
class BooksPage(BasePage):
    def __init__(self, page: ft.Page, change_page_func, **kwargs):
        self.page = page  # đảm bảo page luôn có giá trị
        self.change_page = change_page_func
        self.initial_filter = kwargs.get("initial_filter")

        # --- Khởi tạo container cho sách TRƯỚC ---
        self.books_container = ft.Column(spacing=10, expand=True, scroll=ft.ScrollMode.AUTO)

        # --- File Picker để lưu Excel ---
        self.file_picker = ft.FilePicker(on_result=self.save_excel_result)
        if self.page:
            self.page.overlay.append(self.file_picker)

        self.excel_generator = ExcelGenerator()

        # --- Khởi tạo Service ---
        db = DatabaseConnection()
        sach_dao = SachDAO(db)
        self.sach_service = SachService(sach_dao)

        # --- Xây dựng header và content chính ---
        self.main_header = self.build_header()
        self.main_content = self.build_main_content()
        
        # --- Khởi tạo BasePage sau khi đã có header và content ---
        super().__init__(
            "Sách",
            header_action=self.main_header
        )
        self.content_body = self.main_content

        # Tải dữ liệu ban đầu SAU KHI mọi thứ đã được xây dựng
        self.load_initial_books()

    def build_header(self):
        """Xây dựng header cho trang sách chính."""
        # --- Nút thêm sách ---
        add_button = AddNewBook(page=self.page)
        
        # --- Thanh tìm kiếm ---
        search_bar = SearchBarBook(
            page=self.page, 
            books_container=self.books_container, 
            width=300
        )

        # --- Nút "Xem sách đã xóa" ---
        trash_button = ft.IconButton(
            icon=ft.Icons.DELETE_SWEEP_ROUNDED,
            icon_color=ft.Colors.WHITE,
            bgcolor="#A94F8B",
            width=40,
            height=40,
            tooltip="Xem sách đã xóa",
            on_click=self.show_unavailable_books,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        )

        # --- Nút refresh ---
        refresh_button = ft.IconButton(
            icon=ft.Icons.REFRESH,
            icon_color=ft.Colors.WHITE,
            bgcolor="#A94F8B",
            width=40,
            height=40,
            tooltip="Làm mới",
            on_click=self.reload_books,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        )

        # --- Nút Xuất Excel ---
        export_excel_button = ft.IconButton(
            icon=ft.Icons.TABLE_VIEW_ROUNDED,
            icon_color=ft.Colors.WHITE,
            bgcolor="#2A9D8F", # Màu xanh lá
            width=40,
            height=40,
            tooltip="Xuất ra file Excel",
            on_click=self.export_to_excel,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        )


        return ft.Row([trash_button, add_button, refresh_button, export_excel_button, search_bar], spacing=10)

    def load_initial_books(self):
        """Tải sách lần đầu, có áp dụng bộ lọc nếu được truyền vào."""
        books = []
        if self.initial_filter == "low_stock":
            books = self.sach_service.get_low_stock_books()
            # Đặt lại bộ lọc để lần làm mới sau đó sẽ tải tất cả sách
            self.initial_filter = None
        elif self.initial_filter == "out_of_stock":
            books = [book for book in self.sach_service.get_all() if book.SoLuong == 0]
            self.initial_filter = None
        else:
            books = self.sach_service.get_all()

        self.books_container.controls.clear()
        # Bỏ columns=3 để nó tự động điều chỉnh
        self.books_container.controls.append(BookTable(books, page=self.page))
        if self.page:
            self.page.update()

    def build_main_content(self):
        """Xây dựng nội dung chính cho trang sách (sách khả dụng)."""
        # KHÔNG tải dữ liệu ở đây nữa, chỉ xây dựng cấu trúc layout
        return ft.Container(
            expand=True,
            content=ft.Column(
                [
                    ft.Divider(height=20, color="transparent"),
                    self.books_container
                ],
                spacing=10,
                expand=True,
                scroll=ft.ScrollMode.AUTO
            )
        )

    def reload_books(self, e=None):
        """Tải lại toàn bộ danh sách sách (dùng cho nút refresh)."""
        # Luôn tạo service mới để lấy dữ liệu mới nhất từ DB
        # sau các thao tác thêm/sửa/xóa từ các form khác.
        db = DatabaseConnection()
        sach_dao = SachDAO(db)
        sach_service = SachService(sach_dao)
        books = sach_service.get_all()

        self.books_container.controls.clear()
        page_to_update = getattr(e.control, "page", self.page) if e else self.page
        self.books_container.controls.append(BookTable(books, page=page_to_update))
        if page_to_update:
            page_to_update.update()

    def show_unavailable_books(self, e):
        """Hiển thị trang sách không khả dụng."""
        from source.ui.pages.unavailable_page.unavailable_book_page import UnavailableBooksPage
        # Yêu cầu MainFrame thay đổi trang sang UnavailableBooksPage
        self.change_page(UnavailableBooksPage)
    
    def build_content(self):
        return self.main_content

    def export_to_excel(self, e):
        """Mở hộp thoại lưu file để xuất Excel."""
        self.file_picker.save_file(
            dialog_title="Lưu file Excel",
            file_name="DanhSachSach.xlsx",
            allowed_extensions=["xlsx"]
        )

    def save_excel_result(self, e: ft.FilePickerResultEvent):
        """Callback sau khi người dùng chọn nơi lưu file."""
        if e.path:
            page = e.page # Lấy page từ sự kiện để đảm bảo an toàn
            all_books = self.sach_service.get_all() # Lấy toàn bộ sách để xuất
            if self.excel_generator.generate_books_excel(all_books, e.path):
                page.snack_bar = ft.SnackBar(content=ft.Text(f"Đã lưu file Excel thành công!"), bgcolor="#2A9D8F")
            else:
                page.snack_bar = ft.SnackBar(content=ft.Text("Lỗi: Không thể tạo file Excel."), bgcolor=ft.colors.ERROR)
            page.snack_bar.open = True
            page.update()