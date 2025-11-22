import flet as ft
from .delete_button_base import DeleteButtonBase
from source.dao.NhaPhanPhoiDAO import NhaPhanPhoiDAO
from source.services.NhaPhanPhoiService import NhaPhanPhoiService
from config.db_connection import DatabaseConnection

class DeleteDistributorButton(DeleteButtonBase):
    def __init__(self, page: ft.Page, on_delete=None):
        super().__init__(text="Xóa", on_delete=on_delete)
        self.page = page
