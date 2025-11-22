from typing import List, Optional
import logging

from config.basedao import BaseDAO
from config.db_connection import DatabaseConnection

from source.models.NhaPhanPhoi import NhaPhanPhoi

from mysql.connector import Error

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class NhaPhanPhoiDAO(BaseDAO):
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self.conn = db.get_connection()

    def get_all(self) -> List[NhaPhanPhoi]:
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary= True)
            cursor.execute("select * from nhaphanphoi where TinhKhaDung = 'Khả dụng'")
            rows = cursor.fetchall()
            return [NhaPhanPhoi.from_dict(row) for row in rows]
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi lấy dữ liệu từ nhà phân phối khả dụng: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
        
    def get_all_unavailable(self) -> List[NhaPhanPhoi]:
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary= True)
            cursor.execute("select * from nhaphanphoi where TinhKhaDung = 'Không khả dụng'")
            rows = cursor.fetchall()
            return [NhaPhanPhoi.from_dict(row) for row in rows]
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi lấy dữ liệu từ nhà phân phối không còn khả dụng: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
        
    def insert(self, nhaphanphoi: NhaPhanPhoi) -> bool:
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = """insert into nhaphanphoi (ID_NguonXuat, TenCoSo, DiaChi, SoDienThoai, Email, TrangThaiNPP, TinhKhaDung, HinhAnh)
                       values (%s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (
                nhaphanphoi.ID_NguonXuat,
                nhaphanphoi.TenCoSo,
                nhaphanphoi.DiaChi,
                nhaphanphoi.SoDienThoai,
                nhaphanphoi.Email,
                nhaphanphoi.TrangThaiNPP,
                nhaphanphoi.TinhKhaDung,
                nhaphanphoi.HinhAnh,
            ))
            self.conn.commit()
            logging.info("Đã thêm thành công nhà phân phối!")
            return True
        except Error as e:
            self.conn.rollback()
            if "Duplicate entry" in str(e):
                logging.warning(f"Đã tồn tại mã nhà phân phối: {nhaphanphoi.ID_NguonXuat}")
                return False
            else:
                logging.error(f"Đã xảy ra lỗi khi thêm nhà phân phối: {e}")
                return False
        finally:
            if cursor:
                cursor.close()
    
    def update(self, nhaphanphoi: NhaPhanPhoi) -> bool:
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = """update nhaphanphoi
                       set TenCoSo = %s, DiaChi = %s, SoDienThoai = %s, Email = %s, TrangThaiNPP = %s, TinhKhaDung = %s, HinhAnh = %s
                       where ID_NguonXuat = %s"""
            cursor.execute(query, (
                nhaphanphoi.TenCoSo,
                nhaphanphoi.DiaChi,
                nhaphanphoi.SoDienThoai,
                nhaphanphoi.Email,
                nhaphanphoi.TrangThaiNPP,
                nhaphanphoi.TinhKhaDung,
                nhaphanphoi.HinhAnh,
                nhaphanphoi.ID_NguonXuat
            ))
            self.conn.commit()
            return cursor.rowcount > 0
        except Error as e:
            self.conn.rollback()
            logging.error(f"Đã xảy ra lỗi khi cập nhật thông tin cho nhà phân phối: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def find_by_key(self, ma_nhaphanphoi: str) -> Optional[NhaPhanPhoi]:
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary= True)
            cursor.execute("select * from nhaphanphoi where ID_NguonXuat = %s", (ma_nhaphanphoi,))
            row = cursor.fetchone()
            if not row:
                logging.error(f"Không tìm thấy nhà phân phối có mã {ma_nhaphanphoi}")
                return None
            return NhaPhanPhoi.from_dict(row)
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi tìm kiếm nhà phân phối theo mã: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
        
    def delete(self, ma_nhaphanphoi: str) -> bool:
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("update nhaphanphoi set TinhKhaDung = 'Không khả dụng' where ID_NguonXuat = %s", (ma_nhaphanphoi,))
            self.conn.commit()
            return cursor.rowcount > 0
        except Error as e:
            self.conn.rollback()
            logging.error(f"Đã xảy ra lỗi khi xóa mềm nhà phân phối: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def completely_delete(self, ma_nhaphanphoi: str) -> bool:
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("delete from nhaphanphoi where ID_NguonXuat = %s", (ma_nhaphanphoi,))
            self.conn.commit()
            return cursor.rowcount > 0
        except Error as e:
            self.conn.rollback()
            logging.error(f"Đã xảy ra lỗi khi xóa hoàn toàn nhà phân phối: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    #các hàm nâng cao

    def check_exists(self, id_nhaphanphoi: str) -> bool:
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("select 1 from nhaphanphoi where ID_NguonXuat = %s", (id_nhaphanphoi,))
            return cursor.fetchone() is not None
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi kiểm tra sự tồn tại nhà phân phối {id_nhaphanphoi}: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def restore(self, id_nhaphanphoi: str) -> bool:
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("update nhaphanphoi set TinhKhaDung = 'Khả dụng' where ID_NguonXuat = %s", (id_nhaphanphoi,))
            self.conn.commit()
            return cursor.rowcount > 0
        except Error as e:
            self.conn.rollback()
            logging.error(f"Đã xảy ra lỗi khi khôi phục lại nhà phân phối: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def get_top_distributors_by_orders(self, limit: int = 5) -> List[dict]:
        """Trả về top nhà phân phối có số phiếu nhập nhiều nhất.
           Kết quả gồm: ID_NguonXuat, TenCoSo, SoLanXuat."""
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = """SELECT npp.ID_NguonXuat, npp.TenCoSo, COUNT(px.ID_PhieuXuat) AS SoLanXuat
                       FROM nhaphanphoi npp
                       JOIN phieuxuatsach px ON npp.ID_NguonXuat = px.ID_NguonXuat
                       GROUP BY npp.ID_NguonXuat, npp.TenCoSo
                       ORDER BY SoLanXuat DESC
                       LIMIT %s"""
            cursor.execute(query, (limit,))
            rows = cursor.fetchall()
            return [] if not rows else rows
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi lấy về các nhà phân phối có nhiều phiếu xuất nhất: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_distributor_performance_summary(self) -> List[dict]:
        """Trả về danh sách thống kê hiệu suất của từng nhà phân phối:
            - Số phiếu xuất
            - Tổng số lượng
            - Tổng tiền"""
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = """SELECT npp.ID_NguonXuat, npp.TenCoSo,
                            COUNT(px.ID_PhieuXuat) AS SoPhieuXuat,
                            COALESCE(SUM(px.TongSoLuong), 0) AS TongSoLuong,
                            COALESCE(SUM(px.TongTien), 0) AS TongTien
                        FROM nhaphanphoi npp
                        LEFT JOIN phieuxuatsach px ON npp.ID_NguonXuat = px.ID_NguonXuat
                        GROUP BY npp.ID_NguonXuat, npp.TenCoSo
                        ORDER BY TongTien DESC"""
            cursor.execute(query)
            rows = cursor.fetchall()
            return [] if not rows else rows
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi thống kê hiệu suất của các nhà phân phối: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_total_distributor_by_status(self) -> dict:
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = """select TinhKhaDung, count(*) as SoLuong
                       from nhaphanphoi
                       group by TinhKhaDung"""
            cursor.execute(query)
            rows = cursor.fetchall()
            return {row["TinhKhaDung"]: row["SoLuong"] for row in rows}
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi xuất ra số lượng nhà phân phối theo tình trạng: {e}")
            return {}
        finally:
            if cursor:
                cursor.close()

    def get_statistics_by_status(self) -> List[dict]:
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = """select TrangThaiNPP, count(*) as SoLuong
                       from nhaphanphoi
                       group by TrangThaiNPP"""
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi đếm các nhà phân phối còn khả dụng và không khả dụng: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def count_all(self) -> int:
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM nhaphanphoi WHERE TinhKhaDung = 'Khả dụng'")
            result = cursor.fetchone()
            return result[0] if result else 0
        except Error as e:
            logging.error(f"Lỗi khi đếm nhà phân phối: {e}")
            return 0
        finally:
            if cursor:
                cursor.close()
        
        