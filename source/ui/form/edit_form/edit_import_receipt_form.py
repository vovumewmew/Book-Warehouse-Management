import flet as ft
import datetime
from decimal import Decimal

from config.db_connection import DatabaseConnection
from source.dao.NhanVienDAO import NhanVienDAO
from source.dao.NguonNhapSachDAO import NguonNhapSachDAO
from source.dao.SachDAO import SachDAO
from source.dao.PhieuNhapSachDAO import PhieuNhapSachDAO
from source.dao.ChiTietPhieuNhapDAO import ChiTietPhieuNhapDAO
from source.services.NhanVienService import NhanVienService
from source.services.NguonNhapSachService import NguonNhapSachService
from source.services.SachService import SachService
from source.services.PhieuNhapSachService import PhieuNhapSachService
from source.services.ChiTietPhieuNhapService import ChiTietPhieuNhapService
from source.models.PhieuNhapSach import PhieuNhapSach

class EditImportReceiptForm(ft.Container):
    def __init__(self, page: ft.Page, receipt_data, on_close=None):
        super().__init__()
        self.page = page
        self._receipt = receipt_data
        self.on_close_callback = on_close

        # --- Khởi tạo Services ---
        db = DatabaseConnection()
        self.nhanvien_service = NhanVienService(NhanVienDAO(db))
        self.nguonnhap_service = NguonNhapSachService(NguonNhapSachDAO(db))
        self.sach_service = SachService(SachDAO(db))
        self.phieunhap_service = PhieuNhapSachService(PhieuNhapSachDAO(db))
        self.chitiet_service = ChiTietPhieuNhapService(ChiTietPhieuNhapDAO(db))
        self.phieunhap_service.set_chitiet_service(self.chitiet_service)
        self.phieunhap_service.set_sach_service(self.sach_service)

        # --- Lấy dữ liệu cho dropdowns ---
        self.available_employees = self.nhanvien_service.get_employee_by_role("Nhân viên nhập sách")
        self.available_suppliers = self.nguonnhap_service.get_all()

        # --- Controls cho thông tin chung ---
        self.id_field = ft.TextField(label="Mã phiếu", read_only=True, expand=True)
        self.date_field = ft.TextField(label="Ngày nhập", hint_text="dd/mm/yyyy", expand=True, on_blur=self._validate_date)
        self.employee_dropdown = ft.Dropdown(
            label="Nhân viên nhập",
            options=[ft.dropdown.Option(nv.ID_NhanVien, nv.HoTen) for nv in self.available_employees],
        )
        self.supplier_dropdown = ft.Dropdown(
            label="Nguồn nhập",
            options=[ft.dropdown.Option(ncc.ID_NguonNhap, ncc.TenCoSo) for ncc in self.available_suppliers]
        )
        self.total_quantity_field = ft.TextField(label="Tổng số lượng", read_only=True)
        self.total_price_field = ft.TextField(label="Tổng tiền", read_only=True)

        self.details_column = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=10)

        # --- Buttons ---
        self.cancel_button = ft.ElevatedButton("Hủy", on_click=self._handle_close, bgcolor="#A94F8B", color=ft.Colors.WHITE)
        self.save_button = ft.ElevatedButton("Lưu", on_click=self._save_receipt, bgcolor="#A94F8B", color=ft.Colors.WHITE)

        # --- Build ---
        self.content = self.build_form()
        self._populate_data()
        
        # Gán sự kiện on_focus để xóa lỗi
        self.employee_dropdown.on_focus = self._clear_error
        self.date_field.on_focus = self._clear_error
        self.supplier_dropdown.on_focus = self._clear_error

    def _clear_error(self, e):
        e.control.error_text = None
        self.page.update()

    def _validate_date(self, e):
        try:
            input_date = datetime.datetime.strptime(self.date_field.value, "%d/%m/%Y").date()
            if input_date > datetime.date.today():
                self.date_field.error_text = "Ngày nhập không được lớn hơn ngày hiện tại"
            else:
                self.date_field.error_text = None
        except ValueError:
            self.date_field.error_text = "Định dạng ngày phải là dd/mm/yyyy"
        self.page.update()

    def build_form(self):
        return ft.Container(
            width=800,
            padding=20,
            bgcolor="#FFF8FB",
            border_radius=ft.border_radius.all(16),
            border=ft.border.all(2, "#E5C4EC"),
            content=ft.Column(
                [
                    ft.Text("Sửa Phiếu Nhập", size=20, weight="bold", color="#A94F8B"),
                    ft.Divider(height=10, color="#A94F8B"),
                    ft.Row(
                        [
                            ft.Column([self.id_field, self.employee_dropdown, self.supplier_dropdown], spacing=10, expand=True),
                            ft.Column([self.date_field, self.total_quantity_field, self.total_price_field], spacing=10, expand=True),
                        ],
                        spacing=20
                    ),
                    ft.Divider(height=15, color="transparent"),
                    ft.Text("Chi tiết phiếu nhập (không thể sửa)", weight="bold", color="#A94F8B"),
                    ft.Container(self.details_column, border=ft.border.all(1, "#E5C4EC"), border_radius=10, padding=10, height=250),
                    ft.Row(
                        [
                            ft.Row(
                                [self.cancel_button, self.save_button],
                                alignment=ft.MainAxisAlignment.END,
                            )
                        ],
                        alignment=ft.MainAxisAlignment.END
                    ),
                ],
                scroll=ft.ScrollMode.AUTO,
            )
        )

    def _populate_data(self):
        """Điền dữ liệu có sẵn vào form."""
        self.id_field.value = self._receipt.ID_PhieuNhap
        self.date_field.value = self._receipt.NgayNhap.strftime("%d/%m/%Y")
        self.employee_dropdown.value = self._receipt.nhan_vien_nhap.ID_NhanVien
        self.supplier_dropdown.value = self._receipt.nguon_nhap.ID_NguonNhap
        self.total_quantity_field.value = str(self._receipt.TongSoLuong)
        self.total_price_field.value = f"{self._receipt.TongTien:,.0f} VNĐ"

        for detail in self._receipt.Danhsachchitietnhap:
            book_dropdown = ft.Dropdown(
                value=detail.sach.ID_Sach,
                options=[ft.dropdown.Option(detail.sach.ID_Sach, detail.sach.TenSach)],
                disabled=True, width=290
            )
            quantity_field = ft.TextField(
                value=str(detail.SoLuong), read_only=True, width=120, text_align=ft.TextAlign.CENTER
            )
            price_field = ft.TextField(
                value=f"{detail.DonGia:,.0f}", read_only=True, width=150, text_align=ft.TextAlign.RIGHT
            )
            
            row = ft.Row([book_dropdown, quantity_field, price_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            self.details_column.controls.append(row)

    def _save_receipt(self, e):
        self.clear_all_errors()
        try:
            ngay_nhap = self.date_field.value
            id_nhanvien = self.employee_dropdown.value
            id_nguonnhap = self.supplier_dropdown.value

            if not ngay_nhap:
                self.date_field.error_text = "Ngày nhập không được trống"
                self.page.update()
                return
            
            if not id_nhanvien:
                self.employee_dropdown.error_text = "Vui lòng chọn nhân viên"
                self.page.update()
                return
            
            if not id_nguonnhap:
                self.supplier_dropdown.error_text = "Vui lòng chọn nguồn nhập"
                self.page.update()
                return
            
            nhan_vien_obj = next((nv for nv in self.available_employees if nv.ID_NhanVien == id_nhanvien), None)
            nguon_nhap_obj = next((ncc for ncc in self.available_suppliers if ncc.ID_NguonNhap == id_nguonnhap), None)
            
            # Tạo đối tượng mới để gửi đi, chỉ chứa các thông tin cần cập nhật
            phieu_nhap_update = PhieuNhapSach(
                ID_PhieuNhap=self._receipt.ID_PhieuNhap,
                NgayNhap=ngay_nhap,
                TongSoLuong=self._receipt.TongSoLuong, # Giữ nguyên
                TongTien=self._receipt.TongTien, # Giữ nguyên
                nhan_vien_nhap=nhan_vien_obj,
                nguon_nhap=nguon_nhap_obj
            )

            update_result = self.phieunhap_service.update(phieu_nhap_update)
            
            if update_result:
                self._show_snackbar("Cập nhật phiếu nhập thành công!")
                self._handle_close(e)
            else:
                self._show_error("Cập nhật phiếu nhập thất bại. Không có thay đổi nào được ghi nhận.")

        except ValueError as ve:
            msg = str(ve)
            if "Ngày nhập" in msg: self.date_field.error_text = msg
            elif "nhân viên" in msg: self.employee_dropdown.error_text = msg
            elif "nguồn nhập" in msg: self.supplier_dropdown.error_text = msg
            else: self._show_error(f"Lỗi dữ liệu: {msg}")
            self.page.update()

        except Exception as ex:
            self._show_error(f"Đã xảy ra lỗi không mong muốn: {ex}")

    def _handle_close(self, e):
        if self.page and self.page.overlay and self in self.page.overlay:
            self.page.overlay.remove(self)
            self.page.update()
        if self.on_close_callback:
            self.on_close_callback()

    def clear_all_errors(self):
        self.date_field.error_text = None
        self.employee_dropdown.error_text = None
        self.supplier_dropdown.error_text = None
        self.page.update()

    def _show_error(self, message: str):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.RED_400
        )
        self.page.snack_bar.open = True
        self.page.update()

    def _show_snackbar(self, message: str):
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message))
        self.page.snack_bar.open = True
        self.page.update()