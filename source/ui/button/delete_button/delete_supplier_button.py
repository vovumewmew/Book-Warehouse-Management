import flet as ft
from .delete_button_base import DeleteButtonBase
from source.dao.NguonNhapSachDAO import NguonNhapSachDAO
from source.services.NguonNhapSachService import NguonNhapSachService
from config.db_connection import DatabaseConnection

class DeleteSupplierButton(DeleteButtonBase):
    def __init__(self, page: ft.Page, on_delete=None):
        super().__init__(text="Xóa", on_delete=on_delete)
        self.page = page
