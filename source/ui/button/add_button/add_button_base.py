import flet as ft

class AddButtonBase(ft.Container):
    """
    Base cho nút thêm mới một đối tượng.
    """
    def __init__(
        self, 
        text: str = "Thêm", 
        on_click=None, 
        width: int = 80, 
        height: int = 30, 
        icon: str = None,
        page: ft.Page = None
    ):
        super().__init__()

        self.page = page
        self.on_click_callback = on_click

        self.button = ft.FilledTonalButton(
            text=text,
            icon=icon,
            on_click=self._handle_click,
            width=width,
            height=height,
            style=ft.ButtonStyle(
                color={"": ft.Colors.WHITE},
                bgcolor={"": "#A94F8B"},
                shape={"": ft.RoundedRectangleBorder(radius=10)},
            ),
        )


        self.content = self.button

    def _handle_click(self, e):
        if callable(self.on_click_callback):
            self.on_click_callback(e)
