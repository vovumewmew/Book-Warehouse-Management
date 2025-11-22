# source/ui/search/search_bar_employee.py
import flet as ft
from .search_bar_base import SearchBarBase
from source.ui.Table.employees_table import EmployeeTable
from source.dao.NhanVienDAO import NhanVienDAO
from config.db_connection import DatabaseConnection

class SearchBarEmployee(SearchBarBase):
    def __init__(self, page: ft.Page, employees_container: ft.Column, width=300):
        super().__init__(placeholder="Tìm nhân viên...", width=width, on_search=self.search_employees)
        self.page = page
        self.employees_container = employees_container
        self.employees_cache = []  # cache dữ liệu nhân viên

        # Lần đầu load dữ liệu
        self.load_employees_from_db()

    def load_employees_from_db(self):
        db = DatabaseConnection()
        self.employees_cache = NhanVienDAO(db).get_all()
        db.disconnect()

    def search_employees(self, query: str):
        employees = self.employees_cache  # filter từ cache
        if query:
            q = query.lower()
            employees = [
                emp for emp in employees
                if q in emp.HoTen.lower()
                or q in emp.ChucVu.lower()
                or q in emp.ID_NhanVien.lower()
                or q in emp.Email.lower()
            ]
        self.employees_container.controls.clear()
        self.employees_container.controls.append(EmployeeTable(employees, page=self.page, columns=3))
        self.page.update()
