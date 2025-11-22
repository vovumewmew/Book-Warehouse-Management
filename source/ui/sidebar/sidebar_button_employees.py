from .sidebar_button_base import SidebarButtonBase
import flet as ft

class SidebarButtonEmployees(SidebarButtonBase):
    def __init__(self, on_click=None, selected=False):
        super().__init__(
            text="Nhân Viên",
            icon=ft.Icons.GROUP_ROUNDED,
            on_click=on_click,
            selected=selected,
        )
