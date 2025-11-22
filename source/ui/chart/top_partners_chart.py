import flet as ft
from typing import List, Dict
from decimal import Decimal

class TopPartnersChart(ft.Container):
    def __init__(self, top_suppliers: List[Dict], top_distributors: List[tuple]):
        super().__init__()
        self.top_suppliers = top_suppliers
        self.top_distributors = top_distributors
        self.width = 1170 # Tăng gấp đôi
        self.height = 300  # Đồng bộ chiều cao với biểu đồ tròn
        self.padding = 10

        self.content = ft.Column(
            [
                ft.Text("TOP 5 ĐỐI TÁC HÀNG ĐẦU", size=16, weight=ft.FontWeight.BOLD, color="#A94F8B"),
                ft.Row(
                    [
                        self._create_chart_column("Nhà Cung Cấp (Tổng tiền nhập)", self.top_suppliers, "#E76F51", "TongTienNhap", "TenCoSo", is_money=True),
                        ft.VerticalDivider(width=20, color="transparent"),
                        self._create_chart_column("Nhà Phân Phối (Số lần xuất)", self.top_distributors, "#264653", 2, 1)
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.START
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

    def _create_chart_column(self, title: str, data, color: str, value_key, name_key, is_money=False):
        bars = []
        max_value = 0
        
        # Tìm giá trị lớn nhất để chuẩn hóa
        if data:
            max_value = max(item[value_key] if isinstance(item, dict) else item[value_key] for item in data)

        if max_value == 0:
            max_value = 1 # Tránh chia cho 0

        for item in data:
            name = item[name_key] if isinstance(item, dict) else item[name_key]
            value = item[value_key] if isinstance(item, dict) else item[value_key]
            
            # Chuẩn hóa giá trị để nằm trong khoảng 0-100 cho thanh progress
            normalized_value = (value / max_value) * 100

            value_text = f"{value:,.0f} VNĐ" if is_money else str(value)

            bars.append(
                ft.Column(
                    [
                        ft.Text(name, size=11, weight=ft.FontWeight.BOLD, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Container(
                            content=ft.Text(value_text, size=10, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
                            width=float(normalized_value) * 3.0, # Tăng gấp đôi độ dài thanh
                            height=20,
                            bgcolor=color,
                            border_radius=5,
                            padding=ft.padding.only(left=5),
                            alignment=ft.alignment.center_left,
                        )
                    ],
                    spacing=2,
                    horizontal_alignment=ft.CrossAxisAlignment.START
                )
            )

        return ft.Column(
            [
                ft.Text(title, size=12, weight=ft.FontWeight.W_600),
                ft.Column(bars, spacing=8)
            ],
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )