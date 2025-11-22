import flet as ft
from .delete_button_base import DeleteButtonBase
from source.dao.NhanVienDAO import NhanVienDAO
from source.services.NhanVienService import NhanVienService
from config.db_connection import DatabaseConnection

class DeleteEmployeeButton(DeleteButtonBase):
    def __init__(self, page: ft.Page, on_delete=None):
        super().__init__(text="Xóa", on_delete=on_delete)
        self.page = page
