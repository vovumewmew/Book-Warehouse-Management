from typing import List, Optional
import logging

from config.basedao import BaseDAO
from config.db_connection import DatabaseConnection

from source.models.NhanVien import NhanVien

from mysql.connector import Error

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class NhanVienDAO(BaseDAO):
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self.conn = db.get_connection()

    def get_all(self) -> List[NhanVien]:
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary= True)
            cursor.execute("select * from nhanvien where TrangThaiNhanVien = 'Đang làm việc'")
            rows = cursor.fetchall()
            print(f"✅ Số nhân viên còn làm việc lấy được từ DB: {len(rows)}")
            return [NhanVien.from_dict(row) for row in rows]
        except Error as e:
            logging.error(f"Lỗi khi lấy dữ liệu từ nhân viên còn làm việc: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
        
    def get_all_unavailable(self) -> List[NhanVien]:
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary= True)
            cursor.execute("select * from nhanvien where TrangThaiNhanVien = 'Đã nghỉ việc'")
            rows = cursor.fetchall()
            return [NhanVien.from_dict(row) for row in rows]
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi lấy dữ liệu từ nhân viên đã nghỉ việc: {e}") 
            return []
        finally:
            if cursor:
                cursor.close()

    def insert(self, nhanvien: NhanVien) -> bool:
        cursor = None
        if not nhanvien.ID_NhanVien:
            logging.warning("Thiếu mã nhân viên khi thêm.")
            return False 
        try:
            cursor = self.conn.cursor()
            query = """insert into nhanvien(ID_NhanVien, HoTen, GioiTinh, ChucVu, SoDienThoai, Email, TrangThaiNhanVien, HinhAnh)
                   values (%s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (
            nhanvien.ID_NhanVien,
            nhanvien.HoTen,
            nhanvien.GioiTinh,
            nhanvien.ChucVu,
            nhanvien.SoDienThoai,
            nhanvien.Email,
            nhanvien.TrangThaiNhanVien,
            nhanvien.HinhAnh,
            ))
            self.conn.commit()
            logging.info("Đã thêm nhân viên thành công!")
            return True
        except Error as e:
            self.conn.rollback()
            if "Duplicate entry" in str(e):
                logging.warning(f"Mã nhân vien: {nhanvien.ID_NhanVien} đã tồn tại")
                return False
            else:
                logging.error(f"Đã xảy ra lỗi khi thêm nhân viên: {e}")
                return False
        finally:
            if cursor:
                cursor.close()

    def update(self, nhanvien: NhanVien) -> bool:
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = """update nhanvien
                       set HoTen = %s, GioiTinh = %s, ChucVu = %s, SoDienThoai = %s, Email = %s, TrangThaiNhanVien = %s, HinhAnh = %s
                       where ID_NhanVien = %s"""
            cursor.execute(query, (
                nhanvien.HoTen,
                nhanvien.GioiTinh,
                nhanvien.ChucVu,
                nhanvien.SoDienThoai,
                nhanvien.Email,
                nhanvien.TrangThaiNhanVien,
                nhanvien.HinhAnh,
                nhanvien.ID_NhanVien
            ))
            self.conn.commit()
            return cursor.rowcount > 0
        except Error as e:
            self.conn.rollback()
            logging.error(f"Lỗi xảy ra khi cập nhật thông tin nhân viên: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def find_by_key(self, ma_nhanvien: str) -> Optional[NhanVien]:
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary= True)
            cursor.execute("select * from nhanvien where ID_NhanVien = %s", (ma_nhanvien,))
            row = cursor.fetchone()
            if not row:
                logging.error(f"Không tìm thấy nhân viên có mã {ma_nhanvien}")
                return None
            return NhanVien.from_dict(row)
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi tìm kiếm nhân viên theo mã: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

    def search_by_name(self, keyword: str) ->List[NhanVien]:
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary=True)
            query = "select * from nhanvien where lower(HoTen) like lower(%s)"
            cursor.execute(query, (f"%{keyword}%",))
            rows = cursor.fetchall()
            return [NhanVien.from_dict(row) for row in rows]
        except Error as e:
            logging.error(f"Lỗi khi tìm kiếm nhân viên theo tên: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

        
    def delete(self, ma_nhanvien: str) -> bool:
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("update nhanvien set TrangThaiNhanVien = 'Đã nghỉ việc' where ID_NhanVien = %s", (ma_nhanvien,))
            if cursor.rowcount == 0:
                logging.warning(f"Không tìm thấy nhân viên để xóa: {ma_nhanvien}")
            self.conn.commit()
            return cursor.rowcount > 0
        except Error as e:
            self.conn.rollback()
            logging.error(f"Đã xảy ra lỗi khi xóa mềm nhân viên: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def completely_delete(self, ma_nhanvien: str) -> bool:
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("delete from nhanvien where ID_NhanVien = %s", (ma_nhanvien,))
            self.conn.commit()
            return cursor.rowcount > 0
        except Error as e:
            self.conn.rollback()
            logging.error(f"Đã xảy ra lỗi khi xóa hoàn toàn nhân viên: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    #các hàm nâng cao

    def restore(self, id_nhanvien: str) -> bool:
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("update nhanvien set TrangThaiNhanVien = 'Đang làm việc' where ID_NhanVien = %s", (id_nhanvien,))
            self.conn.commit()
            return cursor.rowcount > 0
        except Error as e:
            self.conn.rollback()
            logging.error(f"Đã xảy ra lỗi khi khôi phục lại nhân viên: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
    
    def get_total_employee(self) -> int:
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("select count(*) from nhanvien where TrangThaiNhanVien = 'Đang làm việc'")
            result = cursor.fetchone()
            return result[0] if result else 0
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi đếm các nhân viên còn làm việc: {e}")
            return 0
        finally:
            if cursor:
                cursor.close()

    def get_employee_by_role(self, chucvu: str) -> List[NhanVien]:
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary=True) # Sửa ở đây
            cursor.execute("SELECT * FROM nhanvien WHERE TrangThaiNhanVien = 'Đang làm việc' AND ChucVu = %s", (chucvu,))
            rows = cursor.fetchall()
            return [NhanVien.from_dict(row) for row in rows]
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi lấy danh sách các nhân viên có chức vụ {chucvu}: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_statistics_by_status(self) -> List[dict]:
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = """select TrangThaiNhanVien, count(*) as SoLuong
                       from nhanvien
                       group by TrangThaiNhanVien"""
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi đếm các nhân viên còn đi làm và đã nghỉ việc: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_all_roles(self) -> List[str]:
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("select distinct ChucVu from nhanvien")
            roles = [row[0] for row in cursor.fetchall()]
            return roles
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi lấy các chức vụ hiện có: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def check_exists(self, id_nhanvien: str) -> bool:
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("select 1 from nhanvien where ID_NhanVien = %s", (id_nhanvien,))
            return cursor.fetchone() is not None
        except Error as e:
            logging.error(f"Đã xảy ra lỗi khi kiểm tra sự tồn tại nhân viên {id_nhanvien}: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    
        

    
