# add_form_base.py
import flet as ft

class AddFormBase(ft.Container):
    def __init__(self, title="Thêm mới", on_submit=None, on_close=None):
        super().__init__()
        self.title = title
        self.on_submit = on_submit
        self.on_close = on_close
        self.page = None
        self.image_file = None

        # --- Màu mặc định ---
        self.default_field_bgcolor = "#FFFFFF"
        self.default_field_color = ft.Colors.BLACK
        self.default_border_color = "#A94F8B"
        self.default_focused_border_color = "#D291BC" # Màu sáng hơn cùng tone

        # --- Danh sách field ---
        self.fields = []
        self.fields_column = ft.Column(self.fields, spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

        # --- File picker + preview hình ---
        self.image_picker = ft.FilePicker(on_result=self._on_file_picked)
        self.image_preview = ft.Container(
            width=120,
            height=120,
            bgcolor="#f0f0f0",
            border_radius=10,
            content=ft.Icon(ft.Icons.IMAGE, size=60, color="gray"),
        )

        # --- Nút hành động ---
        self.submit_button = ft.ElevatedButton(
            "Lưu",
            bgcolor="#A94F8B",
            color=ft.Colors.WHITE,
            width=100,
            height=40,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
            on_click=self.submit_button_clicked,  # CHỈNH SỬA: gọi submit_button_clicked
        )
        self.close_button = ft.ElevatedButton(
            "Đóng",
            bgcolor="#A94F8B",
            color=ft.Colors.WHITE,
            width=100,
            height=40,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
            on_click=self._handle_close,
        )

        # --- Container chính ---
        self.form_container = ft.Container(
            bgcolor="#FFF8FB",
            padding=20,
            border_radius=ft.border_radius.all(16),
            border=ft.border.all(2, "#E5C4EC"),
            width=500,
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
                    ft.Row(
                        [
                            ft.Container(
                                on_click=lambda e: self.image_picker.pick_files(
                                    allow_multiple=False,
                                    file_type=ft.FilePickerFileType.IMAGE,
                                ),
                                content=self.image_preview,
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    self.fields_column,
                    ft.Row(
                        [self.submit_button, self.close_button],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=15,
                    ),
                ],
                scroll=ft.ScrollMode.AUTO,
                spacing=15,
            ),
        )

        # --- Overlay chính ---
        self.overlay = ft.Container(
            bgcolor=ft.Colors.TRANSPARENT,
            expand=True,
            content=ft.Row(
                [ft.Container(expand=True), self.form_container, ft.Container(expand=True)],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        # --- Container chính sẽ hiển thị overlay ---
        self.content = self.overlay

    # --- Xử lý chọn file ---
    def _on_file_picked(self, e):
        if e.files:
            self.image_file = e.files[0].path
            self.image_preview.content = ft.Image(
                src=self.image_file, width=120, height=120, fit=ft.ImageFit.COVER
            )
            self.image_preview.update()

    # CHỈNH SỬA: nút submit gọi child _handle_submit, chỉ close khi True
    def submit_button_clicked(self, e):
        success = False
        if hasattr(self, "_handle_submit"):
            try:
                success = self._handle_submit(e)
            except Exception as ex:
                print(f"Lỗi khi submit: {ex}")

        if success:
            self.close()
            if self.page:
                self.page.update()


    def _handle_close(self, e):
        if self.on_close:
            self.on_close(e)
        self.close()

    # --- Mở form ---
    def open_form(self, page: ft.Page):
        self.page = page
        if self not in page.overlay:
            page.overlay.append(self)
        if self.image_picker not in page.overlay:
            page.overlay.append(self.image_picker)
        page.update()

    # --- Đóng form ---
    def close(self):
        if not self.page:
            print("⚠️ self.page is None, form cannot close properly.")
            return

        try:
            if self.image_picker and self.image_picker in self.page.overlay:
                self.page.overlay.remove(self.image_picker)

            if self in self.page.overlay:
                self.page.overlay.remove(self)

            self.page.update()
            print("✅ Form closed successfully.")
        except Exception as e:
            print(f"⚠️ Lỗi khi đóng form: {e}")


    # --- Thêm field ---
    def add_field(self, label_text: str, prefix_text: str = "", hint_text: str = ""):
        field = ft.TextField(
            label=label_text,
            prefix_text=prefix_text,
            hint_text=hint_text,
            border_color=self.default_border_color,
            focused_border_color=self.default_focused_border_color,
            bgcolor=self.default_field_bgcolor,
            color=self.default_field_color,
            border_radius=12,
            content_padding=ft.padding.all(12),
            text_size=14,
            cursor_color="#A94F8B",
            cursor_width=2,
            width=450,
        )
        self.fields.append(field)
        self.fields_column.controls.append(field)
        if self.fields_column.page:
            self.fields_column.update()
        return field
