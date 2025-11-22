import flet as ft

def show_error_dialog(page: ft.Page, title: str, message: str, on_close=None):
    """
    Hiển thị một hộp thoại lỗi tùy chỉnh, có thể đóng được.
    """
    error_dialog = None

    def close_dialog(e=None):
        if page and page.overlay and error_dialog in page.overlay:
            page.overlay.remove(error_dialog)
            page.update()
        if on_close:
            on_close()

    dialog_content = ft.Container(
        width=400,
        padding=20,
        bgcolor="#F8BBD0",  # Màu nền lỗi
        border_radius=18,
        content=ft.Column([
            ft.Text(title, size=18, weight="bold", color="#C2185B"),
            ft.Text(message, size=14, color="#C2185B", max_lines=3, overflow=ft.TextOverflow.ELLIPSIS, text_align=ft.TextAlign.CENTER),
            ft.Row(
                [ft.ElevatedButton("Đóng", bgcolor="#A94F8B", color="white", on_click=close_dialog)],
                alignment=ft.MainAxisAlignment.END
            )
        ], spacing=15,
           # Để Column tự điều chỉnh chiều cao
           tight=True)
    )

    error_dialog = ft.Container(
        expand=True,
        bgcolor=ft.Colors.with_opacity(0.4, ft.Colors.BLACK),
        alignment=ft.alignment.center,
        content=dialog_content
    )

    page.overlay.append(error_dialog)
    page.update()