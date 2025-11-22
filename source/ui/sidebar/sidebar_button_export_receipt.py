from .sidebar_button_base import SidebarButtonBase
import flet as ft

class SidebarButtonExportReceipt(SidebarButtonBase):
    def __init__(self, on_click=None, selected=False):
        super().__init__(
            text="Phiếu Xuất",
            icon=ft.Icons.UPLOAD_ROUNDED,
            on_click=on_click,
            selected=selected,
        )
