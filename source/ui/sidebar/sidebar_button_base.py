import flet as ft

class SidebarButtonBase(ft.Container):
    def __init__(self, text: str, icon: str = None, on_click=None, selected=False):
        super().__init__()
        self.text = text
        self.icon = icon
        self.on_click_callback = on_click
        self.selected = selected

        # 🎨 Màu sắc
        self.bg_default = "#FFFFFF"
        self.bg_hover = "#FDE7EF"
        self.text_color_default = "#555555"
        self.text_color_selected = "#C2185B"
        self.selected_border_color = "#C2185B"

        # === Nội dung nút ===
        self.icon_view = ft.Icon(
            self.icon or ft.Icons.HOME_OUTLINED,
            color=self._text_color(),
            size=20,
        )
        self.text_view = ft.Text(
            self.text,
            size=14,
            color=self._text_color(),
            weight=ft.FontWeight.W_600,
        )
        if self.selected:
            self.text_view.decoration = ft.TextDecoration.UNDERLINE

        # === Gạch dọc bên trái khi được chọn ===
        self.left_border = ft.Container(
            width=4,
            height=30,
            bgcolor=self.selected_border_color if self.selected else None,
            border_radius=ft.border_radius.all(3),
        )

        # === Gộp nội dung icon + text ===
        self.content_row = ft.Row(
            controls=[self.icon_view, self.text_view],
            spacing=10,
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # === Tổng thể nút (có gạch trái + nội dung) ===
        self.inner = ft.Row(
            controls=[self.left_border, self.content_row],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # === Container chính ===
        self.bgcolor = self.bg_default
        self.content = self.inner
        self.border_radius = 10
        self.padding = 10
        self.margin = ft.margin.only(top=10)
        self.ink = True

        # Sự kiện
        self.on_hover = self._on_hover
        self.on_click = self._on_click

    # 🧠 Lấy màu chữ hiện tại
    def _text_color(self):
        return self.text_color_selected if self.selected else self.text_color_default

    # 🧠 Khi hover chuột
    def _on_hover(self, e: ft.HoverEvent):
        if not self.selected:
            self.bgcolor = self.bg_hover if e.data == "true" else self.bg_default
            self.update()

    # 🧠 Khi click
    def _on_click(self, e: ft.ControlEvent):
        if self.on_click_callback:
            self.on_click_callback(self)

    # 🧠 Cập nhật khi được chọn hoặc bỏ chọn
    def set_selected(self, value: bool):
        self.selected = value

        self.icon_view.color = self._text_color()

        # Gạch bên trái
        self.left_border.bgcolor = self.selected_border_color if value else None

        # Màu chữ
        self.text_view.color = self._text_color()

        # Gạch dưới text
        self.text_view.decoration = ft.TextDecoration.UNDERLINE if value else None

        # Reset nền (nếu bỏ chọn)
        if not value:
            self.bgcolor = self.bg_default

        # Update tất cả control con
        self.icon_view.update()
        self.text_view.update()
        self.left_border.update()
        self.update()
