import flet as ft
from typing import List, Tuple

class CategoryPieChart(ft.Container):
    def __init__(self, data: List[Tuple[str, int]]):
        super().__init__()
        self.data = data
        self.width = 600   
        self.height = 375 
        self.padding = 10

        # Bảng màu đẹp mắt
        self.colors = [
            ft.Colors.PINK_200, ft.Colors.PURPLE_200, ft.Colors.INDIGO_200,
            ft.Colors.BLUE_200, ft.Colors.CYAN_200, ft.Colors.TEAL_200,
            ft.Colors.LIME_200, ft.Colors.AMBER_200
        ]

        self.chart = ft.PieChart(
            sections=self._create_sections(),
            sections_space=1,
            center_space_radius=60,
            on_chart_event=self.on_chart_event,
            expand=True
        )

        self.content = ft.Column(
            [
                ft.Text("TỶ LỆ SÁCH THEO THỂ LOẠI", size=16, weight=ft.FontWeight.BOLD, color="#A94F8B"),
                self.chart
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5 # Giảm khoảng cách giữa tiêu đề và biểu đồ
        )

    def _create_sections(self) -> List[ft.PieChartSection]:
        sections = []
        total_books = sum(item[1] for item in self.data)
        if total_books == 0:
            return []

        for i, (category, count) in enumerate(self.data[:8]): # Chỉ lấy top 8
            percentage = (count / total_books) * 100
            sections.append(
                ft.PieChartSection(
                    value=percentage,
                    title=f"{percentage:.1f}%",
                    title_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                    color=self.colors[i % len(self.colors)],
                    radius=80,
                    badge=ft.Container(ft.Text(category, size=11), bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.WHITE), padding=3, border_radius=5),
                    badge_position=0.98
                )
            )
        return sections

    def on_chart_event(self, e: ft.PieChartEvent):
        for idx, section in enumerate(self.chart.sections):
            section.radius = 90 if e.type == "hover" and e.section_index == idx else 80
        self.chart.update()