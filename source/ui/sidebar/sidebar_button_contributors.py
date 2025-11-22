from .sidebar_button_base import SidebarButtonBase
import flet as ft

class SidebarButtonContributors(SidebarButtonBase):
    def __init__(self, on_click=None, selected=False):
        super().__init__(
            text="Nhà Phân Phối",
            icon=ft.Icons.STORE_ROUNDED,
            on_click=on_click,
            selected=selected,
        )
