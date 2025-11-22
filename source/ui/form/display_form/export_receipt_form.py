# source/ui/form/display_form/export_receipt_form.py
import flet as ft
from config.db_connection import DatabaseConnection
from source.dao.PhieuXuatSachDAO import PhieuXuatSachDAO
from source.services.PhieuXuatSachService import PhieuXuatSachService
from source.dao.ChiTietPhieuXuatDAO import ChiTietPhieuXuatDAO
from source.services.ChiTietPhieuXuatService import ChiTietPhieuXuatService
from source.dao.SachDAO import SachDAO
from source.services.SachService import SachService
from source.ui.form.display_form.display_form_base import DisplayFormBase
from source.ui.button.edit_button.edit_export_receipt_button import EditExportReceiptButton
from source.ui.button.delete_button.delete_export_receipt_button import DeleteExportReceiptButton
from util.pdf_generator import PDFGenerator

class ExportReceiptForm(DisplayFormBase):
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
        phieuxuat_dao = PhieuXuatSachDAO(db_conn)
        chitiet_dao = ChiTietPhieuXuatDAO(db_conn)
        sach_dao = SachDAO(db_conn)
        self.phieuxuat_service = PhieuXuatSachService(phieuxuat_dao)
        self.chitiet_service = ChiTietPhieuXuatService(chitiet_dao)
        self.sach_service = SachService(sach_dao)
        self.phieuxuat_service.set_chitiet_service(self.chitiet_service)
        self.phieuxuat_service.set_sach_service(self.sach_service)

        # --- Tính toán lại tổng số lượng và tổng tiền từ chi tiết ---
        total_quantity = sum(detail.SoLuong for detail in self._receipt.Danhsachchitietxuat)
        total_price = sum(detail.ThanhTien for detail in self._receipt.Danhsachchitietxuat)

        # --- Mapping label → attribute ---
        fields = {
            "Mã phiếu": self._receipt.ID_PhieuXuat,
            "Ngày xuất": self._receipt.NgayXuat.strftime("%d/%m/%Y"),
            "Nhân viên": self._receipt.TenNhanVien,
            "Nhà phân phối": self._receipt.TenNhaPhanPhoi,
            "Tổng số lượng": f"{total_quantity} cuốn",
            "Tổng tiền": f"{total_price:,.0f} VNĐ",
        }

        # --- Gọi super().__init__() ---
        super().__init__(
            title=f"Chi tiết Phiếu Xuất",
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

        for detail in self._receipt.Danhsachchitietxuat:
            details_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(detail.sach.TenSach, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS)),
                    ft.DataCell(ft.Text(str(detail.SoLuong))),
                    ft.DataCell(ft.Text(f"{detail.DonGia:,.0f}")),
                    ft.DataCell(ft.Text(f"{detail.ThanhTien:,.0f}")),
                ])
            )

        # --- Nút Sửa ---
        edit_button = EditExportReceiptButton(page=self.page, receipt=self._receipt, on_edit_callback=self.on_close)

        # --- Nút Xóa mới ---
        # on_deleted sẽ gọi hàm on_close của form để tải lại bảng dữ liệu.
        delete_button = DeleteExportReceiptButton(page=self.page, receipt=self._receipt, service=self.phieuxuat_service, on_deleted=self.on_close)

        # --- Nút In PDF ---
        print_pdf_button = ft.ElevatedButton(
            "In PDF",
            icon=ft.Icons.PICTURE_AS_PDF,
            on_click=lambda _: self.file_picker.save_file(dialog_title="Lưu file PDF", file_name=f"PhieuXuat_{self._receipt.ID_PhieuXuat}.pdf"),
            color=ft.Colors.WHITE, bgcolor="#264653"
        )

        # --- Thêm bảng chi tiết vào layout ---
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
            if self.pdf_generator.generate_export_receipt_pdf(self._receipt, e.path):
                self.show_snackbar(f"Đã lưu file PDF thành công tại: {e.path}")
            else:
                self.show_snackbar("Lỗi: Không thể tạo file PDF.")

    def show_snackbar(self, message: str):
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message))
        self.page.snack_bar.open = True
        self.page.update()