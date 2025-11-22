import flet as ft
import datetime
from decimal import Decimal

from config.db_connection import DatabaseConnection
from source.dao.NhanVienDAO import NhanVienDAO
from source.dao.NhaPhanPhoiDAO import NhaPhanPhoiDAO
from source.dao.SachDAO import SachDAO
from source.dao.PhieuXuatSachDAO import PhieuXuatSachDAO
from source.dao.ChiTietPhieuXuatDAO import ChiTietPhieuXuatDAO
from source.services.NhanVienService import NhanVienService
from source.services.NhaPhanPhoiService import NhaPhanPhoiService
from source.services.SachService import SachService
from source.services.PhieuXuatSachService import PhieuXuatSachService
from source.services.ChiTietPhieuXuatService import ChiTietPhieuXuatService
from source.models.PhieuXuatSach import PhieuXuatSach

class EditExportReceiptForm(ft.Container):
    def __init__(self, page: ft.Page, receipt_data, on_close=None):
        super().__init__()
        self.page = page
        self._receipt = receipt_data
        self.on_close_callback = on_close

        # --- Khởi tạo Services ---
        db = DatabaseConnection()
        self.nhanvien_service = NhanVienService(NhanVienDAO(db))
        self.nhaphanphoi_service = NhaPhanPhoiService(NhaPhanPhoiDAO(db))
        self.sach_service = SachService(SachDAO(db))
        self.phieuxuat_service = PhieuXuatSachService(PhieuXuatSachDAO(db))
        self.chitiet_service = ChiTietPhieuXuatService(ChiTietPhieuXuatDAO(db))
        self.phieuxuat_service.set_chitiet_service(self.chitiet_service)
        self.phieuxuat_service.set_sach_service(self.sach_service)

        # --- Lấy dữ liệu cho dropdowns ---
        self.available_employees = self.nhanvien_service.get_employee_by_role("Nhân viên xuất sách")
        self.available_distributors = self.nhaphanphoi_service.get_all()

        # --- Controls cho thông tin chung ---
        self.id_field = ft.TextField(label="Mã phiếu", read_only=True, expand=True)
        self.date_field = ft.TextField(label="Ngày xuất", hint_text="dd/mm/yyyy", expand=True, on_blur=self._validate_date)
        self.employee_dropdown = ft.Dropdown(
            label="Nhân viên xuất",
            options=[ft.dropdown.Option(nv.ID_NhanVien, nv.HoTen) for nv in self.available_employees],
        )
        self.distributor_dropdown = ft.Dropdown(
            label="Nhà phân phối",
            options=[ft.dropdown.Option(npp.ID_NguonXuat, npp.TenCoSo) for npp in self.available_distributors]
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
        
        self.employee_dropdown.on_focus = self._clear_error
        self.date_field.on_focus = self._clear_error
        self.distributor_dropdown.on_focus = self._clear_error

    def _clear_error(self, e):
        e.control.error_text = None
        self.page.update()

    def _validate_date(self, e):
        try:
            input_date = datetime.datetime.strptime(self.date_field.value, "%d/%m/%Y").date()
            if input_date > datetime.date.today():
                self.date_field.error_text = "Ngày xuất không được lớn hơn ngày hiện tại"
            else:
                self.date_field.error_text = None
        except ValueError:
            self.date_field.error_text = "Định dạng ngày phải là dd/mm/yyyy"
        self.page.update()

    def build_form(self):
        return ft.Container(
            width=800, padding=20, bgcolor="#FFF8FB", border_radius=16, border=ft.border.all(2, "#E5C4EC"),
            content=ft.Column(
                [
                    ft.Text("Sửa Phiếu Xuất", size=20, weight="bold", color="#A94F8B"),
                    ft.Divider(height=10, color="#A94F8B"),
                    ft.Row(
                        [
                            ft.Column([self.id_field, self.employee_dropdown, self.distributor_dropdown], spacing=10, expand=True),
                            ft.Column([self.date_field, self.total_quantity_field, self.total_price_field], spacing=10, expand=True),
                        ], spacing=20
                    ),
                    ft.Divider(height=15, color="transparent"),
                    ft.Text("Chi tiết phiếu xuất (không thể sửa)", weight="bold", color="#A94F8B"),
                    ft.Container(self.details_column, border=ft.border.all(1, "#E5C4EC"), border_radius=10, padding=10, height=250),
                    ft.Row([ft.Row([self.cancel_button, self.save_button], alignment=ft.MainAxisAlignment.END)], alignment=ft.MainAxisAlignment.END),
                ], scroll=ft.ScrollMode.AUTO
            )
        )

    def _populate_data(self):
        self.id_field.value = self._receipt.ID_PhieuXuat
        self.date_field.value = self._receipt.NgayXuat.strftime("%d/%m/%Y")
        self.employee_dropdown.value = self._receipt.nhan_vien_xuat.ID_NhanVien
        self.distributor_dropdown.value = self._receipt.nha_phan_phoi.ID_NguonXuat
        self.total_quantity_field.value = str(self._receipt.TongSoLuong)
        self.total_price_field.value = f"{self._receipt.TongTien:,.0f} VNĐ"

        for detail in self._receipt.Danhsachchitietxuat:
            book_dropdown = ft.Dropdown(value=detail.sach.ID_Sach, options=[ft.dropdown.Option(detail.sach.ID_Sach, detail.sach.TenSach)], disabled=True, width=290)
            quantity_field = ft.TextField(value=str(detail.SoLuong), read_only=True, width=120, text_align=ft.TextAlign.CENTER)
            price_field = ft.TextField(value=f"{detail.DonGia:,.0f}", read_only=True, width=150, text_align=ft.TextAlign.RIGHT)
            row = ft.Row([book_dropdown, quantity_field, price_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            self.details_column.controls.append(row)

    def _save_receipt(self, e):
        self.clear_all_errors()
        try:
            ngay_xuat, id_nhanvien, id_nhaphanphoi = self.date_field.value, self.employee_dropdown.value, self.distributor_dropdown.value

            if not ngay_xuat: self.date_field.error_text = "Ngày xuất không được trống"; self.page.update(); return
            if not id_nhanvien: self.employee_dropdown.error_text = "Vui lòng chọn nhân viên"; self.page.update(); return
            if not id_nhaphanphoi: self.distributor_dropdown.error_text = "Vui lòng chọn nhà phân phối"; self.page.update(); return
            
            nhan_vien_obj = next((nv for nv in self.available_employees if nv.ID_NhanVien == id_nhanvien), None)
            nha_phan_phoi_obj = next((npp for npp in self.available_distributors if npp.ID_NguonXuat == id_nhaphanphoi), None)
            
            phieu_xuat_update = PhieuXuatSach(
                ID_PhieuXuat=self._receipt.ID_PhieuXuat,
                NgayXuat=ngay_xuat,
                TongSoLuong=self._receipt.TongSoLuong,
                TongTien=self._receipt.TongTien,
                nhan_vien_xuat=nhan_vien_obj,
                nha_phan_phoi=nha_phan_phoi_obj
            )

            update_result = self.phieuxuat_service.update(phieu_xuat_update)
            
            if update_result:
                self._show_snackbar("Cập nhật phiếu xuất thành công!")
                self._handle_close(e)
            else:
                self._show_error("Cập nhật phiếu xuất thất bại. Không có thay đổi nào được ghi nhận.")

        except ValueError as ve:
            msg = str(ve)
            if "Ngày xuất" in msg: self.date_field.error_text = msg
            elif "nhân viên" in msg: self.employee_dropdown.error_text = msg
            elif "nhà phân phối" in msg: self.distributor_dropdown.error_text = msg
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
        self.distributor_dropdown.error_text = None
        self.page.update()

    def _show_error(self, message: str):
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message, color=ft.Colors.WHITE), bgcolor=ft.Colors.RED_400)
        self.page.snack_bar.open = True
        self.page.update()

    def _show_snackbar(self, message: str):
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message))
        self.page.snack_bar.open = True
        self.page.update()