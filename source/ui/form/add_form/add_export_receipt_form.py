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
from source.models.ChiTietPhieuXuat import ChiTietPhieuXuat
from util.dialog_utils import show_error_dialog

class AddExportReceiptForm(ft.Container):
    def __init__(self, page: ft.Page, on_close=None):
        super().__init__()
        self.page = page
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
        self.available_books = self.sach_service.get_all()

        # --- Controls cho thông tin chung ---
        self.id_field = ft.TextField(label="Mã phiếu", expand=True)
        self.date_field = ft.TextField(label="Ngày xuất", hint_text="dd/mm/yyyy", expand=True, on_blur=self._validate_date)
        self.employee_dropdown = ft.Dropdown(
            label="Nhân viên xuất",
            options=[ft.dropdown.Option(nv.ID_NhanVien, nv.HoTen) for nv in self.available_employees],
        )
        self.distributor_dropdown = ft.Dropdown(
            label="Nhà phân phối",
            options=[ft.dropdown.Option(npp.ID_NguonXuat, npp.TenCoSo) for npp in self.available_distributors]
        )
        self.total_quantity_field = ft.TextField(label="Tổng số lượng", read_only=True, value="0")
        self.total_price_field = ft.TextField(label="Tổng tiền", read_only=True, value="0 VNĐ")

        self.details_column = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=10)

        # --- Buttons ---
        self.cancel_button = ft.ElevatedButton("Hủy", on_click=self._handle_close, bgcolor="#A94F8B", color=ft.Colors.WHITE)
        self.save_button = ft.ElevatedButton("Lưu", on_click=self._save_receipt, bgcolor="#A94F8B", color=ft.Colors.WHITE)

        # --- Build ---
        self.content = self.build_form()
        self._add_detail_row()
        
        self.id_field.on_focus = self._clear_error
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
                    ft.Text("Thêm Phiếu Xuất Mới", size=20, weight="bold", color="#A94F8B"),
                    ft.Divider(height=10, color="#A94F8B"),
                    ft.Row(
                        [
                            ft.Column([self.id_field, self.employee_dropdown, self.distributor_dropdown], spacing=10, expand=True),
                            ft.Column([self.date_field, self.total_quantity_field, self.total_price_field], spacing=10, expand=True),
                        ], spacing=20
                    ),
                    ft.Divider(height=15, color="transparent"),
                    ft.Text("Chi tiết phiếu xuất", weight="bold", color="#A94F8B"),
                    ft.Container(self.details_column, border=ft.border.all(1, "#E5C4EC"), border_radius=10, padding=10, height=250),
                    ft.Row(
                        [
                            ft.IconButton(icon=ft.Icons.ADD_CIRCLE, on_click=self._add_detail_row, tooltip="Thêm dòng", icon_color=ft.Colors.WHITE, bgcolor="#A94F8B"),
                            ft.Row([self.cancel_button, self.save_button], alignment=ft.MainAxisAlignment.END)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                ], scroll=ft.ScrollMode.AUTO
            )
        )

    def _add_detail_row(self, e=None):
        quantity_field = ft.TextField(label="Số lượng", width=120, input_filter=ft.NumbersOnlyInputFilter(), text_align=ft.TextAlign.CENTER)
        book_dropdown = ft.Dropdown(
            label="Tên sách",
            options=[ft.dropdown.Option(sach.ID_Sach, f"{sach.TenSach} (Tồn: {sach.SoLuong})") for sach in self.available_books],
            width=290,
        )
        price_field = ft.TextField(label="Đơn giá", width=150, hint_text="Mặc định giá sách", text_align=ft.TextAlign.RIGHT)

        book_dropdown.on_change = lambda ev: self._update_and_validate_row(ev, quantity_field)
        quantity_field.on_change = lambda ev: self._update_and_validate_row(ev, quantity_field, book_dropdown)
        price_field.on_change = self._update_totals

        action_button = ft.IconButton()
        new_row = ft.Row([book_dropdown, quantity_field, price_field, action_button], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        if len(self.details_column.controls) == 0:
            action_button.icon, action_button.tooltip, action_button.on_click = ft.Icons.DELETE_ROUNDED, "Xóa trắng dòng", lambda _, row=new_row: self._reset_detail_row(row)
        else:
            action_button.icon, action_button.tooltip, action_button.on_click = ft.Icons.DELETE_ROUNDED, "Xóa dòng", lambda _, row=new_row: self._remove_detail_row(row)
        
        action_button.icon_color, action_button.bgcolor, action_button.style = ft.Colors.WHITE, "#A94F8B", ft.ButtonStyle(shape=ft.CircleBorder())
        
        self.details_column.controls.append(new_row)
        self.page.update()

    def _update_and_validate_row(self, e, quantity_field, book_dropdown=None):
        book_id = e.control.value if book_dropdown is None else book_dropdown.value
        quantity_str = quantity_field.value
        quantity_field.error_text = None

        if book_id and quantity_str:
            try:
                quantity_to_export = int(quantity_str)
                book_in_stock = next((b for b in self.available_books if b.ID_Sach == book_id), None)
                if book_in_stock and quantity_to_export > book_in_stock.SoLuong:
                    quantity_field.error_text = f"Tồn: {book_in_stock.SoLuong}"
            except ValueError:
                quantity_field.error_text = "Lỗi"
        self._update_totals()

    def _remove_detail_row(self, row_to_remove):
        self.details_column.controls.remove(row_to_remove)
        self._update_totals()

    def _reset_detail_row(self, row_to_reset):
        row_to_reset.controls[0].value = None
        row_to_reset.controls[1].value = ""
        row_to_reset.controls[2].value = ""
        row_to_reset.controls[1].error_text = None
        self._update_totals()

    def _update_totals(self, e=None):
        total_quantity, total_price = 0, Decimal(0)
        for row in self.details_column.controls:
            book_id, quantity_str, price_str = row.controls[0].value, row.controls[1].value, row.controls[2].value
            if not book_id or not quantity_str: continue
            try:
                quantity = int(quantity_str)
                if quantity <= 0: continue
                book = next((b for b in self.available_books if b.ID_Sach == book_id), None)
                if not book: continue
                price = Decimal(price_str.replace(",", "")) if price_str else book.Gia
                total_quantity += quantity
                total_price += quantity * price
            except (ValueError, TypeError): continue
        self.total_quantity_field.value = str(total_quantity)
        self.total_price_field.value = f"{total_price:,.0f} VNĐ"
        self.page.update()

    def _save_receipt(self, e):
        self.clear_all_errors()
        try:
            id_phieu, ngay_xuat, id_nhanvien, id_nhaphanphoi = self.id_field.value, self.date_field.value, self.employee_dropdown.value, self.distributor_dropdown.value

            if not id_phieu: self.id_field.error_text = "Mã phiếu không được trống"; self.page.update(); return
            try:
                PhieuXuatSach(ID_PhieuXuat=id_phieu, NgayXuat="01/01/2025", TongSoLuong=0, TongTien=0, nhan_vien_xuat=self.available_employees[0], nha_phan_phoi=self.available_distributors[0])
            except ValueError as ve:
                self.id_field.error_text = str(ve); self.page.update(); return
            if not ngay_xuat: self.date_field.error_text = "Ngày xuất không được trống"; self.page.update(); return
            if not id_nhanvien: self.employee_dropdown.error_text = "Vui lòng chọn nhân viên"; self.page.update(); return
            if not id_nhaphanphoi: self.distributor_dropdown.error_text = "Vui lòng chọn nhà phân phối"; self.page.update(); return

            nhan_vien_obj = next((nv for nv in self.available_employees if nv.ID_NhanVien == id_nhanvien), None)
            nha_phan_phoi_obj = next((npp for npp in self.available_distributors if npp.ID_NguonXuat == id_nhaphanphoi), None)
            phieu_xuat = PhieuXuatSach(ID_PhieuXuat=id_phieu, NgayXuat=ngay_xuat, TongSoLuong=0, TongTien=Decimal(0), nhan_vien_xuat=nhan_vien_obj, nha_phan_phoi=nha_phan_phoi_obj)

            list_chitiet = []
            for row in self.details_column.controls:
                book_id, quantity_field, price_str = row.controls[0].value, row.controls[1], row.controls[2].value
                quantity_str = quantity_field.value
                if not book_id or not quantity_str or int(quantity_str) <= 0: continue

                sach_obj = next((s for s in self.available_books if s.ID_Sach == book_id), None)
                if not sach_obj: self._show_error(f"Không tìm thấy sách với mã {book_id}"); return
                
                if int(quantity_str) > sach_obj.SoLuong:
                    quantity_field.error_text = f"Vượt tồn kho: {sach_obj.SoLuong}"; self.page.update()
                    self._show_error("Số lượng xuất vượt quá số lượng tồn kho."); return

                don_gia = Decimal(price_str) if price_str else sach_obj.Gia
                chi_tiet = ChiTietPhieuXuat(phieu_xuat=phieu_xuat, sach=sach_obj, SoLuong=int(quantity_str), DonGia=don_gia)
                list_chitiet.append(chi_tiet)

            if not list_chitiet: self._show_error("Phiếu xuất phải có ít nhất một chi tiết hợp lệ."); return

            phieu_xuat.load_chitiet_xuat(list_chitiet)

            if self.phieuxuat_service.create(phieu_xuat):
                self._show_snackbar("Tạo phiếu xuất thành công!")
                self._handle_close(e)
            else:
                show_error_dialog(
                    self.page,
                    "Lỗi Trùng Lặp",
                    f"Mã phiếu xuất '{id_phieu}' đã tồn tại trong hệ thống. Vui lòng sử dụng mã khác."
                )
        except ValueError as ve:
            msg = str(ve)
            if "Mã phiếu xuất" in msg or "ID_PhieuXuat" in msg: self.id_field.error_text = msg
            elif "Ngày xuất" in msg: self.date_field.error_text = msg
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
        self.id_field.error_text, self.date_field.error_text, self.employee_dropdown.error_text, self.distributor_dropdown.error_text = None, None, None, None
        for row in self.details_column.controls: row.controls[1].error_text = None
        self.page.update()

    def _show_error(self, message: str):
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message, color=ft.Colors.WHITE), bgcolor=ft.Colors.RED_400)
        self.page.snack_bar.open = True
        self.page.update()

    def _show_snackbar(self, message: str):
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message))
        self.page.snack_bar.open = True
        self.page.update()