from typing import List, Optional
import logging

from config.basedao import BaseDAO
from config.db_connection import DatabaseConnection

from source.models.NguonNhapSach import NguonNhapSach

from mysql.connector import Error

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class NguonNhapSachDAO(BaseDAO):
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self.conn = db.get_connection()

    def get_all(self) -> List[NguonNhapSach]:
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary= True)
            cursor.execute("select * from nguonnhapsach where TinhKhaDung = 'Khả dụng'")
            rows = cursor.fetchall()
            return [NguonNhapSach.from_dict(row) for row in rows]
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi lấy dữ liệu nguồn nhập sách khả dụng: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_all_unavailable(self) -> List[NguonNhapSach]:
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary= True)
            cursor.execute("select * from nguonnhapsach where TinhKhaDung = 'Không khả dụng'")
            rows = cursor.fetchall()
            return [NguonNhapSach.from_dict(row) for row in rows]
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi lấy dữ liệu nguồn nhập sách không khả dụng: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def insert(self, nguonnhapsach: NguonNhapSach) -> bool:
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = """insert into nguonnhapsach (ID_NguonNhap, TenCoSo, HinhThucNhap, DiaChi, SoDienThoai, Email, TrangThaiNCC, TinhKhaDung, HinhAnh)
                       values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (
                nguonnhapsach.ID_NguonNhap,
                nguonnhapsach.TenCoSo,
                nguonnhapsach.HinhThucNhap,
                nguonnhapsach.DiaChi,
                nguonnhapsach.SoDienThoai,
                nguonnhapsach.Email,
                nguonnhapsach.TrangThaiNCC,
                nguonnhapsach.TinhKhaDung,
                nguonnhapsach.HinhAnh,
            ))
            self.conn.commit()
            logging.info(f"Đã thêm nguồn nhập sách có mã: {nguonnhapsach.ID_NguonNhap}")
            return True
        except Error as e:
            self.conn.rollback()
            if "Duplicate entry" in str(e):
                logging.warning(f"Mã nguồn nhập '{nguonnhapsach.ID_NguonNhap}' đã tồn tại.")
                return False
            else:
                logging.error(f"Đã xảy ra lỗi khi thêm nguồn nhập sách: {e}")
                return False
        finally:
            if cursor:
                cursor.close()
    
    def update(self, nguonnhapsach: NguonNhapSach) -> bool:
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = """update nguonnhapsach
                       set TenCoSo = %s, HinhThucNhap = %s, DiaChi = %s, SoDienThoai = %s, Email = %s, TrangThaiNCC = %s, TinhKhaDung = %s, HinhAnh = %s
                       where ID_NguonNhap = %s"""
            cursor.execute(query, (
                nguonnhapsach.TenCoSo,
                nguonnhapsach.HinhThucNhap,
                nguonnhapsach.DiaChi,
                nguonnhapsach.SoDienThoai,
                nguonnhapsach.Email,
                nguonnhapsach.TrangThaiNCC,
                nguonnhapsach.TinhKhaDung,
                nguonnhapsach.HinhAnh,
                nguonnhapsach.ID_NguonNhap
            ))
            self.conn.commit()
            return cursor.rowcount > 0
        except Error as e:
            self.conn.rollback()
            logging.error(f"Đã xảy ra lỗi khi cập nhật thông tin cho nguồn nhập sách: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
    
    def find_by_key(self, ma_nguonnhapsach: str) -> Optional[NguonNhapSach]:
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary= True)
            cursor.execute("select * from nguonnhapsach where ID_NguonNhap = %s", (ma_nguonnhapsach,))
            row = cursor.fetchone()
            if not row:
                logging.error(f"Không tìm thấy nguồn nhập sách có mã {ma_nguonnhapsach}")
                return None
            return NguonNhapSach.from_dict(row) 
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi tìm nguồn nhập sách theo mã: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

    def delete(self, ma_nguonnhapsach: str) -> bool:
        cursor = None
        try: 
            cursor = self.conn.cursor()
            cursor.execute("update nguonnhapsach set TinhKhaDung = 'Không khả dụng' where ID_NguonNhap = %s", (ma_nguonnhapsach,))
            self.conn.commit()
            return cursor.rowcount > 0
        except Error as e:
            self.conn.rollback()
            logging.error(f"Đã xảy ra lỗi khi xóa mềm nguồn nhập sách: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def completely_delete(self, ma_nguonnhapsach: str) -> bool:
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("delete from nguonnhapsach where ID_NguonNhap = %s", (ma_nguonnhapsach,))
            self.conn.commit()
            return cursor.rowcount > 0
        except Error as e:
            self.conn.rollback()
            logging.error(f"Đã xảy ra lỗi khi xóa hoàn toàn nguồn nhập sách: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    #các hàm nâng cao

    def check_exists(self, id_nguonhapsach: str) -> bool:
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("select 1 from nguonnhapsach where ID_NguonNhap = %s", (id_nguonhapsach,))
            return cursor.fetchone() is not None
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi kiểm tra sự tồn tại nguồn nhập sách {id_nguonhapsach}: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def restore(self, id_nguonnhap: str) -> bool:
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("update nguonnhapsach set TinhKhaDung = 'Khả dụng' where ID_NguonNhap = %s", (id_nguonnhap,))
            self.conn.commit()
            return cursor.rowcount > 0
        except Error as e:
            self.conn.rollback()
            logging.error(f"Đã xảy ra lỗi khi khôi phục lại nguồn nhập sách: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
        
    def get_top_suppliers_by_orders(self, limit: int = 5) -> List[dict]:
        """Trả về top nhà cung cấp có số phiếu nhập nhiều nhất.
           Kết quả gồm: ID_NguonNhap, TenCoSo, SoLanNhap."""
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = """SELECT ncc.ID_NguonNhap, ncc.TenCoSo, COUNT(pn.ID_PhieuNhap) AS SoLanNhap
                       FROM nguonnhapsach ncc
                       JOIN phieunhapsach pn ON ncc.ID_NguonNhap = pn.ID_NguonNhap
                       GROUP BY ncc.ID_NguonNhap, ncc.TenCoSo
                       ORDER BY SoLanNhap DESC
                       LIMIT %s"""
            cursor.execute(query, (limit,))
            rows = cursor.fetchall()
            return [] if not rows else rows
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi lấy về các nhà cung cấp có nhiều phiếu nhập nhất: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_supplier_performance_summary(self) -> List[dict]:
        """Trả về danh sách thống kê hiệu suất của từng nhà cung cấp:
            - Số phiếu nhập
            - Tổng số lượng
            - Tổng tiền"""
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = """SELECT ncc.ID_NguonNhap, ncc.TenCoSo,
                            COUNT(pn.ID_PhieuNhap) AS SoPhieuNhap,
                            COALESCE(SUM(pn.TongSoLuong), 0) AS TongSoLuong,
                            COALESCE(SUM(pn.TongTien), 0) AS TongTien
                        FROM nguonnhapsach ncc
                        LEFT JOIN phieunhapsach pn ON ncc.ID_NguonNhap = pn.ID_NguonNhap
                        GROUP BY ncc.ID_NguonNhap, ncc.TenCoSo
                        ORDER BY TongTien DESC"""
            cursor.execute(query)
            rows = cursor.fetchall()
            return [] if not rows else rows
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi thống kê hiệu suất của các nhà cung cấp: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_total_suppliers_by_status(self) -> dict:
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = """select TinhKhaDung, count(*) as SoLuong
                       from nguonnhapsach
                       group by TinhKhaDung"""
            cursor.execute(query)
            rows = cursor.fetchall()
            return {row["TinhKhaDung"]: row["SoLuong"] for row in rows}
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi xuất ra số lượng nhà cung cấp theo tình trạng: {e}")
            return {}
        finally:
            if cursor:
                cursor.close()

    def get_statistics_by_status(self) -> List[dict]:
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = """select TrangThaiNCC, count(*) as SoLuong
                       from nguonnhapsach
                       group by TrangThaiNCC"""
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi đếm các nhà cung cấp còn khả dụng và không khả dụng: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def count_all(self) -> int:
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM nguonnhapsach WHERE TinhKhaDung = 'Khả dụng'")
            result = cursor.fetchone()
            return result[0] if result else 0
        except Error as e:
            logging.error(f"Lỗi khi đếm nhà cung cấp: {e}")
            return 0
        finally:
            if cursor:
                cursor.close()