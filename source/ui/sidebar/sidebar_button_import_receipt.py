from .sidebar_button_base import SidebarButtonBase
import flet as ft

class SidebarButtonImportReceipt(SidebarButtonBase):
    def __init__(self, on_click=None, selected=False):
        super().__init__(
            text="Phiếu Nhập",
            icon=ft.Icons.DOWNLOAD_ROUNDED,
            on_click=on_click,
            selected=selected,
        )
