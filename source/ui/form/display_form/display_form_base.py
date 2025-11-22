import flet as ft

class DisplayFormBase(ft.Container):
    def __init__(self, title: str, fields: dict, width: int = 400, height: int = 500, on_close=None):
        super().__init__()
        self.title = title
        self.fields = fields  # dict: {"Tên trường": "Giá trị"}
        self.width = width
        self.height = height
        self.on_close = on_close  # lưu callback
        self.content = self.build_form()

    def build_form(self):
        field_controls = []
        for label, value in self.fields.items():
            field_controls.append(
                ft.TextField(
                    label=label,
                    value=str(value) if value is not None else "",
                    width=self.width - 60,
                    read_only=True,
                    border_color="#C8A2C8",
                )
            )

        # Nút đóng form, khi click sẽ gọi callback on_close nếu có
        close_button = ft.ElevatedButton(
            "Đóng",
            bgcolor="#A94F8B",
            color=ft.Colors.WHITE,
            on_click=self._handle_close
        )

        return ft.Container(
            bgcolor="#FFF8FB",
            padding=20,
            border_radius=ft.border_radius.all(16),
            border=ft.border.all(2, "#E5C4EC"),
            content=ft.Column(
                [
                    ft.Text(
                        self.title,
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color="#A94F8B",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Divider(height=20, color="#A94F8B"),
                    ft.Column(field_controls, spacing=10),
                    ft.Divider(height=10, color="transparent"),
                    close_button,
                ],
                scroll=ft.ScrollMode.AUTO,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    def _handle_close(self, e):
    # Nếu form đang được hiển thị trong page overlay, xóa nó
        if hasattr(self, "page") and self.page and self.page.overlay and self in self.page.overlay:
            self.page.overlay.remove(self)
            self.page.update()

        # Chỉ gọi callback on_close khi có một hành động thực sự xảy ra (được gọi từ các hàm con)
        # Nếu người dùng chỉ nhấn nút "Đóng", không cần làm mới trang.
        if e.control.text != "Đóng" and self.on_close:
             self.on_close()
