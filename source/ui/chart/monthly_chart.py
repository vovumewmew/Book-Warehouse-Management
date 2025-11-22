import flet as ft
from typing import List, Tuple
from decimal import Decimal
import datetime

class MonthlyChart(ft.Container):
    def __init__(self, import_data: List[Tuple[int, int, Decimal]], export_data: List[Tuple[int, int, Decimal]]):
        super().__init__()
        self.width = 800  # Giới hạn chiều rộng của biểu đồ
        self.height = 400 # Giới hạn chiều cao của biểu đồ
        self.padding = ft.padding.only(top=10, left=50, right=20) # Tăng mạnh padding trái

        self.import_data = {item[0]: item[2] for item in import_data}
        self.export_data = {item[0]: item[2] for item in export_data}
        
        self.bar_groups = self._create_bar_groups()
        
        self.chart = ft.BarChart(
            bar_groups=self.bar_groups,
            border=ft.border.all(1, ft.Colors.GREY_400),
            left_axis=ft.ChartAxis(
                labels_size=40,
                title=ft.Text("Tổng tiền (VNĐ)"),
                title_size=12,
                labels_interval=self._calculate_interval(),
            ),
            bottom_axis=ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(value=i, label=ft.Text(f"T{i+1}", size=14)) for i in range(12)
                ],
                labels_size=40,
            ),
            horizontal_grid_lines=ft.ChartGridLines(
                interval=self._calculate_interval(), color=ft.Colors.GREY_300, width=1
            ),
            tooltip_bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.WHITE),
            max_y=self._get_max_y(),
            interactive=True,
            expand=True,
        )
        
        self.content = ft.Column(
            [
                ft.Text(f"BIỂU ĐỒ HOẠT ĐỘNG NĂM {datetime.date.today().year}", size=18, weight=ft.FontWeight.BOLD, color="#A94F8B"),
                self.chart
            ]
        )

    def _get_max_y(self):
        max_import = max(self.import_data.values()) if self.import_data else 0
        max_export = max(self.export_data.values()) if self.export_data else 0
        max_val = max(max_import, max_export)
        if max_val == 0:
            return 1000000 # Giá trị mặc định nếu không có dữ liệu
        
        # Làm tròn lên đến triệu, chục triệu, trăm triệu... gần nhất
        power = 10 ** (len(str(int(max_val))) - 1)
        return (int(max_val / power) + 1) * power

    def _calculate_interval(self):
        return self._get_max_y() / 5

    def _create_bar_groups(self) -> List[ft.BarChartGroup]:
        groups = []
        for i in range(12):
            import_val = self.import_data.get(i + 1, 0)
            export_val = self.export_data.get(i + 1, 0)

            groups.append(
                ft.BarChartGroup(
                    x=i,
                    bar_rods=[
                        ft.BarChartRod(
                            from_y=0,
                            to_y=float(import_val),
                            width=18,
                            color="#E76F51",
                            tooltip=f"Nhập: {import_val:,.0f} VNĐ",
                            border_radius=0,
                        ),
                        ft.BarChartRod(
                            from_y=0,
                            to_y=float(export_val),
                            width=18,
                            color="#264653",
                            tooltip=f"Xuất: {export_val:,.0f} VNĐ",
                            border_radius=0,
                        ),
                    ],
                )
            )
        return groups