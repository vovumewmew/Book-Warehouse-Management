import flet as ft

class BasePage(ft.Container):
    def __init__(self, title: str, header_action: ft.Control = None):
        super().__init__()
        self.title = title
        self.header_action = header_action  # 👈 thêm control tùy chọn (nút ở góc phải)
        self.content_body = None

    def switch_content(self, new_content):
        self.content_body = new_content
        # Chỉ update khi BasePage đã được add vào page
        if getattr(self, "page", None):
            self.update()


    def build(self):
        # Nếu subclass chưa gán content_body thì gọi build_content()
        if not self.content_body:
            self.content_body = self.build_content()

        # 👇 Hàng tiêu đề: gồm tiêu đề bên trái, nút bên phải
        header_row = ft.Row(
            controls=[
                ft.Text(self.title, size=28, weight=ft.FontWeight.BOLD, color= "#5E4B56"),
                ft.Container(expand=True),  # đẩy phần còn lại sang phải
                self.header_action if self.header_action else ft.Container(),
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # 👇 Container chính của trang (giữ nguyên style bạn có)
        return ft.Container(
            expand=True,
            bgcolor="#FFEAF3",
            border_radius=ft.border_radius.all(18),
            shadow=ft.BoxShadow(
                blur_radius=30,
                spread_radius=-5,
                color="rgba(0,0,0,0.08)",
                offset=(0, 10),
            ),
            padding=30,
            content=ft.Column(
                [
                    header_row,  # 👈 thay vì chỉ là Text, giờ là cả hàng tiêu đề + nút
                    ft.Divider(height=20, color="transparent"),
                    self.content_body,  # nội dung chính
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.START,
                spacing=10,
            ),
        )

    def build_content(self):
        """Hàm con để các lớp kế thừa override"""
        return ft.Text("Chưa có nội dung")
