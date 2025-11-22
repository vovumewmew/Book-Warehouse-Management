from .sidebar_button_base import SidebarButtonBase
import flet as ft

class SidebarButtonBooks(SidebarButtonBase):
    def __init__(self, on_click=None, selected=False):
        super().__init__(
            text="Sách",
            icon=ft.Icons.MENU_BOOK_ROUNDED,
            on_click=on_click,
            selected=selected,
        )
