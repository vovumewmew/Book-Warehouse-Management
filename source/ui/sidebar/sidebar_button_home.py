from .sidebar_button_base import SidebarButtonBase
import flet as ft

class SidebarButtonHome(SidebarButtonBase):
    def __init__(self, on_click=None, selected=False):
        super().__init__(
            text="Trang chủ",
            icon=ft.Icons.HOME_ROUNDED,
            on_click=on_click,
            selected=selected,
        )
