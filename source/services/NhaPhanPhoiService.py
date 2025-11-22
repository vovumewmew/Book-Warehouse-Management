from typing import List, Optional
import logging

from source.models.NhaPhanPhoi import NhaPhanPhoi
from source.dao.NhaPhanPhoiDAO import NhaPhanPhoiDAO
from config.baseservice import BaseService 

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class NhaPhanPhoiService(BaseService):
    def __init__(self, dao: NhaPhanPhoiDAO):
        super().__init__(dao)
        self.dao = dao

    def get_all(self) -> List[NhaPhanPhoi]:
        try:
            contributors = self.dao.get_all()
            self.log_action("GET ALL", f"Đã lấy {len(contributors)} nhà phân phối khả dụng")
            return contributors
        except Exception as e:
            self.handle_error(e)
            return []
        
    def get_unavailable_contributors(self) -> List[NhaPhanPhoi]:
        try:
            contributors = self.dao.get_all_unavailable()
            self.log_action("GET ALL UNAVAILABLE", f"Đã lấy {len(contributors)} phân phối đã bị xóa")
            return contributors
        except Exception as e:
            self.handle_error(e)
            return []
        
    def create(self, nhaphanphoi: NhaPhanPhoi) -> bool:
        try:
            self.validate_not_null(nhaphanphoi.ID_NguonXuat, "Mã Nhà phân phối")
            if self.check_exists(nhaphanphoi.ID_NguonXuat):
                raise ValueError(f"Mã nhà phân phối '{nhaphanphoi.ID_NguonXuat}' đã tồn tại.")
            result = self.execute_transaction(self.dao.insert, nhaphanphoi)
            if result:
                self.log_action("CREATE", f"Đã thêm vào nhà phân phối {nhaphanphoi.TenCoSo} ({nhaphanphoi.ID_NguonXuat})")
            return result
        except ValueError as ve:
            # Ném lại lỗi validation hoặc lỗi trùng lặp để UI bắt
            raise ve
        except Exception as e:
            self.handle_error(e)
            return False
        
    def update(self, nhaphanphoi: NhaPhanPhoi) -> bool:
        try:
            if not self.check_exists(nhaphanphoi.ID_NguonXuat):
                logging.warning(f"Mã nhà phân phối {nhaphanphoi.ID_NguonXuat} cần cập nhật không tồn tại!")
                return False
            result = self.execute_transaction(self.dao.update, nhaphanphoi)
            if result:
                self.log_action("UPDATE", f"Đã cập nhật thành công cho nhà phân phối {nhaphanphoi.TenCoSo} ({nhaphanphoi.ID_NguonXuat})")
            return result
        except Exception as e:
            self.handle_error(e)
            return False
        
    def find_by_id(self, id_nhaphanphoi: str) -> Optional[NhaPhanPhoi]:
        try:
            contributors = self.dao.find_by_key(id_nhaphanphoi)
            if not contributors:
                logging.error(f"Không tìm thấy nhà phân phối có mã {id_nhaphanphoi}")
                return None
            return contributors
        except Exception as e:
            self.handle_error(e)
            return None
        
    def delete(self, id_nhaphanphoi: str) -> bool:
        try:
            if not self.check_exists(id_nhaphanphoi):
                logging.warning(f"nhà phân phối có mã {id_nhaphanphoi} không tồn tại")
                return False
            result = self.execute_transaction(self.dao.delete, id_nhaphanphoi)
            if result:
                self.log_action("DELETE", f"Đã xóa mềm thành công nhà phân phối có mã {id_nhaphanphoi}")
            return result
        except Exception as e:
            self.handle_error(e)
            return False
        
    def completely_delete(self, id_nhaphanphoi: str) -> bool:
        try:
            result = self.execute_transaction(self.dao.completely_delete, id_nhaphanphoi)
            if result:
                self.log_action("COMPLETELY DELETE", f"Đã xóa hoàn toàn nhà phân phối có mã {id_nhaphanphoi}")
            return result
        except Exception as e:
            self.handle_error(e)
            return False
        
    #các hàm nâng cao

    def restore(self, ids: List[str]) -> int:
        try:
            restored_count = 0
            for distributor_id in ids:
                if not self.check_exists(distributor_id):
                    logging.error(f"Không tìm thấy nhà phân phối có mã {distributor_id} để khôi phục")
                    continue
                if self.execute_transaction(self.dao.restore, distributor_id):
                    restored_count += 1
            self.log_action("RESTORE", f"Đã phục hồi {restored_count}/{len(ids)} nhà phân phối.")
            return restored_count
        except Exception as e:
            self.handle_error(e)
            return 0
        
    def get_top_distributors_by_orders(self, limit: int = 5) -> List[dict]:
        try:
            result = self.dao.get_top_distributors_by_orders(limit)
            if result:
                self.log_action("GET TOP DISTRIBUTORS BY ORDERS", "Đã lấy các nhà phân phối theo số lượng phiếu xuất nhiều nhất")
            return result
        except Exception as e:
            self.handle_error(e)
            return []
    
    def get_distributor_performance_summary(self) -> List[dict]:
        try:
            result = self.dao.get_distributor_performance_summary()
            if result:
                self.log_action("GET DISTRIBUTOR PERFORMANCE SUMMARY", "Đã tổng kết hiệu suất nhà phân phối")
            return result
        except Exception as e:
            self.handle_error(e)
            return []
        
    def get_total_distributor_by_status(self) -> dict:
        try:
            return self.dao.get_total_distributor_by_status()
        except Exception as e:
            self.handle_error(e)
            return {}
        
    def get_statistics_by_status(self) -> List[dict]:
        try:
            return self.dao.get_statistics_by_status()
        except Exception as e:
            self.handle_error(e)
            return []
            
    def check_exists(self, id_nhaphanphoi: str) -> bool:
        try:
            return self.dao.check_exists(id_nhaphanphoi)
        except Exception as e:
            self.handle_error(e)
            return False

    def count_all(self) -> int:
        try:
            return self.dao.count_all()
        except Exception as e:
            self.handle_error(e)
            return 0