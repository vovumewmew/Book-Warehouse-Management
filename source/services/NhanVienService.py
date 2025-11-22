from typing import List, Optional
import logging 

from config.baseservice import BaseService
from source.models.NhanVien import NhanVien
from source.dao.NhanVienDAO import NhanVienDAO

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class NhanVienService(BaseService):
    def __init__(self, dao: NhanVienDAO):
        super().__init__(dao)
        self.dao = dao

    def get_all(self) -> List[NhanVien]:
        try:
            ds_nhanvien = self.dao.get_all()
            self.log_action("GET ALL", f"Đã lấy toàn bộ danh sách nhân viên")
            return ds_nhanvien
        except Exception as e:
            self.handle_error(e)
            return []
        
    def get_unavailable_employee(self) -> List[NhanVien]:
        try:
            ds_nhanvien = self.dao.get_all_unavailable()
            self.log_action("GET ALL UNAVAILABLE","Đã lấy danh sách các nhân viên bị xóa")
            return ds_nhanvien
        except Exception as e:
            self.handle_error(e)
            return []
    
    def create(self, nhanvien: NhanVien) -> bool:
        try:
            self.validate_not_null(nhanvien.ID_NhanVien, "Mã nhân viên")
            if self.check_exists(nhanvien.ID_NhanVien):
                raise ValueError(f"Mã nhân viên '{nhanvien.ID_NhanVien}' đã tồn tại.")
            result = self.execute_transaction(self.dao.insert, nhanvien)
            if result:
                self.log_action("CREATE", f"Đã thêm nhân viên có mã {nhanvien.HoTen} ({nhanvien.ID_NhanVien})")
            return result
        except ValueError as ve:
            # Ném lại lỗi validation hoặc lỗi trùng lặp để UI bắt
            raise ve
        except Exception as e:
            self.handle_error(e)
            return False
        
    def update(self, nhanvien: NhanVien) -> bool:
        try:
            if not self.check_exists(nhanvien.ID_NhanVien):
                logging.error(f"Mã nhân viên {nhanvien.ID_NhanVien} không tồn tại!")
                return False
            result = self.execute_transaction(self.dao.update, nhanvien)
            if result:
                self.log_action("UPDATE", f"Đã cập nhật thông tin nhân viên {nhanvien.HoTen} ({nhanvien.ID_NhanVien})")
            return result
        except Exception as e:
            self.handle_error(e)
            return False
        
    def find_by_id(self, id_nhanvien: str) -> Optional[NhanVien]:
        try:
            nhanvien = self.dao.find_by_key(id_nhanvien)
            if not nhanvien:
                logging.info(f"Không thể tìm thấy nhân viên có mã {id_nhanvien}")
                return None
            return nhanvien
        except Exception as e:
            logging.error(f"Không tìm thấy nhân viên có mã {id_nhanvien}")
            self.handle_error(e)
            return None
    
    def search_by_name(self, hoten: str) -> List[NhanVien]:
        try:
            nhanvien = self.dao.search_by_name(hoten)
            if not nhanvien:
                logging.info(f"Không tìm thấy nhân viên có tên {hoten}")
                return []
            return nhanvien
        except Exception as e:
            logging.error(f"Không tìm thấy nhân viên có tên {hoten}")
            self.handle_error(e)
            return []
        
    def delete(self, id_nhanvien: str) -> bool:
        try:
            if not self.check_exists(id_nhanvien):
                logging.error(f"Mã nhân viên {id_nhanvien} không tồn tại")
                return False
            result = self.execute_transaction(self.dao.delete, id_nhanvien)
            if result:
                self.log_action("DELETE", f"Đã xóa thành công nhân viên có mã {id_nhanvien}")
            return result
        except Exception as e:
            self.handle_error(e)
            return False
    
    def completely_delete(self, id_nhanvien: str) -> bool:
        try:
            result = self.execute_transaction(self.dao.completely_delete, id_nhanvien)
            if result:
                self.log_action("COMPLETELY DELETE", f"Đã xóa hoàn toàn nhân viên có mã {id_nhanvien}")
            return result
        except Exception as e:
            self.handle_error(e)
            return False

    def check_exists(self, id_nhanvien: str) -> bool:
        try: 
            return self.dao.check_exists(id_nhanvien)
        except Exception as e:
            self.handle_error(e)
            return False
        
    #các hàm nâng cao
    def restore(self, ids: List[str]) -> int:
        try:
            restored_count = 0
            for employee_id in ids:
                if not self.check_exists(employee_id):
                    logging.error(f"Không tìm thấy nhân viên có mã {employee_id} để khôi phục")
                    continue
                if self.execute_transaction(self.dao.restore, employee_id):
                    restored_count += 1
            self.log_action("RESTORE", f"Đã khôi phục {restored_count}/{len(ids)} nhân viên.")
            return restored_count
        except Exception as e:
            self.handle_error(e)
            return 0
        
    def get_total_employee(self) -> int:
        try:
            return self.dao.get_total_employee()
        except Exception as e:
            self.handle_error(e)
            return 0
    
    def get_employee_by_role(self, chucvu: str) -> List[NhanVien]:
        try:
            employee_by_role = self.dao.get_employee_by_role(chucvu)
            self.log_action(f"GET ALL ROLES", f"Đã lấy toàn bộ nhân viên theo chức vụ '{chucvu}'")
            return employee_by_role
        except Exception as e:
            self.handle_error(e)
            return []
        
    def get_all_roles(self) -> List[str]:
        try:
            roles = self.dao.get_all_roles()
            self.log_action("GET ALL 'Chuc Vu'", f"Đã lấy toàn bộ chức vụ")
            return roles
        except Exception as e:
            self.handle_error(e)
            return []
        
    def get_statistics_by_status(self) -> List[dict]:
        try:
            return self.dao.get_statistics_by_status()
        except Exception as e:
            self.handle_error(e)
            return []