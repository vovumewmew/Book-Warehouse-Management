from source.ui.card.card_base import CardBase
from source.ui.form.display_form.book_form import BookForm

class BookCard(CardBase):
    def __init__(self, sach, *, page=None, mode="available"):
        self.page = page  # lưu page để sử dụng khi mở form

        # Logic mới: Kiểm tra số lượng sách để quyết định hiển thị
        if sach.SoLuong > 0:
            extra_info_text = f"{sach.SoLuong} cuốn"
            extra_info_color = "#A94F8B"  # Màu mặc định
        else:
            extra_info_text = "Hết hàng"
            extra_info_color = "#E57373"  # Màu đỏ pastel

        super().__init__(
            title=sach.TenSach,
            subtitle=f"Tác giả: {sach.TacGia}",
            image_path=sach.HinhAnh,
            extra_info=extra_info_text,
            extra_info_color=extra_info_color,
            form_class=BookForm,
            form_data=sach,
            width=220,
            height=300,
            mode=mode
        )
