import logging
from typing import List, Optional

from source.models.NguonNhapSach import NguonNhapSach
from source.dao.NguonNhapSachDAO import NguonNhapSachDAO
from config.baseservice import BaseService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class NguonNhapSachService(BaseService):
    def __init__(self, dao: NguonNhapSachDAO):
        super().__init__(dao)
        self.dao = dao

    def get_all(self) -> List[NguonNhapSach]:
        try:
            suppliers = self.dao.get_all()
            self.log_action("GET ALL", "Đã lấy toàn bộ danh sách các nguồn nhập sách")
            return suppliers
        except Exception as e:
            self.handle_error(e)
            return []
    
    def get_unavailable_suppliers(self) -> List[NguonNhapSach]:
        try:
            suppliers = self.dao.get_all_unavailable()
            self.log_action("GET ALL UNAVAILABLE", "Đã lấy toàn bộ danh sách các nguồn nhập sách không khả dụng")
            return suppliers
        except Exception as e:
            self.handle_error(e)
            return []
        
    def create(self, nguonhapsach: NguonNhapSach) -> bool:
        try:
            self.validate_not_null(nguonhapsach.ID_NguonNhap, "Mã nguồn nhập sách")
            if self.check_exists(nguonhapsach.ID_NguonNhap):
                raise ValueError(f"Mã nguồn nhập '{nguonhapsach.ID_NguonNhap}' đã tồn tại.")
            result = self.execute_transaction(self.dao.insert, nguonhapsach)
            if result:
                self.log_action("CREATE", f"Đã tạo nguồn nhập sách {nguonhapsach.TenCoSo} ({nguonhapsach.ID_NguonNhap})")
            return result
        except ValueError as ve:
            # Ném lại lỗi validation hoặc lỗi trùng lặp để UI bắt
            raise ve
        except Exception as e:
            self.handle_error(e)
            return False
    
    def update(self, nguonnhapsach: NguonNhapSach) -> bool:
        try:
            if not self.check_exists(nguonnhapsach.ID_NguonNhap):
                logging.error(f"Không tìm thấy nguồn nhập {nguonnhapsach.ID_NguonNhap} để cập nhật")
                return False
            result = self.execute_transaction(self.dao.update, nguonnhapsach)
            if result:
                self.log_action("UPDATE", f"Đã cập nhật thành công cho nguồn nhập sách {nguonnhapsach.TenCoSo} ({nguonnhapsach.ID_NguonNhap})")
            return result  
        except Exception as e:
            self.handle_error(e)
            return False

    def find_by_id(self, id_nguonnhap: str) -> Optional[NguonNhapSach]:
        try:
            suppliers = self.dao.find_by_key(id_nguonnhap)
            if not suppliers:
                logging.error(f"Không thể tìm thấy nguồn nhập sách có mã {id_nguonnhap}")
                return None
            return suppliers
        except Exception as e:
            self.handle_error(e)
            return None
        
    def delete(self, id_nguonnhap: str) -> bool:
        try:
            if not self.check_exists(id_nguonnhap):
                logging.error(f"Không thể tìm thấy nguồn nhập sách có mã {id_nguonnhap} cần xóa")
                return False
            result = self.execute_transaction(self.dao.delete, id_nguonnhap)
            if result:
                self.log_action("DELETE", f"Đã xóa nguồn nhập có mã {id_nguonnhap}")
            return result
        except Exception as e:
            self.handle_error(e)
            return False
        
    def completely_delete(self, id_nguonnhap: str) -> bool:
        try:
            result = self.execute_transaction(self.dao.completely_delete, id_nguonnhap)
            if result:
                self.log_action("COMPLETELY DELETE", f"Đã xóa hoàn toàn nguồn nhập có mã {id_nguonnhap}")
            return result
        except Exception as e:
            self.handle_error(e)
            return False
    
    def check_exists(self, id_nguonnhap: str) -> bool:
        try:
            return self.dao.check_exists(id_nguonnhap)
        except Exception as e:
            self.handle_error(e)
            return False
        
    #các hàm nâng cao

    def restore(self, ids: List[str]) -> int:
        try:
            restored_count = 0
            for supplier_id in ids:
                if not self.check_exists(supplier_id):
                    logging.error(f"Không tìm thấy nguồn nhập có mã {supplier_id} để khôi phục")
                    continue
                if self.execute_transaction(self.dao.restore, supplier_id):
                    restored_count += 1
            self.log_action("RESTORE", f"Đã phục hồi thành công {restored_count}/{len(ids)} nhà cung cấp.")
            return restored_count
        except Exception as e:
            self.handle_error(e)
            return 0
        
    def get_top_suppliers_by_orders(self, limit: int = 5) -> List[dict]:
        try:
            result = self.dao.get_top_suppliers_by_orders(limit)
            if result:
                self.log_action("GET TOP SUPPLIERS BY ORDERS", "Đã lấy các nguồn nhập sách theo số lượng phiếu nhập nhiều nhất")
            return result
        except Exception as e:
            self.handle_error(e)
            return []
    
    def get_suppliers_performance_summary(self) -> List[dict]:
        try:
            result = self.dao.get_supplier_performance_summary()
            if result:
                self.log_action("GET SUPPLIERS PERFORMANCE SUMMARY", "Đã tổng kết chất lượng nguồn nhập sách")
            return result
        except Exception as e:
            self.handle_error(e)
            return []
        
    def get_total_suppliers_by_status(self) -> dict:
        try:
            return self.dao.get_total_suppliers_by_status()
        except Exception as e:
            self.handle_error(e)
            return {}
        
    def get_statistics_by_status(self) -> List[dict]:
        try:
            return self.dao.get_statistics_by_status()
        except Exception as e:
            self.handle_error(e)
            return []

    def count_all(self) -> int:
        try:
            return self.dao.count_all()
        except Exception as e:
            self.handle_error(e)
            return 0
