# source/ui/search/search_bar_distributor.py
import flet as ft
from .search_bar_base import SearchBarBase
from source.ui.Table.distributor_table import DistributorTable
from source.dao.NhaPhanPhoiDAO import NhaPhanPhoiDAO
from config.db_connection import DatabaseConnection

class SearchBarDistributor(SearchBarBase):
    def __init__(self, page: ft.Page, distributors_container: ft.Column, width=300):
        super().__init__(placeholder="Tìm nhà phân phối...", width=width, on_search=self.search_distributors)
        self.page = page
        self.distributors_container = distributors_container
        self.distributors_cache = []  # cache dữ liệu

        # Lần đầu load dữ liệu
        self.load_distributors_from_db()

    def load_distributors_from_db(self):
        db = DatabaseConnection()
        self.distributors_cache = NhaPhanPhoiDAO(db).get_all()
        db.disconnect()

    def search_distributors(self, query: str):
        distributors = self.distributors_cache  # filter từ cache
        if query:
            q = query.lower()
            distributors = [
                d for d in distributors
                if q in d.TenCoSo.lower()
                or q in d.ID_NguonXuat.lower()
                or q in d.DiaChi.lower()
                or q in d.Email.lower()
            ]
        self.distributors_container.controls.clear()
        self.distributors_container.controls.append(DistributorTable(distributors, page=self.page, columns=3))
        self.page.update()
