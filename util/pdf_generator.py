import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

from source.models.PhieuNhapSach import PhieuNhapSach
from source.models.PhieuXuatSach import PhieuXuatSach
from util.get_absolute_path import get_absolute_path

class PDFGenerator:
    def __init__(self):
        self.font_name = 'Helvetica' # Font mặc định
        
        # Đăng ký font hỗ trợ tiếng Việt
        font_path_times = get_absolute_path("fonts/times.ttf")
        font_path_arial = get_absolute_path("fonts/arial.ttf")

        if os.path.exists(font_path_times):
            pdfmetrics.registerFont(TTFont('TimesNewRoman', font_path_times))
            self.font_name = 'TimesNewRoman' # Ưu tiên Times New Roman
        elif os.path.exists(font_path_arial):
            pdfmetrics.registerFont(TTFont('Arial', font_path_arial))
            self.font_name = 'Arial' # Nếu không có thì dùng Arial
        else:
            print(f"Cảnh báo: Không tìm thấy font 'times.ttf' hoặc 'arial.ttf'. Sử dụng font mặc định (có thể lỗi tiếng Việt).")

        self.styles = getSampleStyleSheet()

    def _draw_header(self, c: canvas.Canvas, title: str):
        c.setFont(self.font_name, 24)
        c.drawCentredString(A4[0] / 2, A4[1] - 50, title)

    def _draw_info(self, c: canvas.Canvas, receipt: PhieuNhapSach):
        c.setFont(self.font_name, 12)
        c.drawString(70, A4[1] - 100, f"Mã phiếu: {receipt.ID_PhieuNhap}")
        c.drawString(70, A4[1] - 120, f"Ngày nhập: {receipt.NgayNhap.strftime('%d/%m/%Y')}")
        c.drawString(70, A4[1] - 140, f"Nhân viên: {receipt.TenNhanVien}")
        c.drawString(70, A4[1] - 160, f"Nhà cung cấp: {receipt.TenNguonNhap}")

    def _draw_table(self, c: canvas.Canvas, receipt: PhieuNhapSach):
        # Dữ liệu bảng
        data = [
            ["STT", "Tên Sách", "Số Lượng", "Đơn Giá", "Thành Tiền"]
        ]
        for i, detail in enumerate(receipt.Danhsachchitietnhap):
            row = [
                str(i + 1),
                detail.sach.TenSach,
                str(detail.SoLuong),
                f"{detail.DonGia:,.0f}",
                f"{detail.ThanhTien:,.0f}"
            ]
            data.append(row)

        # Tạo bảng
        table = Table(data, colWidths=[40, 250, 70, 80, 80])

        # Style cho bảng
        style = TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black), # Đổi màu chữ tiêu đề thành đen
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), self.font_name),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), self.font_name),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
        table.setStyle(style)

        # Vẽ bảng lên canvas
        # Lấy kích thước thực tế của bảng để xác định vị trí vẽ chính xác
        _width, table_height = table.wrapOn(c, A4[0] - 140, A4[1]) # 140 = 70 margin left + 70 margin right
        y_position = A4[1] - 190 - table_height
        table.drawOn(c, 70, y_position)
        
        return table_height # Trả về chiều cao thực tế của bảng để tính vị trí footer

    def _draw_footer(self, c: canvas.Canvas, receipt: PhieuNhapSach, table_height: int):
        c.setFont(self.font_name, 12)
        y_position = A4[1] - 190 - table_height - 30
        
        total_quantity_text = f"Tổng số lượng: {receipt.TongSoLuong}"
        total_amount_text = f"Tổng thành tiền: {receipt.TongTien:,.0f} VNĐ"

        c.drawRightString(A4[0] - 70, y_position, total_quantity_text)
        c.drawRightString(A4[0] - 70, y_position - 20, total_amount_text)

        c.setFont(self.font_name, 10)
        c.drawCentredString(A4[0] / 2, 50, "Cảm ơn và hẹn gặp lại!")

    def generate_import_receipt_pdf(self, receipt: PhieuNhapSach, file_path: str):
        try:
            c = canvas.Canvas(file_path, pagesize=A4)
            
            self._draw_header(c, "PHIẾU NHẬP SÁCH")
            self._draw_info(c, receipt)
            table_height = self._draw_table(c, receipt)
            self._draw_footer(c, receipt, table_height)
            
            c.showPage()
            c.save()
            return True
        except Exception as e:
            print(f"Lỗi khi tạo file PDF: {e}")
            return False

    # --- Methods for Export Receipt ---

    def _draw_info_export(self, c: canvas.Canvas, receipt: PhieuXuatSach):
        c.setFont(self.font_name, 12)
        c.drawString(70, A4[1] - 100, f"Mã phiếu: {receipt.ID_PhieuXuat}")
        c.drawString(70, A4[1] - 120, f"Ngày xuất: {receipt.NgayXuat.strftime('%d/%m/%Y')}")
        c.drawString(70, A4[1] - 140, f"Nhân viên: {receipt.TenNhanVien}")
        c.drawString(70, A4[1] - 160, f"Nhà phân phối: {receipt.TenNhaPhanPhoi}")

    def _draw_table_export(self, c: canvas.Canvas, receipt: PhieuXuatSach):
        data = [["STT", "Tên Sách", "Số Lượng", "Đơn Giá", "Thành Tiền"]]
        for i, detail in enumerate(receipt.Danhsachchitietxuat):
            row = [
                str(i + 1),
                detail.sach.TenSach,
                str(detail.SoLuong),
                f"{detail.DonGia:,.0f}",
                f"{detail.ThanhTien:,.0f}"
            ]
            data.append(row)

        table = Table(data, colWidths=[40, 250, 70, 80, 80])
        style = TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black), # Đổi màu chữ tiêu đề thành đen
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), self.font_name),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), self.font_name),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
        table.setStyle(style)

        _width, table_height = table.wrapOn(c, A4[0] - 140, A4[1])
        y_position = A4[1] - 190 - table_height
        table.drawOn(c, 70, y_position)
        return table_height

    def _draw_footer_export(self, c: canvas.Canvas, receipt: PhieuXuatSach, table_height: int):
        c.setFont(self.font_name, 12)
        y_position = A4[1] - 190 - table_height - 30
        total_quantity_text = f"Tổng số lượng: {receipt.TongSoLuong}"
        total_amount_text = f"Tổng thành tiền: {receipt.TongTien:,.0f} VNĐ"
        c.drawRightString(A4[0] - 70, y_position, total_quantity_text)
        c.drawRightString(A4[0] - 70, y_position - 20, total_amount_text)
        c.setFont(self.font_name, 10)
        c.drawCentredString(A4[0] / 2, 50, "Cảm ơn và hẹn gặp lại!")

    def generate_export_receipt_pdf(self, receipt: PhieuXuatSach, file_path: str):
        try:
            c = canvas.Canvas(file_path, pagesize=A4)
            self._draw_header(c, "PHIẾU XUẤT SÁCH")
            self._draw_info_export(c, receipt)
            table_height = self._draw_table_export(c, receipt)
            self._draw_footer_export(c, receipt, table_height)
            c.showPage()
            c.save()
            return True
        except Exception as e:
            print(f"Lỗi khi tạo file PDF: {e}")
            return False