import flet as ft

class DashboardCard(ft.Container):
    def __init__(self, title: str, value: str, icon: ft.Icon, color: str, on_click=None):
        super().__init__()
        self.on_click = on_click
        self.width = 220
        self.height = 120
        self.bgcolor = color
        self.border_radius = 16
        self.padding = 20
        self.shadow = ft.BoxShadow(
            blur_radius=15,
            spread_radius=-5,
            color=ft.Colors.with_opacity(0.3, color),
            offset=ft.Offset(0, 8),
        )

        self.content = ft.Row(
            [
                ft.Column(
                    [
                        ft.Text(
                            value,
                            size=28,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                        ),
                        ft.Text(
                            title,
                            size=14,
                            color=ft.Colors.WHITE,
                            weight=ft.FontWeight.W_500,
                            opacity=0.9
                        ),
                    ],
                    spacing=2,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Container(
                    icon,
                    width=48,
                    height=48,
                    bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                    border_radius=12,
                    alignment=ft.alignment.center,
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )