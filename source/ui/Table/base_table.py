import flet as ft

class TableBase(ft.Container):
    """
    Lớp base cho các bảng chứa card (dạng lưới).
    Có thể tái sử dụng cho sách, nhân viên, nhà phân phối,...
    """
    def __init__(self, items: list, columns: int = 3, card_class=None, page=None, mode: str = "available"):
        """
        items: danh sách đối tượng dữ liệu (ví dụ: sách, nhân viên,...)
        columns: số lượng cột trong grid
        card_class: class card cụ thể (BookCard, EmployeeCard,...)
        page: đối tượng ft.Page — cần để mở form khi click card
        mode: chế độ hiển thị form ('available' hoặc 'unavailable')
        """
        super().__init__()
        self.items = items
        self.columns = columns
        self.card_class = card_class
        self.page = page
        self.mode = mode
        self.content = self.build()

    def build(self):
        # Danh sách các hàng (Row)
        rows = []

        for i in range(0, len(self.items), self.columns):
            row_items = self.items[i : i + self.columns]
            row = ft.Row(
                [
                    self.card_class(item, page=self.page, mode=self.mode)
                    for item in row_items
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=20,
            )
            rows.append(row)

        return ft.Container(
            expand=True,
            padding=10,
            content=ft.Column(
                rows,
                spacing=10,
                scroll=ft.ScrollMode.AUTO,  # ✅ Cuộn mượt hơn
            ),
        )
