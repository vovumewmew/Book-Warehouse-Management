from typing import List, Optional
import logging
from decimal import Decimal

from config.basedao import BaseDAO
from config.db_connection import DatabaseConnection

from source.models.ChiTietPhieuXuat import ChiTietPhieuXuat

from mysql.connector import Error

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class ChiTietPhieuXuatDAO(BaseDAO):
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self.conn = db.get_connection()


    def get_all(self, ma_phieuxuat: str) -> List[ChiTietPhieuXuat]:
        "hàm này là lấy ra tất cả chi tiết phiếu xuất của 1 phiếu xuất"
        from source.dao.PhieuXuatSachDAO import PhieuXuatSachDAO
        phieu_obj = PhieuXuatSachDAO(self.db).find_by_key(ma_phieuxuat)
        cursor = None
        try: 
            cursor = self.conn.cursor(dictionary=True)
            query = """
                SELECT ctpx.SoLuong as SoLuongXuat, ctpx.DonGia, s.* 
                FROM chitietphieuxuat ctpx
                JOIN sach s ON ctpx.ID_Sach = s.ID_Sach
                WHERE ctpx.ID_PhieuXuat = %s
            """
            cursor.execute(query, (ma_phieuxuat,))
            rows = cursor.fetchall()
            return [ChiTietPhieuXuat.from_dict(row, phieu_xuat_obj= phieu_obj) for row in rows]
        except Error as e:
            logging.error(f"Gặp lỗi khi lấy các chi tiết phiếu xuất {ma_phieuxuat}: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
    
    def insert(self, chitietphieuxuat: ChiTietPhieuXuat) -> bool:
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = """insert into chitietphieuxuat (ID_PhieuXuat, ID_Sach, SoLuong, DonGia)
                       values(%s, %s, %s, %s)"""
            cursor.execute(query, (
                chitietphieuxuat.phieu_xuat.ID_PhieuXuat,
                chitietphieuxuat.sach.ID_Sach,
                chitietphieuxuat.SoLuong,
                chitietphieuxuat.DonGia
            ))
            self.conn.commit()
            from source.dao.PhieuXuatSachDAO import PhieuXuatSachDAO
            PhieuXuatSachDAO(self.db).auto_update_total(chitietphieuxuat.phieu_xuat.ID_PhieuXuat)
            return True
        except Error as e:
            self.conn.rollback()
            logging.error(f"Đã xảy ra lỗi khi thêm 1 chi tiết cho phiếu xuất {chitietphieuxuat.phieu_xuat.ID_PhieuXuat}: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def update(self, chitietphieuxuat: ChiTietPhieuXuat, ma_sach: str) -> bool:
        "Hàm này là sửa trực tiếp chi tiết phiếu xuất với 1 mã sách cố định được thêm vào từ người dùng"
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = """update chitietphieuxuat
                       set SoLuong = %s, DonGia = %s
                       where ID_PhieuXuat = %s and ID_Sach = %s"""
            cursor.execute(query, (
                chitietphieuxuat.SoLuong,
                chitietphieuxuat.DonGia,
                chitietphieuxuat.phieu_xuat.ID_PhieuXuat,
                ma_sach
            ))
            self.conn.commit()
            from source.dao.PhieuXuatSachDAO import PhieuXuatSachDAO
            PhieuXuatSachDAO(self.db).auto_update_total(chitietphieuxuat.phieu_xuat.ID_PhieuXuat)
            return cursor.rowcount > 0
        except Error as e:
            self.conn.rollback()
            logging.error(f"Đã xảy ra lỗi khi cập nhật thông tin chi tiết phiếu xuất có mã:{chitietphieuxuat.phieu_xuat.ID_PhieuXuat} và về sách: {ma_sach}, có lỗi là: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def find_by_key(self, id_phieuxuat: str, id_sach: str) -> Optional[ChiTietPhieuXuat]:
        "Hàm này là tìm 1 chi tiết phiếu nhập của phiếu xuất đối với 1 mã sách cố định (vì mỗi mã sách chỉ xuất hiện cố định 1 lần trong 1 phiếu xuất)"
        cursor = None

        from source.dao.PhieuXuatSachDAO import PhieuXuatSachDAO
        phieu_obj = PhieuXuatSachDAO(self.db).find_by_key(id_phieuxuat)
        try:
            cursor = self.conn.cursor(dictionary= True)
            query = """
                SELECT ctpx.SoLuong as SoLuongXuat, ctpx.DonGia, s.*
                FROM chitietphieuxuat ctpx
                JOIN sach s ON ctpx.ID_Sach = s.ID_Sach
                WHERE ctpx.ID_PhieuXuat = %s AND ctpx.ID_Sach = %s
            """
            cursor.execute(query, (id_phieuxuat, id_sach,))
            row = cursor.fetchone()
            if not row:
                logging.warning(f"Không thể tìm thấy sách có mã: {id_sach} từ chi tiết phiếu xuất có mã: {id_phieuxuat}")
                return None
            return ChiTietPhieuXuat.from_dict(row, phieu_xuat_obj= phieu_obj)
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi tìm kiếm với chi tiết phiếu xuất: {id_phieuxuat} đối với sách: {id_sach} với lỗi: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
        
    def delete(self, id_phieuxuat: str, id_sach: str) -> bool:
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("delete from chitietphieuxuat where ID_PhieuXuat = %s and ID_Sach = %s", (id_phieuxuat, id_sach,))
            self.conn.commit()
            from source.dao.PhieuXuatSachDAO import PhieuXuatSachDAO
            PhieuXuatSachDAO(self.db).auto_update_total(id_phieuxuat)
            return cursor.rowcount > 0
        except Error as e:
            self.conn.rollback()
            logging.error(f"Đã xảy ra lỗi khi xóa chi tiết phiếu xuất: {id_phieuxuat} đối với sách: {id_sach}, với lỗi: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def exist(self, id_phieuxuat: str, id_sach: str) -> bool:
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = "select 1 from chitietphieuxuat where ID_PhieuXuat = %s and ID_Sach = %s"
            cursor.execute(query, (id_phieuxuat, id_sach,))
            return cursor.fetchone() is not None
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi kiểm tra chi tiết phiếu xuất rỗng {id_phieuxuat} - sách {id_sach}: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
    
    def bulk_insert(self, list_chitiet: List[ChiTietPhieuXuat]) -> bool:
        cursor = None
        if not list_chitiet:
            return False
        try:
            cursor = self.conn.cursor()
            query = """insert into chitietphieuxuat (ID_PhieuXuat, ID_Sach, SoLuong, DonGia)
                       values(%s, %s, %s, %s)"""
            data = [
                (ct.phieu_xuat.ID_PhieuXuat, ct.sach.ID_Sach, ct.SoLuong, ct.DonGia)
                for ct in list_chitiet
            ]
            cursor.executemany(query, data)
            self.conn.commit()
            return cursor.rowcount == len(list_chitiet)
        except Error as e:
            self.conn.rollback()
            logging.error(f"Đã xảy ra lỗi khi bulk_insert chi tiết phiếu xuất: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    #các hàm nâng cao#

    def get_by_sach(self, id_sach: str) -> List[ChiTietPhieuXuat]:
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary=True)
            query = """
                SELECT ctpx.ID_PhieuXuat, ctpx.SoLuong as SoLuongXuat, ctpx.DonGia, s.*
                FROM chitietphieuxuat ctpx
                JOIN sach s ON ctpx.ID_Sach = s.ID_Sach
                WHERE ctpx.ID_Sach = %s
            """
            cursor.execute(query, (id_sach,))
            rows = cursor.fetchall()    
            result = []
            for row in rows:
                phieu_obj = PhieuXuatSachDAO(self.db).find_by_key(row["ID_PhieuXuat"])
                result.append(ChiTietPhieuXuat.from_dict(row, phieu_xuat_obj=phieu_obj))
            return result
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi tìm chi tiết phiếu xuất bằng mã sách: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_by_phieu(self, id_phieuxuat: str) -> List[ChiTietPhieuXuat]:
        cursor = None
        try:
            from source.dao.PhieuXuatSachDAO import PhieuXuatSachDAO
            phieu_obj = PhieuXuatSachDAO(self.db).find_by_key(id_phieuxuat)
            if not phieu_obj:
                logging.warning(f"Không tìm thấy phiếu xuất có mã {id_phieuxuat}")
                return []
            cursor = self.conn.cursor(dictionary=True)
            query = """
                SELECT ctpx.SoLuong as SoLuongXuat, ctpx.DonGia, s.*
                FROM chitietphieuxuat ctpx
                JOIN sach s ON ctpx.ID_Sach = s.ID_Sach
                WHERE ctpx.ID_PhieuXuat = %s
            """
            cursor.execute(query, (id_phieuxuat,))
            rows = cursor.fetchall()
            result = []
            for row in rows:
                chitiet = ChiTietPhieuXuat.from_dict(row, phieu_xuat_obj=phieu_obj)
                result.append(chitiet)
            return result
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi tìm chi tiết phiếu xuất bằng mã phiếu {id_phieuxuat}: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

        
    def delete_all_by_phieu(self, id_phieuxuat: str) -> bool:
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("delete from chitietphieuxuat where ID_PhieuXuat = %s", (id_phieuxuat,))
            self.conn.commit()
            from source.dao.PhieuXuatSachDAO import PhieuXuatSachDAO
            PhieuXuatSachDAO(self.db).auto_update_total(id_phieuxuat)
            return cursor.rowcount > 0
        except Error as e:
            self.conn.rollback()
            logging.error(f"Đã xảy ra lỗi khi xóa toàn bộ chi tiết của phiếu xuất: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def get_total_by_sach(self, id_sach: str) -> int:
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("select sum(SoLuong) from chitietphieuxuat where ID_Sach = %s", (id_sach,))
            result = cursor.fetchone()
            return result[0] if result and result[0] else 0
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi tính tổng số lượng các sách xuất: {e}")
            return 0
        finally:
            if cursor:
                cursor.close()

    def get_total_value_by_sach(self, id_sach: str) -> Decimal:
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = """select sum(SoLuong * DonGia) as TongTien
                       from chitietphieuxuat
                       where ID_Sach = %s"""
            cursor.execute(query, (id_sach,))
            result = cursor.fetchone()
            return float(result[0]) if result and result[0] else 0.0
        except Error as e:
            logging.error(f"Lỗi khi tính tổng số tiền xuất của sách {id_sach}: {e}")
            return 0.0
        finally:
            if cursor:
                cursor.close()

    def get_export_stats_by_month(self, year: int):
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = """select
                            month(px.NgayXuat) as Thang,
                            sum(ct.SoLuong * ct.DonGia) as TongTienXuat
                       from chitietphieuxuat ct
                       join phieuxuatsach px on ct.ID_PhieuXuat = px.ID_PhieuXuat
                       where year(px.NgayXuat) = %s
                       group by month(px.NgayXuat)
                       order by Thang"""
            cursor.execute(query, (year,))
            return cursor.fetchall()
        except Error as e:
            logging.error(f"Lỗi khi nhập thống kê xuất năm {year} theo tháng: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_avg_export_price_by_sach(self, id_sach: str) -> Decimal:
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = """select avg(DonGia) as GiaTrungBinh
                       from chitietphieuxuat
                       where ID_Sach = %s"""
            cursor.execute(query, (id_sach,))
            result = cursor.fetchone()
            return float(result[0]) if result and result[0] else 0.0
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi lấy giá xuất trung bình với sách {id_sach}: {e}")
            return 0.0
        finally:
            if cursor:
                cursor.close()
        
        
        
        
            

        
        
        
        
        
