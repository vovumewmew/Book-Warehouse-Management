# source/ui/search/search_bar_supplier.py
import flet as ft
from .search_bar_base import SearchBarBase
from source.ui.Table.supplier_table import SupplierTable
from source.dao.NguonNhapSachDAO import NguonNhapSachDAO
from config.db_connection import DatabaseConnection

class SearchBarSupplier(SearchBarBase):
    def __init__(self, page: ft.Page, supplier_container: ft.Column, width=300):
        super().__init__(placeholder="Tìm nhà cung cấp...", width=width, on_search=self.search_suppliers)
        self.page = page
        self.supplier_container = supplier_container
        self.suppliers_cache = []  # cache dữ liệu

        # Lần đầu load dữ liệu
        self.load_suppliers_from_db()

    def load_suppliers_from_db(self):
        db = DatabaseConnection()
        self.suppliers_cache = NguonNhapSachDAO(db).get_all()
        db.disconnect()

    def search_suppliers(self, query: str):
        suppliers = self.suppliers_cache  # filter từ cache
        if query:
            q = query.lower()
            suppliers = [
                s for s in suppliers
                if q in s.TenCoSo.lower()
                or q in s.ID_NguonNhap.lower()
                or q in s.DiaChi.lower()
                or q in s.Email.lower()
            ]
        self.supplier_container.controls.clear()
        self.supplier_container.controls.append(SupplierTable(suppliers, page=self.page, columns=3))
        self.page.update()
