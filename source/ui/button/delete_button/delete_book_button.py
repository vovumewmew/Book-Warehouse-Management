# source/ui/button/delete_button/delete_book_button.py

import flet as ft
from .delete_button_base import DeleteButtonBase
from source.dao.SachDAO import SachDAO
from source.services.SachService import SachService
from config.db_connection import DatabaseConnection

class DeleteBookButton(DeleteButtonBase):
    def __init__(self, page: ft.Page, on_delete=None):
        super().__init__(text="Xóa", on_delete=on_delete)
        self.page = page
