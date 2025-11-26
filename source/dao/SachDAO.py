from typing import List, Optional
import logging
from decimal import Decimal

from config.basedao import BaseDAO
from config.db_connection import DatabaseConnection

from source.models.Sach import Sach

from mysql.connector import Error

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class SachDAO(BaseDAO):
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self.conn = db.get_connection()

    def get_all(self) -> List[Sach]:
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM sach WHERE TinhKhaDung = 'Khả dụng' ORDER BY CAST(SUBSTRING(ID_Sach, 2) AS UNSIGNED)")
            rows = cursor.fetchall()
            print(f"✅ Số sách còn khả dụng lấy được từ DB: {len(rows)}")
            return [Sach.from_dict(row) for row in rows]
        except Error as e:
            logging.error(f"Đã có lỗi khi lấy dữ liệu sách: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def count_out_of_stock_books(self) -> int:
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sach WHERE SoLuong = 0 AND TinhKhaDung = 'Khả dụng'")
            result = cursor.fetchone()
            return result[0] if result and result[0] else 0
        except Error as e:
            logging.error(f"Lỗi khi đếm sách đã hết hàng: {e}")
            return 0
        finally:
            if cursor:
                cursor.close()
        
    def get_unavailable(self) -> List[Sach]:
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM sach WHERE TinhKhaDung = 'Không khả dụng' ORDER BY CAST(SUBSTRING(ID_Sach, 2) AS UNSIGNED)")
            rows = cursor.fetchall()
            print(f"✅ Số sách không khả dụng lấy được từ DB: {len(rows)}")
            return [Sach.from_dict(row) for row in rows]
        except Error as e:
            logging.error(f"Đã có lỗi khi lấy dữ liệu sách đã xóa: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def insert(self, sach: Sach) -> bool:
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = """ insert into sach (ID_Sach, TenSach, TacGia, TheLoai, NamXuatBan,NhaXuatBan, NgonNgu, SoLuong, TrangThai, Gia, TinhKhaDung, HinhAnh)
                        values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (
                sach.ID_Sach,
                sach.TenSach,
                sach.TacGia,
                sach.TheLoai,
                sach.NamXuatBan,
                sach.NhaXuatBan,
                sach.NgonNgu,
                sach.SoLuong,
                sach.TrangThai,
                sach.Gia,
                sach.TinhKhaDung,
                sach.HinhAnh,
            ))
            self.conn.commit()
            return True
        except Error as e:
            self.conn.rollback()
            logging.error(f"Lỗi khi thêm sách: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def update(self, sach: Sach) -> bool:
        cursor = None
        try: 
            cursor = self.conn.cursor()
            cursor.execute(""" update sach
                               set TenSach = %s, TacGia = %s, TheLoai = %s, NamXuatBan = %s,NhaXuatBan = %s, NgonNgu = %s, SoLuong = %s, TrangThai = %s, Gia = %s, TinhKhaDung = %s, HinhAnh=%s
                               where ID_Sach = %s""", (
                                   sach.TenSach,
                                   sach.TacGia,
                                   sach.TheLoai,
                                   sach.NamXuatBan,
                                   sach.NhaXuatBan,
                                   sach.NgonNgu,
                                   sach.SoLuong,
                                   sach.TrangThai,
                                   sach.Gia,
                                   sach.TinhKhaDung,
                                   sach.HinhAnh,
                                   sach.ID_Sach
                               ))
            self.conn.commit()
            return cursor.rowcount > 0
        except Error as e:
            self.conn.rollback()
            logging.error(f"Đã có lỗi khi cập nhật sách: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
        
    def find_by_key(self, ma_sach: str) -> Optional[Sach]:
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute("select * from sach where ID_Sach = %s", (ma_sach,))
            row = cursor.fetchone()
            if not row:
                logging.error(f"Không tìm thấy sách có mã {ma_sach}")
                return None
            return Sach.from_dict(row)
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi tìm sách theo mã: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

    def search_by_name(self, ten_sach: str) -> List[Sach]:
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM sach WHERE TenSach LIKE %s AND TinhKhaDung = 'Khả dụng' ORDER BY CAST(SUBSTRING(ID_Sach, 2) AS UNSIGNED)", (f"%{ten_sach}%",))
            rows = cursor.fetchall()
            return [Sach.from_dict(row) for row in rows]
        except Error as e:
            logging.error(f"Lỗi khi tìm kiếm sách: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def delete(self, ma_sach: str) -> bool:
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("update sach set TinhKhaDung = 'Không khả dụng' where ID_Sach = %s", (ma_sach,))
            self.conn.commit()
            return cursor.rowcount > 0
        except Error as e:
            self.conn.rollback()
            logging.error(f"Đã có lỗi khi xóa: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def completely_delete(self, ma_sach: str) -> bool:
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("delete from sach where ID_Sach = %s", (ma_sach,))
            self.conn.commit()
            return cursor.rowcount > 0
        except Error as e:
            self.conn.rollback()
            logging.error(f"Đã có lỗi khi xóa: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
    
    #các hàm nâng cao
    
    def restore(self, id_sach: str) -> bool:
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("update sach set TinhKhaDung = 'Khả dụng' where ID_Sach = %s", (id_sach,))
            self.conn.commit()
            return cursor.rowcount > 0
        except Error as e:
            self.conn.rollback()
            logging.error(f"Đã xảy ra lỗi khi khôi phục lại sách: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def filter_by_category(self, theloai: str) -> List[Sach]:
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM sach WHERE TheLoai = %s AND TinhKhaDung = 'Khả dụng' ORDER BY CAST(SUBSTRING(ID_Sach, 2) AS UNSIGNED)", (theloai,))
            rows = cursor.fetchall()
            return [Sach.from_dict(row) for row in rows]
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi lọc theo thể loại: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_low_stock_books(self, soluong: int = 5) -> List[Sach]:
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute("select * from sach where SoLuong <= %s and SoLuong > 0 and TinhKhaDung = 'Khả dụng'", (soluong,))
            rows = cursor.fetchall()
            return [Sach.from_dict(row) for row in rows]
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi tìm các sách sắp hết: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def update_stock(self, ma_sach: str, so_luong_moi: int) -> bool:
        cursor = None
        try:
            cursor = self.conn.cursor()
            # Logic mới: Tự động cập nhật trạng thái dựa trên số lượng
            trang_thai_moi = 'Còn hàng' if so_luong_moi > 0 else 'Hết hàng'
            cursor.execute("UPDATE sach SET SoLuong = %s, TrangThai = %s WHERE ID_Sach = %s", (so_luong_moi, trang_thai_moi, ma_sach))
            self.conn.commit()
            return cursor.rowcount > 0
        except Error as e:
            self.conn.rollback()
            logging.error(f"Lỗi khi cập nhật số lượng sách: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def check_exists(self, id_sach: str) -> bool:
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("select 1 from sach where ID_Sach = %s", (id_sach,))
            return cursor.fetchone() is not None
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi kiểm tra sự tồn tại sách {id_sach}: {e}")
            return False
        finally:
            if cursor:
                cursor.close() 

    def count_books(self) -> int:
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("select count(*) from sach where TinhKhaDung = 'Khả dụng'") 
            return cursor.fetchone()[0]
        except Error as e:
            logging.error(f"Lỗi khi đếm sách: {e}")
            return 0
        finally:
            if cursor:
                cursor.close()
            
    def get_total_stock_value(self) -> Decimal:
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT SUM(SoLuong * Gia) FROM sach WHERE TinhKhaDung = 'Khả dụng'")
            result = cursor.fetchone()
            return result[0] if result and result[0] else Decimal('0')
        except Error as e:
            logging.error(f"Lỗi khi tính tổng giá trị kho: {e}")
            return Decimal('0')
        finally:
            if cursor:
                cursor.close()

    def count_low_stock_books(self, threshold: int = 5) -> int:
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sach WHERE SoLuong <= %s AND TinhKhaDung = 'Khả dụng' AND SoLuong > 0", (threshold,))
            result = cursor.fetchone()
            return result[0] if result and result[0] else 0
        except Error as e:
            logging.error(f"Lỗi khi đếm sách sắp hết hàng: {e}")
            return 0
        finally:
            if cursor:
                cursor.close()

    def get_category_statistics(self) -> List[tuple[str, int]]:
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = """SELECT TheLoai, COUNT(*) as SoLuong
                       FROM sach
                       WHERE TinhKhaDung = 'Khả dụng' AND TheLoai IS NOT NULL AND TheLoai != ''
                       GROUP BY TheLoai
                       ORDER BY SoLuong DESC"""
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            logging.error(f"Lỗi khi thống kê sách theo thể loại: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
        
