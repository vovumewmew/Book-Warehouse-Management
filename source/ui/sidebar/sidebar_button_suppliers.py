from .sidebar_button_base import SidebarButtonBase
import flet as ft

class SidebarButtonSuppliers(SidebarButtonBase):
    def __init__(self, on_click=None, selected=False):
        super().__init__(
            text="Nhà cung cấp",
            icon=ft.Icons.FACTORY_ROUNDED,
            on_click=on_click,
            selected=selected,
        )
