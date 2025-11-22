# source/ui/search/search_bar_base.py
import flet as ft

class SearchBarBase(ft.Container):
    def __init__(self, placeholder="Tìm kiếm...", on_search=None, width=250):
        super().__init__()
        self.on_search = on_search
        self.width = width

        # TextField kéo dài
        self.search_field = ft.TextField(
            hint_text=placeholder,
            expand=True,
            border_radius=12,
            border_color="#A94F8B",
            focused_border_color="#FF69B4",
            bgcolor="#FFF8FB",
            text_size=14,
            content_padding=ft.padding.symmetric(horizontal=12, vertical=6),
            cursor_color="#A94F8B",
            cursor_width=2,
            on_submit=self._submit
        )

        # Nút kính lúp
        self.search_button = ft.IconButton(
            icon=ft.Icons.SEARCH,
            bgcolor="#A94F8B",
            icon_color=ft.Colors.WHITE,
            width=40,
            height=40,
            tooltip="Tìm kiếm",
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
            on_click=self._submit
        )

        # Row chứa TextField + nút
        self.content = ft.Row(
            [self.search_field, self.search_button],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
            width=self.width
        )

    def _submit(self, e):
        if self.on_search:
            query = self.search_field.value.strip()
            self.on_search(query)