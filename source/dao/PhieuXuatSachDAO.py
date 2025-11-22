from typing import List, Optional
from datetime import date
from decimal import Decimal
import logging

from config.db_connection import DatabaseConnection
from config.basedao import BaseDAO

from source.models.PhieuXuatSach import PhieuXuatSach

from mysql.connector import Error

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class PhieuXuatSachDAO(BaseDAO):
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self.conn = db.get_connection()

    def get_all(self) -> List[PhieuXuatSach]:
        cursor = None
        try: 
            cursor = self.conn.cursor(dictionary=True)
            query = """
                SELECT pxs.*, nv.HoTen as TenNhanVien, npp.TenCoSo as TenNhaPhanPhoi
                FROM phieuxuatsach pxs
                JOIN nhanvien nv ON pxs.ID_NhanVien = nv.ID_NhanVien
                JOIN nhaphanphoi npp ON pxs.ID_NguonXuat = npp.ID_NguonXuat
                ORDER BY CAST(SUBSTRING(pxs.ID_PhieuXuat, 3) AS UNSIGNED)
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            return [PhieuXuatSach.from_dict(row) for row in rows]
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi lấy dữ liệu phiếu xuất sách: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
    
    def insert(self, phieuxuatsach: PhieuXuatSach) -> bool:
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = """insert into phieuxuatsach (ID_PhieuXuat, NgayXuat, TongSoLuong, TongTien, ID_NhanVien, ID_NguonXuat)
                       values (%s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (
                phieuxuatsach.ID_PhieuXuat,
                phieuxuatsach.NgayXuat,
                phieuxuatsach.TongSoLuong,
                phieuxuatsach.TongTien,
                phieuxuatsach.nhan_vien_xuat.ID_NhanVien,
                phieuxuatsach.nha_phan_phoi.ID_NguonXuat
            ))
            self.conn.commit()
            return True
        except Error as e:
            self.conn.rollback()
            logging.error(f"Đã xảy ra lỗi khi thêm 1 phiếu xuất sách: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def update(self, phieuxuatsach: PhieuXuatSach) -> bool:
        cursor = None
        try:
            print(f"--- DEBUG (DAO): PhieuXuatSachDAO.update được gọi cho ID: {phieuxuatsach.ID_PhieuXuat}")
            cursor = self.conn.cursor()
            query = """update phieuxuatsach
                       set NgayXuat = %s, ID_NhanVien = %s, ID_NguonXuat = %s
                       where ID_PhieuXuat = %s"""
            cursor.execute(query, (
                phieuxuatsach.NgayXuat,
                phieuxuatsach.nhan_vien_xuat.ID_NhanVien,
                phieuxuatsach.nha_phan_phoi.ID_NguonXuat,
                phieuxuatsach.ID_PhieuXuat
            ))
            print(f"--- DEBUG (DAO): cursor.rowcount = {cursor.rowcount}")
            return cursor.rowcount > 0
        except Error as e:
            print(f"--- DEBUG (DAO): Lỗi SQL khi cập nhật: {e}")
            logging.error(f"Đã xảy ra lỗi khi cập nhật thông tin phiếu xuất: {e}")
            raise e # Ném lỗi ra để Service bắt và rollback
        finally:
            if cursor:
                cursor.close()

    def find_by_key(self, id_phieuxuat) -> Optional[PhieuXuatSach]:
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary=True)
            query = """
                SELECT pxs.*, nv.HoTen as TenNhanVien, npp.TenCoSo as TenNhaPhanPhoi
                FROM phieuxuatsach pxs
                JOIN nhanvien nv ON pxs.ID_NhanVien = nv.ID_NhanVien
                JOIN nhaphanphoi npp ON pxs.ID_NguonXuat = npp.ID_NguonXuat
                WHERE pxs.ID_PhieuXuat = %s
            """
            cursor.execute(query, (id_phieuxuat,))
            row = cursor.fetchone()
            if not row:
                logging.error(f"Không thể tìm thấy phiếu xuất có mã: {id_phieuxuat}")
                return None
            phieu = PhieuXuatSach.from_dict(row)
            # Tạm thời không load chi tiết để tránh lỗi đệ quy, Service sẽ xử lý việc này
            phieu.Danhsachchitietxuat = []
            return phieu
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi tìm kiếm phiếu xuất: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

    def delete(self, id_phieuxuat) -> bool:
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("delete from phieuxuatsach where ID_PhieuXuat = %s", (id_phieuxuat,))
            self.conn.commit()
            return cursor.rowcount > 0
        except Error as e:
            self.conn.rollback()
            logging.error(f"Đã xảy ra lỗi khi xóa phiếu xuất: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def get_total(self, id_phieuxuat: str) -> tuple[int, Decimal]:
        try:
            from source.dao.ChiTietPhieuXuatDAO import ChiTietPhieuXuatDAO
            chitiet_dao = ChiTietPhieuXuatDAO(self.db)
            list_ct = chitiet_dao.get_all(id_phieuxuat)
            if not list_ct:
                return 0, 0.0
            tong_sl = sum(ct.SoLuong for ct in list_ct)
            tong_tien = sum(ct.ThanhTien for ct in list_ct)
            return tong_sl, tong_tien
        except Error as e:
            logging.error(f"Lỗi khi tính tổng SL và tổng tiền: {e}")
            return 0, 0.0
        
    def auto_update_total(self, id_phieuxuat: str) -> bool:
        cursor = None
        try:
            tong_sl, tong_tien = self.get_total(id_phieuxuat)
            cursor = self.conn.cursor()
            query = """update phieuxuatsach
                       set TongSoLuong = %s, TongTien = %s
                       where ID_PhieuXuat = %s"""
            cursor.execute(query, (tong_sl, tong_tien, id_phieuxuat))
            self.conn.commit()
            return True
        except Error as e:
            self.conn.rollback()
            logging.error(f"Lỗi khi cập nhật tổng của phiếu xuất {id_phieuxuat}: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    #các hàm nâng cao

    def get_recent(self, limit: int = 10) -> List[PhieuXuatSach]:
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("select * from phieuxuatsach order by NgayXuat desc limit %s", (limit,))
            rows = cursor.fetchall()
            return [PhieuXuatSach.from_dict(row) for row in rows]
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi lấy {limit} phiếu xuất gần nhất: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
    
    def search_by_date_range(self, start_date: date, end_date: date) -> List[PhieuXuatSach]:
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary=True)
            query = """select * from phieuxuatsach
                       where NgayXuat between %s and %s
                       order by NgayXuat asc"""
            cursor.execute(query, (start_date, end_date, ))
            rows = cursor.fetchall()
            return [PhieuXuatSach.from_dict(row) for row in rows]
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi tìm các phiếu xuất từ ngày {start_date} đến ngày {end_date}: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_by_id_nhanvien(self, id_nhanvien: str) -> List[PhieuXuatSach]:
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute("select * from phieuxuatsach where ID_NhanVien = %s", (id_nhanvien,))
            rows = cursor.fetchall()
            return [PhieuXuatSach.from_dict(row) for row in rows]
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi tìm phiếu xuất bằng mã nhân viên {id_nhanvien}: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_total_revenue(self, start_date: date, end_date: date) -> Decimal:
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = """select sum(TongTien) as TongDoanhThu
                       from phieuxuatsach
                       where NgayXuat between %s and %s"""
            cursor.execute(query, (start_date, end_date,))
            row = cursor.fetchone()
            return row[0] if row and row[0] else 0.0
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi tính tổng doanh thu trong khoảng {start_date} tới {end_date}: {e}")
            return 0.0
        finally:
            if cursor:
                cursor.close()
    
    def count_by_employee(self) -> List[tuple[str, int]]:
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = """select ID_NhanVien, count(*) as TongSoPhieu
                       from phieuxuatsach
                       group by ID_NhanVien"""
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi thống kê số phiếu xuất theo nhân viên: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_monthly_revenue(self, year: int) -> List[tuple[int, Decimal]]:
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = """select month(NgayXuat) as Thang, sum(TongTien) as TongDoanhThu
                       from phieuxuatsach
                       where year(NgayXuat) = %s
                       group by month(NgayXuat)
                       order by Thang asc""" 
            cursor.execute(query, (year,))
            return cursor.fetchall()
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi xuất thống kê doanh thu theo tháng trong năm {year}: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_highest_value_invoice(self) -> Optional[PhieuXuatSach]:
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary=True)
            query = """select * from phieuxuatsach
                       order by TongTien desc
                       limit 1"""
            cursor.execute(query)
            row = cursor.fetchone()
            return PhieuXuatSach.from_dict(row) if row else None
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi lấy phiếu xuất có tổng tiền lớn nhất: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

    def get_by_sach(self, id_sach: str) -> List[PhieuXuatSach]:
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary=True)
            query = """select distinct px.*
                       from phieuxuatsach px
                       join chitietphieuxuat ctx on px.ID_PhieuXuat = ctx.ID_PhieuXuat
                       where ctx.ID_Sach = %s"""
            cursor.execute(query, (id_sach,))
            rows = cursor.fetchall()
            return [PhieuXuatSach.from_dict(row) for row in rows]
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi lấy phiếu xuất qua mã sách {id_sach}: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_summary_by_date_range(self, start_date: date, end_date: date) -> tuple[int, Decimal]:
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary=True)
            query = """select sum(TongSoLuong), sum(TongTien)
                       from phieuxuatsach
                       where NgayXuat between %s and %s"""
            cursor.execute(query, (start_date,end_date,))
            result = cursor.fetchone()
            return result if result else (0, 0.0)
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi lấy tổng số lượng và tổng tiền trong khoảng từ ngày {start_date} đến ngày {end_date}: {e}")
            return 0, 0.0
        finally:
            if cursor:
                cursor.close()

    def get_current_month(self) -> List[PhieuXuatSach]:
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary=True)
            query = """select * from phieuxuatsach
                       where month(NgayXuat) = month(current_date())
                       and year(NgayXuat) = year(current_date())"""
            cursor.execute(query)
            rows = cursor.fetchall()
            return [PhieuXuatSach.from_dict(row) for row in rows]
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi lấy các phiếu xuất trong tháng: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def count_current_month(self) -> int:
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = "SELECT COUNT(*) FROM phieuxuatsach WHERE MONTH(NgayXuat) = MONTH(CURRENT_DATE()) AND YEAR(NgayXuat) = YEAR(CURRENT_DATE())"
            cursor.execute(query)
            result = cursor.fetchone()
            return result[0] if result else 0
        except Error as e:
            logging.error(f"Lỗi khi đếm phiếu xuất trong tháng: {e}")
            return 0
        finally:
            if cursor:
                cursor.close()

    def get_current_month_revenue(self) -> Decimal:
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = "SELECT SUM(TongTien) FROM phieuxuatsach WHERE MONTH(NgayXuat) = MONTH(CURRENT_DATE()) AND YEAR(NgayXuat) = YEAR(CURRENT_DATE())"
            cursor.execute(query)
            result = cursor.fetchone()
            return result[0] if result and result[0] else Decimal('0')
        except Error as e:
            logging.error(f"Lỗi khi tính doanh thu xuất trong tháng: {e}")
            return Decimal('0')
        finally:
            if cursor:
                cursor.close()


    def get_monthly_statistics(self, year: int) -> List[tuple[int, int, Decimal]]:
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = """select month(NgayXuat) as Thang,
                              count(*) as TongSoPhieu,
                              sum(TongTien) as TongTien
                        from phieuxuatsach
                        where year(NgayXuat) = %s
                        group by Thang
                        order by Thang"""
            cursor.execute(query, (year,))
            return cursor.fetchall()
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi thống kê số phiếu xuất theo năm {year}: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def search(self, keyword: str) -> List[PhieuXuatSach]:
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary=True)
            query = """
                SELECT pxs.*, nv.HoTen as TenNhanVien, npp.TenCoSo as TenNhaPhanPhoi
                FROM phieuxuatsach pxs
                JOIN nhanvien nv ON pxs.ID_NhanVien = nv.ID_NhanVien
                JOIN nhaphanphoi npp ON pxs.ID_NguonXuat = npp.ID_NguonXuat
                WHERE pxs.ID_PhieuXuat LIKE %s OR nv.HoTen LIKE %s OR npp.TenCoSo LIKE %s
                ORDER BY CAST(SUBSTRING(pxs.ID_PhieuXuat, 3) AS UNSIGNED)
            """
            search_term = f"%{keyword}%"
            cursor.execute(query, (search_term, search_term, search_term))
            rows = cursor.fetchall()
            return [PhieuXuatSach.from_dict(row) for row in rows]
        except Error as e:
            logging.error(f"Lỗi khi tìm kiếm phiếu xuất: {e}")
            return []
        finally:
            if cursor:
                cursor.close()



    
    
