import logging
from typing import List, Optional
from decimal import Decimal

from config.baseservice import BaseService
from source.dao.ChiTietPhieuXuatDAO import ChiTietPhieuXuatDAO
from source.models.ChiTietPhieuXuat import ChiTietPhieuXuat

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class ChiTietPhieuXuatService(BaseService):
    def __init__(self, dao: ChiTietPhieuXuatDAO):
        super().__init__(dao)
        self.dao: ChiTietPhieuXuatDAO = dao

    # ======================= CRUD =======================

    def get_all(self, id_phieuxuat: str) -> List[ChiTietPhieuXuat]:
        try:
            self.validate_not_null(id_phieuxuat, "Mã phiếu xuất")
            return self.dao.get_all(id_phieuxuat)
        except Exception as e:
            self.handle_error(e)
            return []

    def create(self, chitiet: ChiTietPhieuXuat) -> bool:
        try:
            if not chitiet.phieu_xuat or not chitiet.sach:
                logging.error("Chi tiết phiếu xuất thiếu thông tin phiếu hoặc sách!")
                return False
            if self.dao.exist(chitiet.phieu_xuat.ID_PhieuXuat, chitiet.sach.ID_Sach):
                logging.warning(
                    f"Sách {chitiet.sach.ID_Sach} đã tồn tại trong phiếu xuất {chitiet.phieu_xuat.ID_PhieuXuat}"
                )
                return False
            result = self.execute_transaction(self.dao.insert, chitiet)
            if result:
                self.log_action("CREATE DETAIL", f"Thêm chi tiết cho phiếu {chitiet.phieu_xuat.ID_PhieuXuat}")
            return result
        except Exception as e:
            self.handle_error(e)
            return False

    def update(self, chitiet: ChiTietPhieuXuat, id_sach: str) -> bool:
        try:
            if not chitiet.phieu_xuat or not id_sach:
                logging.error("Thiếu thông tin phiếu xuất hoặc mã sách!")
                return False
            if not self.dao.exist(chitiet.phieu_xuat.ID_PhieuXuat, id_sach):
                logging.error(f"Không tìm thấy sách {id_sach} trong phiếu {chitiet.phieu_xuat.ID_PhieuXuat}")
                return False
            result = self.execute_transaction(self.dao.update, chitiet, id_sach)
            if result:
                self.log_action("UPDATE DETAIL", f"Sửa chi tiết sách {id_sach} trong phiếu {chitiet.phieu_xuat.ID_PhieuXuat}")
            return result
        except Exception as e:
            self.handle_error(e)
            return False

    def find_by_id(self, id_phieuxuat: str, id_sach: str) -> Optional[ChiTietPhieuXuat]:
        try:
            export = self.dao.find_by_key(id_phieuxuat, id_sach)
            if not export:
                logging.error(f"Không tìm thấy sách {id_sach} trong phiếu xuất {id_phieuxuat}")
                return None
            return export
        except Exception as e:
            self.handle_error(e)
            return None

    def delete(self, id_phieuxuat: str, id_sach: str) -> bool:
        try:
            result = self.execute_transaction(self.dao.delete, id_phieuxuat, id_sach)
            if result:
                self.log_action("DELETE DETAIL", f"Xóa sách {id_sach} trong phiếu {id_phieuxuat}")
            return result
        except Exception as e:
            self.handle_error(e)
            return False

    def delete_all_by_phieu(self, id_phieuxuat: str) -> bool:
        try:
            result = self.execute_transaction(self.dao.delete_all_by_phieu, id_phieuxuat)
            if result:
                self.log_action("DELETE ALL DETAIL", f"Xóa toàn bộ chi tiết của phiếu {id_phieuxuat}")
            return result
        except Exception as e:
            self.handle_error(e)
            return False
        
#các hàm nâng cao

    def get_by_phieu(self, id_phieuxuat: str) -> List[ChiTietPhieuXuat]:
        try:
            return self.dao.get_by_phieu(id_phieuxuat)
        except Exception as e:
            self.handle_error(e)
            return []

    def get_by_sach(self, id_sach: str) -> List[ChiTietPhieuXuat]:
        try:
            return self.dao.get_by_sach(id_sach)
        except Exception as e:
            self.handle_error(e)
            return []

    def get_total_by_sach(self, id_sach: str) -> int:
        try:
            return self.dao.get_total_by_sach(id_sach)
        except Exception as e:
            self.handle_error(e)
            return 0

    def get_total_value_by_sach(self, id_sach: str) -> Decimal:
        try:
            return self.dao.get_total_value_by_sach(id_sach)
        except Exception as e:
            self.handle_error(e)
            return Decimal("0.0")

    def get_export_stats_by_month(self, year: int):
        try:
            return self.dao.get_export_stats_by_month(year)
        except Exception as e:
            self.handle_error(e)
            return []

    def get_avg_export_price_by_sach(self, id_sach: str) -> Decimal:
        try:
            return self.dao.get_avg_export_price_by_sach(id_sach)
        except Exception as e:
            self.handle_error(e)
            return Decimal("0.0")
