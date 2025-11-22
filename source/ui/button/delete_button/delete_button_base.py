# source/ui/button/delete_button/delete_button_base.py
import flet as ft

class DeleteButtonBase(ft.ElevatedButton):
    def __init__(self, text: str = "Xóa", on_delete=None):
        super().__init__(
            text=text,
            bgcolor="#A94F8B",  # nút delete màu tím
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=28)),
            on_click=self._handle_click
        )
        self.on_delete = on_delete
        self.confirm_overlay = None

    def _handle_click(self, e):
        self.confirm_delete(e)

    def confirm_delete(self, e):
        # Hộp popup chính (không để expand!)
        confirm_box = ft.Container(
            width=360,
            height=160,
            padding=20,
            bgcolor="#C0ABE4",
            border_radius=18,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.25, ft.Colors.BLACK),
            ),
            # ⭐ Cho phép scroll nếu vượt quá
            content=ft.Column(
                [
                    ft.Text(
                        "Xác nhận xóa",
                        size=18,
                        weight="bold",
                        color="#72287F",
                    ),
                    ft.Text(
                        "Bạn có chắc chắn muốn xóa mục này không?",
                        size=14,
                        color="#72287F",
                    ),
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                "Hủy",
                                bgcolor="#914D86",
                                color="white",
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8)
                                ),
                                on_click=self.cancel_delete
                            ),
                            ft.ElevatedButton(
                                "Xóa",
                                bgcolor="#914D86",
                                color="white",
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8)
                                ),
                                on_click=self.delete_confirmed
                            )
                        ],
                        alignment=ft.MainAxisAlignment.END,
                        spacing=12
                    )
                ],
                spacing=20,
                # ⭐ Nếu nội dung dài → tự bật scroll
                scroll=ft.ScrollMode.AUTO
            )
        )

        # Overlay nền mờ (chỉ overlay expand)
        self.confirm_overlay = ft.Container(
            expand=True,
            bgcolor=ft.Colors.with_opacity(0.4, ft.Colors.BLACK),
            alignment=ft.alignment.center,
            content=confirm_box
        )

        # Lấy page từ sự kiện để đảm bảo luôn có giá trị
        page = e.control.page
        if page:
            page.overlay.append(self.confirm_overlay)
            page.update()

    def cancel_delete(self, e):
        page = e.control.page
        if page and page.overlay and self.confirm_overlay in page.overlay:
            page.overlay.remove(self.confirm_overlay)
            page.update()

    def delete_confirmed(self, e):
        page = e.control.page
        if self.on_delete:
            self.on_delete(e) # Truyền sự kiện 'e' vào

        if page and page.overlay and self.confirm_overlay in page.overlay:
            page.overlay.remove(self.confirm_overlay)
            page.update()
