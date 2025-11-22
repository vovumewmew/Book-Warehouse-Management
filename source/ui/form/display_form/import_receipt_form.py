# source/ui/form/display_form/import_receipt_form.py
import flet as ft
from config.db_connection import DatabaseConnection
from source.dao.PhieuNhapSachDAO import PhieuNhapSachDAO
from source.services.PhieuNhapSachService import PhieuNhapSachService
from source.dao.ChiTietPhieuNhapDAO import ChiTietPhieuNhapDAO
from source.services.ChiTietPhieuNhapService import ChiTietPhieuNhapService
from source.dao.SachDAO import SachDAO
from source.services.SachService import SachService
from source.ui.form.display_form.display_form_base import DisplayFormBase
from source.ui.button.edit_button.edit_import_receipt_button import EditImportReceiptButton
from source.ui.button.delete_button.delete_import_receipt_button import DeleteImportReceiptButton
from util.pdf_generator import PDFGenerator

class ImportReceiptForm(DisplayFormBase):
    def __init__(self, receipt, page=None, on_close=None, **kwargs):
        self.page = page
        self._receipt = receipt
        self.on_close = on_close # Lưu lại callback on_close

        # --- File Picker để lưu PDF ---
        self.file_picker = ft.FilePicker(on_result=self.save_pdf_result)
        if self.page:
            self.page.overlay.append(self.file_picker)
            self.page.update()

        # --- PDF Generator ---
        self.pdf_generator = PDFGenerator()

        # --- Khởi tạo DAO & Service ---
        db_conn = DatabaseConnection()
        phieunhap_dao = PhieuNhapSachDAO(db_conn)
        chitiet_dao = ChiTietPhieuNhapDAO(db_conn)
        sach_dao = SachDAO(db_conn)
        self.phieunhap_service = PhieuNhapSachService(phieunhap_dao)
        self.chitiet_service = ChiTietPhieuNhapService(chitiet_dao)
        self.sach_service = SachService(sach_dao)
        self.phieunhap_service.set_chitiet_service(self.chitiet_service)
        self.phieunhap_service.set_sach_service(self.sach_service)

        # --- Tính toán lại tổng số lượng và tổng tiền từ chi tiết ---
        total_quantity = sum(detail.SoLuong for detail in self._receipt.Danhsachchitietnhap)
        total_price = sum(detail.ThanhTien for detail in self._receipt.Danhsachchitietnhap)

        # --- Mapping label → attribute ---
        fields = {
            "Mã phiếu": self._receipt.ID_PhieuNhap,
            "Ngày nhập": self._receipt.NgayNhap.strftime("%d/%m/%Y"),
            "Nhân viên": self._receipt.TenNhanVien,
            "Nguồn nhập": self._receipt.TenNguonNhap,
            "Tổng số lượng": f"{total_quantity} cuốn",
            "Tổng tiền": f"{total_price:,.0f} VNĐ",
        }

        # --- Gọi super().__init__() ---
        super().__init__(
            title=f"Chi tiết Phiếu Nhập",
            fields=fields,
            width=450,
            height=600, # Tăng chiều cao để chứa bảng
            on_close=on_close
        )

    def build_form(self):
        container = super().build_form()
        close_button = container.content.controls.pop()

        # --- Tạo bảng chi tiết ---
        details_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Tên Sách", weight="bold")),
                ft.DataColumn(ft.Text("SL", weight="bold"), numeric=True),
                ft.DataColumn(ft.Text("Đơn Giá", weight="bold"), numeric=True),
                ft.DataColumn(ft.Text("Thành Tiền", weight="bold"), numeric=True),
            ],
            rows=[],
            column_spacing=20,
            border=ft.border.all(1, "#E5C4EC"),
            border_radius=ft.border_radius.all(8),
            heading_row_color=ft.Colors.with_opacity(0.1, "#A94F8B"),
        )

        for detail in self._receipt.Danhsachchitietnhap:
            details_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(detail.sach.TenSach, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS)),
                    ft.DataCell(ft.Text(str(detail.SoLuong))),
                    ft.DataCell(ft.Text(f"{detail.DonGia:,.0f}")),
                    ft.DataCell(ft.Text(f"{detail.ThanhTien:,.0f}")),
                ])
            )

        # --- Nút Sửa ---
        edit_button = EditImportReceiptButton(page=self.page, receipt=self._receipt, on_edit_callback=self.on_close)

        # --- Nút Xóa mới ---
        # on_deleted sẽ gọi hàm on_close của form, hàm này được truyền từ page vào
        # để tải lại bảng dữ liệu.
        delete_button = DeleteImportReceiptButton(page=self.page, receipt=self._receipt, service=self.phieunhap_service, on_deleted=self.on_close)

        # --- Nút In PDF ---
        print_pdf_button = ft.ElevatedButton(
            "In PDF",
            icon=ft.Icons.PICTURE_AS_PDF,
            on_click=lambda _: self.file_picker.save_file(dialog_title="Lưu file PDF", file_name=f"PhieuNhap_{self._receipt.ID_PhieuNhap}.pdf"),
            color=ft.Colors.WHITE, bgcolor="#264653"
        )

        # --- Thêm bảng chi tiết vào layout ---
        # Tìm vị trí của divider cuối cùng để chèn bảng vào trước nó
        divider_index = -1
        for i, ctrl in enumerate(container.content.controls):
            if isinstance(ctrl, ft.Divider):
                divider_index = i
        
        if divider_index != -1:
            container.content.controls.insert(divider_index, ft.Container(details_table, expand=True))

        # --- Thêm các nút vào layout ---
        buttons_row = ft.Row(
            controls=[print_pdf_button, edit_button, delete_button, close_button],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        )
        container.content.controls.append(buttons_row)
        return container

    def save_pdf_result(self, e: ft.FilePickerResultEvent):
        if e.path:
            if self.pdf_generator.generate_import_receipt_pdf(self._receipt, e.path):
                self.show_snackbar(f"Đã lưu file PDF thành công tại: {e.path}")
            else:
                self.show_snackbar("Lỗi: Không thể tạo file PDF.")

    def show_snackbar(self, message: str):
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message))
        self.page.snack_bar.open = True
        self.page.update()