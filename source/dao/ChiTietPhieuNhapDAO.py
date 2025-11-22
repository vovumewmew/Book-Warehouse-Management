from typing import List, Optional
import logging
from decimal import Decimal

from config.basedao import BaseDAO
from config.db_connection import DatabaseConnection

from source.models.ChiTietPhieuNhap import ChiTietPhieuNhap

from mysql.connector import Error

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class ChiTietPhieuNhapDAO(BaseDAO):
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self.conn = db.get_connection()

    def get_all_for_phieu(self, phieu_obj: 'PhieuNhapSach') -> List[ChiTietPhieuNhap]:
        """
        Lấy tất cả chi tiết của một đối tượng PhieuNhapSach đã có.
        Hàm này không gọi ngược lại PhieuNhapSachDAO, tránh đệ quy.
        """
        if not phieu_obj:
            return []
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary=True)
            # JOIN với bảng 'sach' để lấy thông tin sách
            query = """
                SELECT ctpn.SoLuong as SoLuongNhap, ctpn.DonGia, s.*
                FROM chitietphieunhap ctpn
                JOIN sach s ON ctpn.ID_Sach = s.ID_Sach
                WHERE ctpn.ID_PhieuNhap = %s
            """
            cursor.execute(query, (phieu_obj.ID_PhieuNhap,))
            rows = cursor.fetchall()
            return [ChiTietPhieuNhap.from_dict(row, phieu_nhap_obj=phieu_obj) for row in rows]
        except Error as e:
            logging.error(f"Gặp lỗi khi lấy các chi tiết phiếu nhập {phieu_obj.ID_PhieuNhap}: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_all(self, ma_phieunhap: str) -> List[ChiTietPhieuNhap]:
        "hàm này là lấy ra tất cả chi tiết phiếu nhập của 1 phiếu nhập"
        from source.dao.PhieuNhapSachDAO import PhieuNhapSachDAO
        phieu_nhap_dao = PhieuNhapSachDAO(self.db)
        phieu_obj = phieu_nhap_dao.find_by_key(ma_phieunhap)
        return self.get_all_for_phieu(phieu_obj)
    
    def insert(self, chitietphieunhap: ChiTietPhieuNhap) -> bool:
        cursor = None
        try:
            from source.dao.PhieuNhapSachDAO import PhieuNhapSachDAO
            phieu_nhap_dao = PhieuNhapSachDAO(self.db)
            cursor = self.conn.cursor()
            query = """insert into chitietphieunhap (ID_PhieuNhap, ID_Sach, SoLuong, DonGia)
                       values(%s, %s, %s, %s)"""
            cursor.execute(query, (
                chitietphieunhap.phieu_nhap.ID_PhieuNhap,
                chitietphieunhap.sach.ID_Sach,
                chitietphieunhap.SoLuong,
                chitietphieunhap.DonGia
            ))
            self.conn.commit()
            phieu_nhap_dao.auto_update_total(chitietphieunhap.phieu_nhap.ID_PhieuNhap)
            return True
        except Error as e:
            self.conn.rollback()
            logging.error(f"Đã xảy ra lỗi khi thêm 1 chi tiết cho phiếu nhập {chitietphieunhap.phieu_nhap.ID_PhieuNhap}: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def update(self, chitietphieunhap: ChiTietPhieuNhap, ma_sach: str) -> bool:
        "Hàm này là sửa trực tiếp chi tiết phiếu nhập với 1 mã sách cố định được thêm vào từ người dùng"
        cursor = None
        try:
            from source.dao.PhieuNhapSachDAO import PhieuNhapSachDAO
            phieu_nhap_dao = PhieuNhapSachDAO(self.db)
            cursor = self.conn.cursor()
            query = """update chitietphieunhap
                       set SoLuong = %s, DonGia = %s
                       where ID_PhieuNhap = %s and ID_Sach = %s"""
            cursor.execute(query, (
                chitietphieunhap.SoLuong,
                chitietphieunhap.DonGia,
                chitietphieunhap.phieu_nhap.ID_PhieuNhap,
                ma_sach
            ))
            self.conn.commit()
            phieu_nhap_dao.auto_update_total(chitietphieunhap.phieu_nhap.ID_PhieuNhap)
            return cursor.rowcount > 0
        except Error as e:
            self.conn.rollback()
            logging.error(f"Đã xảy ra lỗi khi cập nhật thông tin chi tiết phiếu nhập có mã:{chitietphieunhap.phieu_nhap.ID_PhieuNhap} và về sách: {ma_sach}, có lỗi là: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def find_by_key(self, id_phieunhap: str, id_sach: str) -> Optional[ChiTietPhieuNhap]:
        "Hàm này là tìm 1 chi tiết phiếu nhập của phiếu nhập đối với 1 mã sách cố định (vì mỗi mã sách chỉ xuất hiện cố định 1 lần trong 1 phiếu nhập)"
        cursor = None
        from source.dao.PhieuNhapSachDAO import PhieuNhapSachDAO
        phieu_nhap_dao = PhieuNhapSachDAO(self.db)
        phieu_obj = phieu_nhap_dao.find_by_key(id_phieunhap)
        try:
            cursor = self.conn.cursor(dictionary= True)
            query = """
                SELECT ctpn.SoLuong as SoLuongNhap, ctpn.DonGia, s.*
                FROM chitietphieunhap ctpn
                JOIN sach s ON ctpn.ID_Sach = s.ID_Sach
                WHERE ctpn.ID_PhieuNhap = %s AND ctpn.ID_Sach = %s
            """
            cursor.execute(query, (id_phieunhap, id_sach,))
            row = cursor.fetchone()
            if not row:
                logging.warning(f"Không thể tìm thấy sách có mã: {id_sach} từ chi tiết phiếu nhập có mã: {id_phieunhap}")
                return None
            return ChiTietPhieuNhap.from_dict(row, phieu_nhap_obj= phieu_obj)
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi tìm kiếm với chi tiết phiếu nhập: {id_phieunhap} đối với sách: {id_sach} với lỗi: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
        
    def delete(self, id_phieunhap: str, id_sach: str) -> bool:
        cursor = None
        try:
            from source.dao.PhieuNhapSachDAO import PhieuNhapSachDAO
            phieu_nhap_dao = PhieuNhapSachDAO(self.db)
            cursor = self.conn.cursor()
            cursor.execute("delete from chitietphieunhap where ID_PhieuNhap = %s and ID_Sach = %s", (id_phieunhap, id_sach,))
            self.conn.commit()
            phieu_nhap_dao.auto_update_total(id_phieunhap)
            return cursor.rowcount > 0
        except Error as e:
            self.conn.rollback()
            logging.error(f"Đã xảy ra lỗi khi xóa chi tiết phiếu nhập: {id_phieunhap} đối với sách: {id_sach}, với lỗi: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def exist(self, id_phieunhap: str, id_sach: str) -> bool:
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = "select 1 from chitietphieunhap where ID_PhieuNhap = %s and ID_Sach = %s"
            cursor.execute(query, (id_phieunhap, id_sach,))
            return cursor.fetchone() is not None
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi kiểm tra chi tiết phiếu nhập rỗng {id_phieunhap} - sách {id_sach}: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
    
    def bulk_insert(self, list_chitiet: List[ChiTietPhieuNhap]) -> bool:
        cursor = None
        if not list_chitiet:
            return False
        try:
            from source.dao.PhieuNhapSachDAO import PhieuNhapSachDAO
            cursor = self.conn.cursor()
            query = """insert into chitietphieunhap (ID_PhieuNhap, ID_Sach, SoLuong, DonGia)
                       values(%s, %s, %s, %s)"""
            data = [
                (ct.phieu_nhap.ID_PhieuNhap, ct.sach.ID_Sach, ct.SoLuong, ct.DonGia)
                for ct in list_chitiet
            ]
            cursor.executemany(query, data)
            self.conn.commit()
            phieu_nhap_dao = PhieuNhapSachDAO(self.db)
            phieu_nhap_dao.auto_update_total(list_chitiet[0].phieu_nhap.ID_PhieuNhap)
            return cursor.rowcount == len(list_chitiet)
        except Error as e:
            self.conn.rollback()
            logging.error(f"Đã xảy ra lỗi khi bulk_insert chi tiết phiếu nhập: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    #các hàm nâng cao#

    def get_by_phieu(self, id_phieunhap: str) -> List[ChiTietPhieuNhap]:
        cursor = None
        try:
            from source.dao.PhieuNhapSachDAO import PhieuNhapSachDAO
            phieu_nhap_dao = PhieuNhapSachDAO(self.db)
            phieu_obj = phieu_nhap_dao.find_by_key(id_phieunhap)
            if not phieu_obj:
                logging.warning(f"Không tìm thấy phiếu nhập có mã {id_phieunhap}")
                return []
            cursor = self.conn.cursor(dictionary=True)
            query = """
                SELECT ctpn.SoLuong as SoLuongNhap, ctpn.DonGia, s.*
                FROM chitietphieunhap ctpn
                JOIN sach s ON ctpn.ID_Sach = s.ID_Sach
                WHERE ctpn.ID_PhieuNhap = %s
            """
            cursor.execute(query, (id_phieunhap,))
            rows = cursor.fetchall()
            result = [ChiTietPhieuNhap.from_dict(row, phieu_nhap_obj=phieu_obj) for row in rows]
            return result
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi tìm chi tiết phiếu nhập bằng mã phiếu {id_phieunhap}: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_by_sach(self, id_sach: str) -> List[ChiTietPhieuNhap]:
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary= True)
            query = """
                SELECT ctpn.ID_PhieuNhap, ctpn.SoLuong as SoLuongNhap, ctpn.DonGia, s.*
                FROM chitietphieunhap ctpn
                JOIN sach s ON ctpn.ID_Sach = s.ID_Sach
                WHERE ctpn.ID_Sach = %s
            """
            cursor.execute(query, (id_sach,))
            rows = cursor.fetchall()
            result = []
            from source.dao.PhieuNhapSachDAO import PhieuNhapSachDAO
            for row in rows:
                phieu_obj = PhieuNhapSachDAO(self.db).find_by_key(row["ID_PhieuNhap"])
                result.append(ChiTietPhieuNhap.from_dict(row, phieu_nhap_obj=phieu_obj))
            return result
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi tìm chi tiết phiếu nhập bằng mã sách: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
        
    def delete_all_by_phieu(self, id_phieunhap: str) -> bool:
        cursor = None
        try:
            from source.dao.PhieuNhapSachDAO import PhieuNhapSachDAO
            phieu_nhap_dao = PhieuNhapSachDAO(self.db)
            cursor = self.conn.cursor()
            cursor.execute("delete from chitietphieunhap where ID_PhieuNhap = %s", (id_phieunhap,))
            self.conn.commit()
            phieu_nhap_dao.auto_update_total(id_phieunhap)
            return cursor.rowcount > 0
        except Error as e:
            self.conn.rollback()
            logging.error(f"Đã xảy ra lỗi khi xóa toàn bộ chi tiết của phiếu nhập: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def get_total_by_sach(self, id_sach: str) -> int:
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("select sum(SoLuong) from chitietphieunhap where ID_Sach = %s", (id_sach,))
            result = cursor.fetchone()
            return result[0] if result and result[0] else 0
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi tính tổng số lượng các sách nhập: {e}")
            return 0
        finally:
            if cursor:
                cursor.close()

    def get_total_value_by_sach(self, id_sach: str) -> Decimal:
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = """select sum(SoLuong * DonGia) as TongTien
                       from chitietphieunhap
                       where ID_Sach = %s"""
            cursor.execute(query, (id_sach,))
            result = cursor.fetchone()
            return float(result[0]) if result and result[0] else 0.0
        except Error as e:
            logging.error(f"Lỗi khi tính tổng số tiền nhập của sách {id_sach}: {e}")
            return 0.0
        finally:
            if cursor:
                cursor.close()

    def get_import_stats_by_month(self, year: int):
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = """select
                            month(pn.NgayNhap) as Thang,
                            sum(ct.SoLuong * ct.DonGia) as TongTienNhap
                        from chitietphieunhap ct
                        join phieunhapsach pn on ct.ID_PhieuNhap = pn.ID_PhieuNhap
                        where year(pn.NgayNhap) = %s
                        group by month(pn.NgayNhap)
                        order by Thang"""
            cursor.execute(query, (year,))
            return cursor.fetchall()
        except Error as e:
            logging.error(f"Lỗi khi nhập thống kê nhập năm {year} theo tháng: {e}")
            return[]
        finally:
            if cursor:
                cursor.close()

    def get_avg_import_price_by_sach(self, id_sach: str) -> Decimal:
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = """select avg(DonGia) as GiaTrungBinh
                       from chitietphieunhap
                       where ID_Sach = %s"""
            cursor.execute(query, (id_sach,))
            result = cursor.fetchone()
            return float(result[0]) if result and result[0] else 0.0
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi lấy giá nhập trung bình với sách {id_sach}: {e}")
            return 0.0
        finally:
            if cursor:
                cursor.close()
        
        
        
        
        