from source.ui.card.card_base import CardBase
from source.ui.form.display_form.book_form import BookForm

class BookCard(CardBase):
    def __init__(self, sach, *, page=None, mode="available"):
        self.page = page  # lưu page để sử dụng khi mở form
        super().__init__(
            title=sach.TenSach,
            subtitle=f"Tác giả: {sach.TacGia}",
            image_path=sach.HinhAnh,
            extra_info=f"{sach.SoLuong} cuốn",
            form_class=BookForm,
            form_data=sach,
            width=220,
            height=300,
            mode=mode
        )
