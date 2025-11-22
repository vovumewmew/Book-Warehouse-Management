from typing import List, Optional
from datetime import date
from decimal import Decimal
import logging

from config.db_connection import DatabaseConnection
from config.basedao import BaseDAO

from source.models.PhieuNhapSach import PhieuNhapSach

from mysql.connector import Error

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class PhieuNhapSachDAO(BaseDAO):
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self.conn = db.get_connection()

    def get_all(self) -> List[PhieuNhapSach]:
        cursor = None
        try: 
            cursor = self.conn.cursor(dictionary= True)
            # JOIN để lấy thông tin tên nhân viên và tên nguồn nhập
            query = """
                SELECT pns.*, nv.HoTen as TenNhanVien, nns.TenCoSo as TenNguonNhap
                FROM phieunhapsach pns
                JOIN nhanvien nv ON pns.ID_NhanVien = nv.ID_NhanVien
                JOIN nguonnhapsach nns ON pns.ID_NguonNhap = nns.ID_NguonNhap
                ORDER BY CAST(SUBSTRING(pns.ID_PhieuNhap, 3) AS UNSIGNED)
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            return [PhieuNhapSach.from_dict(row) for row in rows]
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi lấy dữ liệu phiếu nhập sách: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
    
    def insert(self, phieunhapsach: PhieuNhapSach) -> bool:
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = """insert into phieunhapsach (ID_PhieuNhap, NgayNhap, TongSoLuong, TongTien, ID_NhanVien, ID_NguonNhap)
                       values (%s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (
                phieunhapsach.ID_PhieuNhap,
                phieunhapsach.NgayNhap,
                phieunhapsach.TongSoLuong,
                phieunhapsach.TongTien,
                phieunhapsach.nhan_vien_nhap.ID_NhanVien,
                phieunhapsach.nguon_nhap.ID_NguonNhap
            ))
            self.conn.commit()
            return True
        except Error as e:
            self.conn.rollback()
            logging.error(f"Đã xảy ra lỗi khi thêm 1 phiếu nhập sách: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def update(self, phieunhapsach: PhieuNhapSach) -> bool:
        cursor = None
        try:
            print(f"--- DEBUG (DAO): PhieuNhapSachDAO.update được gọi cho ID: {phieunhapsach.ID_PhieuNhap}")
            cursor = self.conn.cursor()
            query = """update phieunhapsach
                       set NgayNhap = %s, ID_NhanVien = %s, ID_NguonNhap = %s
                       where ID_PhieuNhap = %s"""
            cursor.execute(query, (
                phieunhapsach.NgayNhap,
                phieunhapsach.nhan_vien_nhap.ID_NhanVien,
                phieunhapsach.nguon_nhap.ID_NguonNhap,
                phieunhapsach.ID_PhieuNhap
            ))
            print(f"--- DEBUG (DAO): cursor.rowcount = {cursor.rowcount}")
            return cursor.rowcount > 0
        except Error as e:
            print(f"--- DEBUG (DAO): Lỗi SQL khi cập nhật: {e}")
            logging.error(f"Đã xảy ra lỗi khi cập nhật thông tin phiếu nhập: {e}")
            raise e # Ném lỗi ra để Service bắt và rollback
        finally:
            if cursor:
                cursor.close()

    def find_by_key(self, id_phieunhap) -> Optional[PhieuNhapSach]:
        cursor = None
        try:
            from source.dao.ChiTietPhieuNhapDAO import ChiTietPhieuNhapDAO
            cursor = self.conn.cursor(dictionary=True)
            query = """
                SELECT pns.*, nv.HoTen as TenNhanVien, nns.TenCoSo as TenNguonNhap
                FROM phieunhapsach pns
                JOIN nhanvien nv ON pns.ID_NhanVien = nv.ID_NhanVien
                JOIN nguonnhapsach nns ON pns.ID_NguonNhap = nns.ID_NguonNhap
                WHERE pns.ID_PhieuNhap = %s
            """
            cursor.execute(query, (id_phieunhap,))
            row = cursor.fetchone()
            if not row:
                logging.error(f"Không thể tìm thấy phiếu nhập có mã: {id_phieunhap}")
                return None
            phieu = PhieuNhapSach.from_dict(row)
            ct_dao = ChiTietPhieuNhapDAO(self.db)
            phieu.Danhsachchitietnhap = ct_dao.get_all_for_phieu(phieu) # Sử dụng hàm mới
            return phieu
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi tìm kiếm phiếu nhập: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

    def delete(self, id_phieunhap) -> bool:
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("delete from phieunhapsach where ID_PhieuNhap = %s", (id_phieunhap,))
            self.conn.commit()
            return cursor.rowcount > 0
        except Error as e:
            self.conn.rollback()
            logging.error(f"Đã xảy ra lỗi khi xóa phiếu nhập: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def get_total(self, id_phieunhap: str) -> tuple[int, Decimal]:
        try:
            from source.dao.ChiTietPhieuNhapDAO import ChiTietPhieuNhapDAO
            chitiet_dao = ChiTietPhieuNhapDAO(self.db)
            list_ct = chitiet_dao.get_all(id_phieunhap)
            if not list_ct:
                return 0, 0.0
            tong_sl = sum(ct.SoLuong for ct in list_ct)
            tong_tien = sum(ct.ThanhTien for ct in list_ct)
            return tong_sl, tong_tien
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi tính tổng số lượng và giá tiền: {e}")
            return 0, 0.0
        
    def auto_update_total(self, id_phieunhap: str) -> bool:
        cursor = None
        try:
            tong_sl, tong_tien = self.get_total(id_phieunhap)
            cursor = self.conn.cursor()
            query = """update phieunhapsach
                       set TongSoLuong = %s, TongTien = %s
                       where ID_PhieuNhap = %s"""
            cursor.execute(query, (tong_sl, tong_tien, id_phieunhap))
            self.conn.commit()
            return True
        except Error as e:
            self.conn.rollback()
            logging.error(f"Lỗi khi cập nhật tổng của phiếu nhập {id_phieunhap}: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    #các hàm nâng cao

    def get_recent(self, limit: int = 10) -> List[PhieuNhapSach]:
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary=True)
            query = """
                SELECT pns.*, nv.HoTen as TenNhanVien, nns.TenCoSo as TenNguonNhap
                FROM phieunhapsach pns
                JOIN nhanvien nv ON pns.ID_NhanVien = nv.ID_NhanVien
                JOIN nguonnhapsach nns ON pns.ID_NguonNhap = nns.ID_NguonNhap
                ORDER BY pns.NgayNhap DESC LIMIT %s
            """
            cursor.execute(query, (limit,))
            rows = cursor.fetchall()
            return [PhieuNhapSach.from_dict(row) for row in rows]
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi lấy {limit} phiếu nhập gần nhất: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
    
    def search_by_date_range(self, start_date: date, end_date: date) -> List[PhieuNhapSach]:
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary=True)
            query = """
                SELECT pns.*, nv.HoTen as TenNhanVien, nns.TenCoSo as TenNguonNhap
                FROM phieunhapsach pns
                JOIN nhanvien nv ON pns.ID_NhanVien = nv.ID_NhanVien
                JOIN nguonnhapsach nns ON pns.ID_NguonNhap = nns.ID_NguonNhap
                WHERE pns.NgayNhap BETWEEN %s AND %s ORDER BY pns.NgayNhap ASC"""
            cursor.execute(query, (start_date, end_date, ))
            rows = cursor.fetchall()
            return [PhieuNhapSach.from_dict(row) for row in rows]
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi tìm các phiếu nhập từ ngày {start_date} đến ngày {end_date}: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_by_id_nhanvien(self, id_nhanvien: str) -> List[PhieuNhapSach]:
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary=True)
            query = """
                SELECT pns.*, nv.HoTen as TenNhanVien, nns.TenCoSo as TenNguonNhap
                FROM phieunhapsach pns
                JOIN nhanvien nv ON pns.ID_NhanVien = nv.ID_NhanVien
                JOIN nguonnhapsach nns ON pns.ID_NguonNhap = nns.ID_NguonNhap
                WHERE pns.ID_NhanVien = %s"""
            cursor.execute(query, (id_nhanvien,))
            rows = cursor.fetchall()
            return [PhieuNhapSach.from_dict(row) for row in rows]
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi tìm phiếu nhập bằng mã nhân viên {id_nhanvien}: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_total_import_cost(self, start_date: date, end_date: date) -> Decimal:
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = """select sum(TongTien) as TongDoanhThu
                       from phieunhapsach
                       where NgayNhap between %s and %s"""
            cursor.execute(query, (start_date, end_date,))
            row = cursor.fetchone()
            return row[0] if row and row[0] else 0.0
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi tính tổng tiền nhập trong khoảng {start_date} tới {end_date}: {e}")
            return 0.0
        finally:
            if cursor:
                cursor.close()
    
    def count_by_employee(self) -> List[tuple[str, int]]:
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = """select ID_NhanVien, count(*) as TongSoPhieu
                       from phieunhapsach
                       group by ID_NhanVien"""
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi thống kê số phiếu xuất theo nhân viên: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_monthly_import_cost(self, year: int) -> List[tuple[int, Decimal]]:
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = """select month(NgayNhap) as Thang, sum(TongTien) as TongChiPhi
                       from phieunhapsach
                       where year(NgayNhap) = %s
                       group by month(NgayNhap)
                       order by Thang asc""" 
            cursor.execute(query, (year,))
            return cursor.fetchall()
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi xuất thống kê chi phí nhập theo tháng trong năm {year}: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_largest_import_invoice(self) -> Optional[PhieuNhapSach]:
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary=True)
            query = """
                SELECT pns.*, nv.HoTen as TenNhanVien, nns.TenCoSo as TenNguonNhap
                FROM phieunhapsach pns
                JOIN nhanvien nv ON pns.ID_NhanVien = nv.ID_NhanVien
                JOIN nguonnhapsach nns ON pns.ID_NguonNhap = nns.ID_NguonNhap
                ORDER BY pns.TongTien DESC LIMIT 1"""
            cursor.execute(query)
            row = cursor.fetchone()
            return PhieuNhapSach.from_dict(row) if row else None
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi lấy phiếu nhập có tổng tiền lớn nhất: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

    def get_by_sach(self, id_sach: str) -> List[PhieuNhapSach]:
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary=True)
            query = """SELECT DISTINCT pns.*, nv.HoTen as TenNhanVien, nns.TenCoSo as TenNguonNhap
                       FROM phieunhapsach pns
                       JOIN chitietphieunhap ctn ON pns.ID_PhieuNhap = ctn.ID_PhieuNhap
                       JOIN nhanvien nv ON pns.ID_NhanVien = nv.ID_NhanVien
                       JOIN nguonnhapsach nns ON pns.ID_NguonNhap = nns.ID_NguonNhap
                       where ctn.ID_Sach = %s"""
            cursor.execute(query, (id_sach,))
            rows = cursor.fetchall()
            return [PhieuNhapSach.from_dict(row) for row in rows]
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi lấy phiếu nhập qua mã sách {id_sach}: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_summary_by_date_range(self, start_date: date, end_date: date) -> tuple[int, Decimal]:
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary=True)
            query = """select sum(TongSoLuong), sum(TongTien)
                       from phieunhapsach
                       where NgayNhap between %s and %s"""
            cursor.execute(query, (start_date,end_date,))
            result = cursor.fetchone()
            return result if result else (0, 0.0)
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi lấy tổng số lượng và tổng tiền trong khoảng từ ngày {start_date} đến ngày {end_date}: {e}")
            return 0, 0.0
        finally:
            if cursor:
                cursor.close()

    def get_current_month(self) -> List[PhieuNhapSach]:
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary=True)
            query = """
                SELECT pns.*, nv.HoTen as TenNhanVien, nns.TenCoSo as TenNguonNhap
                FROM phieunhapsach pns
                JOIN nhanvien nv ON pns.ID_NhanVien = nv.ID_NhanVien
                JOIN nguonnhapsach nns ON pns.ID_NguonNhap = nns.ID_NguonNhap
                WHERE MONTH(pns.NgayNhap) = MONTH(CURRENT_DATE()) AND YEAR(pns.NgayNhap) = YEAR(CURRENT_DATE())"""
            cursor.execute(query)
            rows = cursor.fetchall()
            return [PhieuNhapSach.from_dict(row) for row in rows]
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi lấy các phiếu nhập trong tháng: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def count_current_month(self) -> int:
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = "SELECT COUNT(*) FROM phieunhapsach WHERE MONTH(NgayNhap) = MONTH(CURRENT_DATE()) AND YEAR(NgayNhap) = YEAR(CURRENT_DATE())"
            cursor.execute(query)
            result = cursor.fetchone()
            return result[0] if result else 0
        except Error as e:
            logging.error(f"Lỗi khi đếm phiếu nhập trong tháng: {e}")
            return 0
        finally:
            if cursor:
                cursor.close()

    def get_current_month_cost(self) -> Decimal:
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = "SELECT SUM(TongTien) FROM phieunhapsach WHERE MONTH(NgayNhap) = MONTH(CURRENT_DATE()) AND YEAR(NgayNhap) = YEAR(CURRENT_DATE())"
            cursor.execute(query)
            result = cursor.fetchone()
            return result[0] if result and result[0] else Decimal('0')
        except Error as e:
            logging.error(f"Lỗi khi tính chi phí nhập trong tháng: {e}")
            return Decimal('0')
        finally:
            if cursor:
                cursor.close()
    def get_top_supplier(self, limit: int = 5):
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary=True)
            query = """SELECT nns.TenCoSo, SUM(pns.TongTien) as TongTienNhap
                       FROM phieunhapsach pns
                       JOIN nguonnhapsach nns ON pns.ID_NguonNhap = nns.ID_NguonNhap
                       GROUP BY nns.TenCoSo
                       order by TongTienNhap desc
                       limit %s"""  
            cursor.execute(query, (limit,))
            return cursor.fetchall()
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi lấy các nhà cung cấp có tổng tiền cao nhất: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_monthly_statistics(self, year: int) -> List[tuple[int, int, Decimal]]:
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = """select month(NgayNhap) as Thang,
                              count(*) as TongSoPhieu,
                              sum(TongTien) as TongTien
                        from phieunhapsach
                        where year(NgayNhap) = %s
                        group by Thang
                        order by Thang"""
            cursor.execute(query, (year,))
            return cursor.fetchall()
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi thống kê số phiếu nhập theo năm {year}: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def search(self, keyword: str) -> List[PhieuNhapSach]:
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary=True)
            query = """
                SELECT pns.*, nv.HoTen as TenNhanVien, nns.TenCoSo as TenNguonNhap
                FROM phieunhapsach pns
                JOIN nhanvien nv ON pns.ID_NhanVien = nv.ID_NhanVien
                JOIN nguonnhapsach nns ON pns.ID_NguonNhap = nns.ID_NguonNhap
                WHERE pns.ID_PhieuNhap LIKE %s OR nv.HoTen LIKE %s OR nns.TenCoSo LIKE %s
                ORDER BY CAST(SUBSTRING(pns.ID_PhieuNhap, 3) AS UNSIGNED)
            """
            search_term = f"%{keyword}%"
            cursor.execute(query, (search_term, search_term, search_term))
            rows = cursor.fetchall()
            return [PhieuNhapSach.from_dict(row) for row in rows]
        except Error as e:
            logging.error(f"Lỗi khi tìm kiếm phiếu nhập: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

            

        
    


    
    
