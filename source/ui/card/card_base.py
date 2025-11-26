# file: source/ui/card/card_base.py
import flet as ft
import os
from util.get_absolute_path import get_absolute_path

class CardBase(ft.Container):
    def __init__(
        self,
        title: str = "",
        subtitle: str = "",
        image_path: str = None,
        extra_info: str = "",
        extra_info_color: str = "#A94F8B",  # Thêm màu cho extra_info
        page=None,
        form_data=None,
        width: int = 220,
        height: int = 300,
        hover_color: str = "#F6EFFF",  # màu khi hover
        card_bgcolor: str = "#FFEAF3", # màu card (phần bo góc)
        form_class=None,
        mode: str = "available", # Thêm mode: 'available' hoặc 'unavailable'
    ):
        super().__init__()
        self.title = title
        self.subtitle = subtitle
        self.image_path = image_path
        self.extra_info = extra_info
        self.extra_info_color = extra_info_color # Lưu lại màu
        self.width = width
        self.height = height
        self.card_bgcolor = card_bgcolor
        self.hover_color = hover_color
        self.default_bgcolor = card_bgcolor
        self.page = page
        self.form_data = form_data
        self.form_class = form_class
        self.mode = mode
        self.form_instance = None

        # Container card thực tế (bo góc, hover)
        self.card_container = ft.Container()
        self.content = self.card_container

        # Hover effect
        self.card_container.on_hover = self._on_hover
        # Click event
        self.card_container.on_click = self._on_click

        self._build_card()

    def _on_hover(self, e: ft.HoverEvent):
        self.card_container.bgcolor = self.hover_color if e.data == "true" else self.default_bgcolor
        self.card_container.update()

    def _build_card(self):
        # Lấy đường dẫn ảnh tuyệt đối
        abs_path = get_absolute_path(self.image_path) if self.image_path else None

        self.card_container.content = ft.Column(
            [
                ft.Container(
                    width=self.width - 40,
                    height=160,
                    border_radius=ft.border_radius.all(12),
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    content=ft.Image(
                        src=abs_path,
                        width=self.width - 40,
                        height=160,
                        fit=ft.ImageFit.COVER,
                    )
                ),
                ft.Text(
                    self.title,
                    size=15,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.GREY_800,
                    text_align=ft.TextAlign.CENTER,
                    max_lines=2,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
                ft.Text(
                    self.subtitle,
                    size=13,
                    color=ft.Colors.GREY_800,
                    text_align=ft.TextAlign.CENTER,
                    italic=True,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ) if self.subtitle else ft.Container(),
                ft.Text(
                    self.extra_info,
                    size=13,
                    color=self.extra_info_color, # Sử dụng màu tùy chỉnh
                    text_align=ft.TextAlign.CENTER,
                ) if self.extra_info else ft.Container(),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=6,
        )

        # Thiết lập Container bo góc chính
        self.card_container.width = self.width
        self.card_container.height = self.height
        self.card_container.bgcolor = self.card_bgcolor
        self.card_container.border_radius = ft.border_radius.all(16)
        self.card_container.shadow = ft.BoxShadow(
            blur_radius=10,
            spread_radius=-3,
            color="rgba(0,0,0,0.08)",
            offset=ft.Offset(2, 3),
        )
        self.card_container.padding = 10
        self.card_container.margin = 8

    def _on_click(self, e):
        # Nếu form instance cũ tồn tại, xóa nó
        if hasattr(self, "form_instance") and self.form_instance:
            if hasattr(self.form_instance, "page") and self.form_instance.page:
                if self.form_instance in self.form_instance.page.overlay:
                    self.form_instance.page.overlay.remove(self.form_instance)
            self.form_instance = None

        # Hàm callback khi form đóng
        def on_form_close():
            # Sau khi form đóng, tự động làm mới trang hiện tại
            # để cập nhật danh sách (xóa/thêm mục vừa thao tác)
            if hasattr(self, "page") and self.page:
                # Tìm MainFrame bằng key để lấy trang hiện tại, thay vì dùng chỉ số cứng
                main_frame_container = self.page.get_control("main_frame")
                if not main_frame_container:
                    return
                current_page_content = main_frame_container.content
                # Tìm và gọi hàm reload tương ứng
                if hasattr(current_page_content, 'reload_books'):
                    current_page_content.reload_books()
                elif hasattr(current_page_content, 'reload_employees'):
                    current_page_content.reload_employees()
                elif hasattr(current_page_content, 'reload_distributors'):
                    current_page_content.reload_distributors()
                elif hasattr(current_page_content, 'reload_suppliers'):
                    current_page_content.reload_suppliers()

            self.form_instance = None
            
        # Tạo form mới
        self.form_instance = self.form_class(
            self.form_data,
            page=self.page,
            on_close=on_form_close,
            mode=self.mode  # Truyền mode vào form
        )

        # Thêm form vào overlay
        if self.page:
            self.form_instance.page = self.page  # đảm bảo form biết page
            self.page.overlay.append(self.form_instance)
            self.page.update()
