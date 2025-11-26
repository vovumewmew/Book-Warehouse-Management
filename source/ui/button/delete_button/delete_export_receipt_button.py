import flet as ft

class DeleteExportReceiptButton(ft.ElevatedButton):
    def __init__(self, page: ft.Page, receipt, service, on_deleted):
        super().__init__(
            text="Xóa",
            bgcolor="#A94F8B",
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=30)),
            on_click=self.confirm_delete
        )
        self.page = page
        self._receipt = receipt
        self.service = service
        self.on_deleted = on_deleted
        self.confirm_dialog = None

    def confirm_delete(self, e):
        """Hiển thị hộp thoại xác nhận xóa."""
        self._show_dialog(
            title="Xác nhận xóa",
            message=f"Bạn có chắc chắn muốn xóa phiếu '{self._receipt.ID_PhieuXuat}'?\nHành động này sẽ hoàn tác số lượng sách trong kho.",
            is_confirm=True
        )

    def delete_action(self, e):
        """Thực hiện hành động xóa sau khi xác nhận."""
        self.close_dialog()
        try:
            success = self.service.delete(self._receipt.ID_PhieuXuat)
            if success:
                if self.on_deleted:
                    self.on_deleted(f"Đã xóa thành công phiếu '{self._receipt.ID_PhieuXuat}'.")
            else:
                self._show_dialog("Lỗi", "Xóa phiếu thất bại do một lỗi không xác định.", is_error=True)
        except Exception as ex:
            self._show_dialog("Lỗi", str(ex), is_error=True)

    def _show_dialog(self, title: str, message: str, is_confirm: bool = False, is_error: bool = False):
        """Hiển thị một dialog tùy chỉnh (xác nhận, lỗi, thành công)."""
        
        if is_error:
            bgcolor = "#F8BBD0"
            title_color = "#C2185B"
        elif is_confirm:
            bgcolor = "#C0ABE4"
            title_color = "#72287F"
        else: # Success
            bgcolor = "#FCE4EC"
            title_color = "#880E4F"

        actions = []
        if is_confirm:
            actions.append(ft.ElevatedButton("Hủy", bgcolor="#914D86", color="white", on_click=lambda e: self.close_dialog()))
            actions.append(ft.ElevatedButton("Xác nhận", bgcolor="#914D86", color="white", on_click=self.delete_action))
        else:
            actions.append(ft.ElevatedButton("Đóng", bgcolor="#A94F8B", color="white", on_click=lambda e: self.close_dialog()))

        dialog_content = ft.Container(
            width=400, padding=20, bgcolor=bgcolor, border_radius=18,
            content=ft.Column([
                ft.Text(title, size=18, weight="bold", color=title_color),
                ft.Text(message, size=14, color=title_color, max_lines=3, overflow=ft.TextOverflow.ELLIPSIS, text_align=ft.TextAlign.CENTER),
                ft.Row(actions, alignment=ft.MainAxisAlignment.END)
            ], spacing=15, tight=True)
        )

        self.confirm_dialog = ft.Container(
            expand=True, bgcolor=ft.Colors.with_opacity(0.4, ft.Colors.BLACK),
            alignment=ft.alignment.center, content=dialog_content
        )
        self.page.overlay.append(self.confirm_dialog)
        self.page.update()

    def close_dialog(self):
        if self.confirm_dialog in self.page.overlay:
            self.page.overlay.remove(self.confirm_dialog)
            self.page.update()