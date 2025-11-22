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
from source.models.ChiTietPhieuNhap import ChiTietPhieuNhap
from util.dialog_utils import show_error_dialog

class AddImportReceiptForm(ft.Container):
    def __init__(self, page: ft.Page, on_close=None):
        super().__init__()
        self.page = page
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
        self.available_books = self.sach_service.get_all()

        # --- Controls cho thông tin chung ---
        self.id_field = ft.TextField(label="Mã phiếu", expand=True)
        self.date_field = ft.TextField(label="Ngày nhập", hint_text="dd/mm/yyyy", expand=True, on_blur=self._validate_date)
        self.employee_dropdown = ft.Dropdown(
            label="Nhân viên nhập",
            options=[ft.dropdown.Option(nv.ID_NhanVien, nv.HoTen) for nv in self.available_employees],
        )
        self.supplier_dropdown = ft.Dropdown(
            label="Nguồn nhập",
            options=[ft.dropdown.Option(ncc.ID_NguonNhap, ncc.TenCoSo) for ncc in self.available_suppliers]
        )
        self.total_quantity_field = ft.TextField(label="Tổng số lượng", read_only=True, value="0")
        self.total_price_field = ft.TextField(label="Tổng tiền", read_only=True, value="0 VNĐ")

        self.details_column = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=10)

        # --- Buttons ---
        self.cancel_button = ft.ElevatedButton("Hủy", on_click=self._handle_close, bgcolor="#A94F8B", color=ft.Colors.WHITE)
        self.save_button = ft.ElevatedButton("Lưu", on_click=self._save_receipt, bgcolor="#A94F8B", color=ft.Colors.WHITE)

        # --- Build ---
        self.content = self.build_form()
        self._add_detail_row() # Thêm một dòng chi tiết trống ban đầu
        
        # Gán sự kiện on_focus để xóa lỗi
        self.id_field.on_focus = self._clear_error
        self.employee_dropdown.on_focus = self._clear_error
        self.date_field.on_focus = self._clear_error
        self.supplier_dropdown.on_focus = self._clear_error

    def _clear_error(self, e):
        e.control.error_text = None
        self.page.update()

    def _validate_date(self, e):
        """Kiểm tra ngày nhập không được lớn hơn ngày hiện tại."""
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
                    ft.Text("Thêm Phiếu Nhập Mới", size=20, weight="bold", color="#A94F8B"),
                    ft.Divider(height=10, color="#A94F8B"),
                    ft.Row(
                        [
                            ft.Column([self.id_field, self.employee_dropdown, self.supplier_dropdown], spacing=10, expand=True),
                            ft.Column([self.date_field, self.total_quantity_field, self.total_price_field], spacing=10, expand=True),
                        ],
                        spacing=20
                    ),
                    ft.Divider(height=15, color="transparent"),
                    ft.Text("Chi tiết phiếu nhập", weight="bold", color="#A94F8B"),
                    ft.Container(self.details_column, border=ft.border.all(1, "#E5C4EC"), border_radius=10, padding=10, height=250),
                    ft.Row(
                        [
                            ft.IconButton(icon=ft.Icons.ADD_CIRCLE, on_click=self._add_detail_row, tooltip="Thêm dòng", icon_color=ft.Colors.WHITE, bgcolor="#A94F8B"),
                            ft.Row(
                                [self.cancel_button, self.save_button],
                                alignment=ft.MainAxisAlignment.END,
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                ],
                scroll=ft.ScrollMode.AUTO,
            )
        )

    def _add_detail_row(self, e=None):
        book_dropdown = ft.Dropdown(
            label="Tên sách",
            options=[ft.dropdown.Option(sach.ID_Sach, f"{sach.TenSach} (Tồn: {sach.SoLuong})") for sach in self.available_books],
            width=290,
            on_change=self._update_totals
        )
        quantity_field = ft.TextField(label="Số lượng", width=120, input_filter=ft.NumbersOnlyInputFilter(), on_change=self._update_totals, text_align=ft.TextAlign.CENTER)
        price_field = ft.TextField(label="Đơn giá", width=150, on_change=self._update_totals, hint_text="Mặc định giá sách", text_align=ft.TextAlign.RIGHT)

        new_row = ft.Row(
            controls=[book_dropdown, quantity_field, price_field],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        if len(self.details_column.controls) == 0:
            reset_button = ft.IconButton(
                icon=ft.Icons.DELETE_ROUNDED,
                icon_color=ft.Colors.WHITE,
                bgcolor="#A94F8B",
                style=ft.ButtonStyle(shape=ft.CircleBorder()),
                tooltip="Xóa trắng dòng",
                on_click=lambda _, row=new_row: self._reset_detail_row(row)
            )
            new_row.controls.append(reset_button)
        else: 
            delete_button = ft.IconButton(
                icon=ft.Icons.DELETE_ROUNDED,
                icon_color=ft.Colors.WHITE,
                bgcolor="#A94F8B",
                tooltip="Xóa dòng",
                style=ft.ButtonStyle(shape=ft.CircleBorder()),
                on_click=lambda _, row=new_row: self._remove_detail_row(row)
            )
            new_row.controls.append(delete_button)

        self.details_column.controls.append(new_row)
        self.page.update()

    def _remove_detail_row(self, row_to_remove):
        self.details_column.controls.remove(row_to_remove)
        self._update_totals()
        self.page.update()

    def _reset_detail_row(self, row_to_reset):
        row_to_reset.controls[0].value = None
        row_to_reset.controls[1].value = ""
        row_to_reset.controls[2].value = ""
        self._update_totals()
        self.page.update()

    def _update_totals(self, e=None):
        total_quantity = 0
        total_price = Decimal(0)

        for row in self.details_column.controls:
            book_id = row.controls[0].value
            quantity_str = row.controls[1].value
            price_str = row.controls[2].value

            if not book_id or not quantity_str:
                continue

            try:
                quantity = int(quantity_str)
                if quantity <= 0: continue

                book = next((b for b in self.available_books if b.ID_Sach == book_id), None)
                if not book: continue

                price = Decimal(price_str.replace(",", "")) if price_str else book.Gia

                total_quantity += quantity
                total_price += quantity * price

            except (ValueError, TypeError):
                continue

        self.total_quantity_field.value = str(total_quantity)
        self.total_price_field.value = f"{total_price:,.0f} VNĐ"
        self.page.update()

    def _save_receipt(self, e):
        self.clear_all_errors()
        try:
            id_phieu = self.id_field.value
            ngay_nhap = self.date_field.value
            id_nhanvien = self.employee_dropdown.value
            id_nguonnhap = self.supplier_dropdown.value

            if not id_phieu:
                self.id_field.error_text = "Mã phiếu không được trống"
                self.page.update()
                return
            
            try:
                PhieuNhapSach(ID_PhieuNhap=id_phieu, NgayNhap="01/01/2025", TongSoLuong=0, TongTien=0, nhan_vien_nhap=self.available_employees[0], nguon_nhap=self.available_suppliers[0])
            except ValueError as ve:
                self.id_field.error_text = str(ve)
                self.page.update()
                return

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
            phieu_nhap = PhieuNhapSach(
                ID_PhieuNhap=id_phieu,
                NgayNhap=ngay_nhap,
                TongSoLuong=0,
                TongTien=Decimal(0),
                nhan_vien_nhap=nhan_vien_obj,
                nguon_nhap=nguon_nhap_obj
            )

            list_chitiet = []
            for row in self.details_column.controls:
                book_id = row.controls[0].value
                quantity_str = row.controls[1].value
                price_str = row.controls[2].value

                if not book_id or not quantity_str or int(quantity_str) <= 0:
                    continue

                sach_obj = next((s for s in self.available_books if s.ID_Sach == book_id), None)
                if not sach_obj:
                    self._show_error(f"Không tìm thấy sách với mã {book_id}")
                    return

                don_gia = Decimal(price_str) if price_str else sach_obj.Gia

                chi_tiet = ChiTietPhieuNhap(
                    phieu_nhap=phieu_nhap,
                    sach=sach_obj,
                    SoLuong=int(quantity_str),
                    DonGia=don_gia
                )
                list_chitiet.append(chi_tiet)

            if not list_chitiet:
                self._show_error("Phiếu nhập phải có ít nhất một chi tiết hợp lệ.")
                return

            phieu_nhap.load_chitiet_nhap(list_chitiet)

            if self.phieunhap_service.create(phieu_nhap):
                self._show_snackbar("Tạo phiếu nhập thành công!")
                self._handle_close(e)
            else:
                show_error_dialog(
                    self.page,
                    "Lỗi Trùng Lặp",
                    f"Mã phiếu nhập '{id_phieu}' đã tồn tại trong hệ thống. Vui lòng sử dụng mã khác."
                )

        except ValueError as ve:
            msg = str(ve)
            if "Mã phiếu nhập" in msg or "ID_PhieuNhap" in msg:
                self.id_field.error_text = msg
            elif "Ngày nhập" in msg: self.date_field.error_text = msg
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
        self.id_field.error_text = None
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