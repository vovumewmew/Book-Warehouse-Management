from typing import List, Optional
import logging
from decimal import Decimal

from config.baseservice import BaseService
from source.dao.SachDAO import SachDAO
from source.models.Sach import Sach

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class SachService(BaseService):
    def __init__(self, dao: SachDAO):
        super().__init__(dao)
        self.dao: SachDAO = dao

    def get_all(self) -> List[Sach]:
        try: 
            books = self.dao.get_all()
            self.log_action("GET_ALL", f"Lấy {len(books)} sách khả dụng")
            return books
        except Exception as e:
            self.handle_error(e)
            return []
        
    def create(self, sach: Sach) -> bool:
        try:
            self.validate_not_null(sach.ID_Sach, "Mã Sách")
            self.validate_not_null(sach.TenSach, "Tên Sách")
            if self.check_exists(sach.ID_Sach):
                raise ValueError(f"Mã sách '{sach.ID_Sach}' đã tồn tại.")
            result = self.execute_transaction(self.dao.insert, sach)
            if result:
                self.log_action("CREATE", f"Đã thêm sách {sach.TenSach} ({sach.ID_Sach})")
            return result
        except ValueError as ve:
            # Ném lại lỗi validation hoặc lỗi trùng lặp để UI bắt
            raise ve
        except Exception as e:
            self.handle_error(e)
            return False
    
    def update(self, sach: Sach) -> bool:
        try:
            if not self.dao.check_exists(sach.ID_Sach):
                logging.error(f"Không tồn tại sách có mã {sach.ID_Sach}")
                return False
            result = self.execute_transaction(self.dao.update, sach)
            if result:
                self.log_action("UPDATE", f"Đã cập nhật thành công sách '{sach.TenSach}' ({sach.ID_Sach})")
            return result
        except Exception as e:
            self.handle_error(e)
            return False
        
    def find_by_id(self, id_sach: str) -> Optional[Sach]:
        try:
            sach = self.dao.find_by_key(id_sach)
            if not sach:
                logging.info(f"Không tìm thấy sách có mã {id_sach}")
            return sach
        except Exception as e:
            logging.error(f"Không tìm thấy sách có mã: {id_sach}")
            self.handle_error(e)
            return None
    
    def delete(self, id_sach: str) -> bool:
        try:
            if not self.dao.check_exists(id_sach):
                logging.warning(f"Không tìm thấy sách có mã {id_sach} để xóa")
                return False
            result = self.execute_transaction(self.dao.delete, id_sach)
            if result:
                self.log_action("DELETE", f"Đã xóa mềm sách có mã {id_sach}")
            return result
        except Exception as e:
            self.handle_error(e)
            return False
    
    def completely_delete(self, id_sach: str) -> bool:
        try:
            result = self.execute_transaction(self.dao.completely_delete, id_sach)
            if result:
                self.log_action("COMPLETELY_DELETE", f"Đã xóa vĩnh viễn sách có mã {id_sach}")
            return result
        except Exception as e:
            self.handle_error(e)
            return False
    
    #các service nâng cao

    def restore_books(self, ids: List[str]) -> int:
        try:
            restore_sach = 0
            for id_sach in ids:
                if self.execute_transaction(self.dao.restore, id_sach):
                    restore_sach += 1
        
            self.log_action("RESTORE", f"Khôi phục thành công sách {restore_sach}/{len(ids)} sách")
            return restore_sach
        except Exception as e:
            self.handle_error(e)
            return 0
    
    def get_unavailable_books(self) -> List[Sach]:
        try:
            return self.dao.get_unavailable()
        except Exception as e:
            self.handle_error(e)
            return []
        
    def filter_by_category(self, theloai: str) -> List[Sach]:
        try:
            return self.dao.filter_by_category(theloai)
        except Exception as e:
            self.handle_error(e)
            return []
        
    def get_low_stock_books(self, threshold: int = 5) -> List[Sach]:
        try:
            return self.dao.get_low_stock_books(threshold)
        except Exception as e:
            self.handle_error(e)
            return []
        
    def update_stock(self, id_sach: str, soluongmoi: int) -> bool:
        if soluongmoi < 0:
            logging.error("Số lượng mới không hợp lệ!")
            return False
        return self.execute_transaction(self.dao.update_stock, id_sach, soluongmoi)
    
    def check_exists(self, id_sach: str) -> bool:
        try:
            return self.dao.check_exists(id_sach)
        except Exception as e:
            self.handle_error(e)
            return False
        
    def count_books(self) -> int: 
        try:
            return self.dao.count_books()
        except Exception as e:
            self.handle_error(e)
            return 0
        
    def search_by_name(self, tensach: str) -> List[Sach]:
        try:
            return self.dao.search_by_name(tensach)
        except Exception as e:
            self.handle_error(e)
            return []
        
    def get_total_stock_value(self) -> Decimal:
        try:
            return self.dao.get_total_stock_value()
        except Exception as e:
            self.handle_error(e)
            return Decimal('0')

    def count_out_of_stock_books(self) -> int:
        try:
            return self.dao.count_out_of_stock_books()
        except Exception as e:
            self.handle_error(e)
            return 0

    def count_low_stock_books(self, threshold: int = 5) -> int:
        try:
            return self.dao.count_low_stock_books(threshold)
        except Exception as e:
            self.handle_error(e)
            return 0

    def get_category_statistics(self) -> List[tuple[str, int]]:
        try:
            return self.dao.get_category_statistics()
        except Exception as e:
            self.handle_error(e)
            return []
        
