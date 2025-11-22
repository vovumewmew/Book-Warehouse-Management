from typing import List, Optional
from datetime import date
from decimal import Decimal
import logging

from config.baseservice import BaseService
from config.db_connection import DatabaseConnection

from source.dao.PhieuXuatSachDAO import PhieuXuatSachDAO
from source.services.ChiTietPhieuXuatService import ChiTietPhieuXuatService
from source.services.SachService import SachService
from source.models.PhieuXuatSach import PhieuXuatSach

class PhieuXuatSachService(BaseService):
    def __init__(self, dao: PhieuXuatSachDAO):
        super().__init__(dao)
        self.dao: PhieuXuatSachDAO = dao
        self.ct_service = None  # sẽ được set sau (để tránh import vòng)
        self.sach_service = None # sẽ được set sau

    def set_chitiet_service(self, ct_service: ChiTietPhieuXuatService):
        self.ct_service = ct_service

    def set_sach_service(self, sach_service: 'SachService'):
        self.sach_service = sach_service

    def create(self, phieu: PhieuXuatSach) -> bool:
        def action():
            # Kiểm tra mã phiếu đã tồn tại chưa
            if self.dao.find_by_key(phieu.ID_PhieuXuat):
                return False # Trả về False nếu đã tồn tại

            if not self.dao.insert(phieu):
                raise Exception("Không thể thêm phiếu xuất sách vào CSDL!")
            
            if not phieu.Danhsachchitietxuat:
                raise Exception("Phiếu xuất không có chi tiết nào!")

            for ct in phieu.Danhsachchitietxuat:
                ct.phieu_xuat = phieu

            if not self.ct_service.dao.bulk_insert(phieu.Danhsachchitietxuat):
                raise Exception("Thêm chi tiết phiếu xuất thất bại!")

            # Cập nhật (giảm) số lượng sách trong kho
            for ct in phieu.Danhsachchitietxuat:
                sach_trong_kho = self.sach_service.find_by_id(ct.sach.ID_Sach)
                if sach_trong_kho.SoLuong < ct.SoLuong:
                    raise Exception(f"Số lượng tồn kho của sách '{ct.sach.TenSach}' không đủ để xuất.")
                so_luong_moi = sach_trong_kho.SoLuong - ct.SoLuong
                if not self.sach_service.update_stock(ct.sach.ID_Sach, so_luong_moi):
                    raise Exception(f"Cập nhật số lượng cho sách {ct.sach.ID_Sach} thất bại!")

            if not self.dao.auto_update_total(phieu.ID_PhieuXuat):
                raise Exception(f"Không thể cập nhật tổng cho phiếu {phieu.ID_PhieuXuat}")

            self.log_action("CREATE", f"Đã tạo phiếu xuất {phieu.ID_PhieuXuat} với {len(phieu.Danhsachchitietxuat)} chi tiết")
            return True

        return self.execute_transaction(lambda: action())


    def get_all(self) -> List[PhieuXuatSach]:
        try:
            phieu_list = self.dao.get_all()
            for phieu in phieu_list:
                phieu.Danhsachchitietxuat = self.ct_service.get_by_phieu(phieu.ID_PhieuXuat)
            return phieu_list
        except Exception as e:
            self.handle_error(e)
            return []

    def find_by_id(self, id_phieuxuat: str) -> Optional[PhieuXuatSach]:
        try:
            phieu = self.dao.find_by_key(id_phieuxuat)
            if phieu:
                phieu.Danhsachchitietxuat = self.ct_service.get_by_phieu(id_phieuxuat)
            return phieu
        except Exception as e:
            self.handle_error(e)
            return None

    def update(self, phieu: PhieuXuatSach) -> bool:
        try:
            # Gọi trực tiếp dao.update trong transaction, giống như SachService
            result = self.execute_transaction(self.dao.update, phieu)
            if result:
                self.log_action("UPDATE", f"Đã cập nhật phiếu xuất {phieu.ID_PhieuXuat}")
            return result
        except Exception as e:
            self.handle_error(e)
            return False

    def delete(self, id_phieuxuat: str) -> bool:
        def action(id_pxs: str):
            # Lấy thông tin chi tiết phiếu xuất TRƯỚC KHI XÓA
            phieu_can_xoa = self.find_by_id(id_pxs)
            if not phieu_can_xoa:
                raise Exception(f"Không tìm thấy phiếu xuất {id_pxs} để xóa.")

            # Hoàn tác số lượng sách trong kho (CỘNG trả lại số lượng đã xuất)
            for ct in phieu_can_xoa.Danhsachchitietxuat:
                sach_trong_kho = self.sach_service.find_by_id(ct.sach.ID_Sach)
                so_luong_moi = sach_trong_kho.SoLuong + ct.SoLuong
                if not self.sach_service.update_stock(ct.sach.ID_Sach, so_luong_moi):
                    raise Exception(f"Cập nhật (hoàn tác) số lượng cho sách {ct.sach.ID_Sach} thất bại!")

            # Xóa tất cả chi tiết phiếu xuất
            if not self.ct_service.delete_all_by_phieu(id_pxs):
                logging.warning(f"Không có chi tiết nào để xóa cho phiếu {id_pxs} hoặc đã có lỗi.")
            # Xóa phiếu xuất
            if not self.dao.delete(id_phieuxuat):
                raise Exception("Không thể xóa phiếu xuất.")
            self.log_action("DELETE", f"Đã xóa phiếu xuất {id_phieuxuat} và hoàn tác số lượng kho.")
            return True

        return self.execute_transaction(action, id_phieuxuat)
    
    #các hàm nâng cao

    def get_total(self, id_phieuxuat: str) -> tuple[int, Decimal]:
        try:
            return self.dao.get_total(id_phieuxuat)
        except Exception as e:
            self.handle_error(e)
            return (0, Decimal("0.0"))
        
    def auto_update_total(self, id_phieuxuat: str) -> bool:
        def action():
            success = self.dao.auto_update_total(id_phieuxuat)
            if not success:
                raise Exception(f"Cập nhật tổng thất bại cho phiếu xuất {id_phieuxuat}!")
            return True

        return self.execute_transaction(
            action, id_phieuxuat
        )
    
    def get_recent(self, limit: int = 10) -> List[PhieuXuatSach]:
        try:
            result = self.dao.get_recent(limit)
            if result:
                self.log_action("GET RECENT", f"Đã lấy {limit} phiếu xuất gần nhất")
            return result
        except Exception as e:
            self.handle_error(e)
            return []
    
    def search_by_date_range(self, start_date: date, end_date: date) -> List[PhieuXuatSach]:
        try:
            result = self.dao.search_by_date_range(start_date, end_date)
            if result:
                self.log_action("SEARCH BY DATE RANGE", f"Đã lấy các phiếu xuất trong khoảng {start_date} đến {end_date}")
            return result
        except Exception as e:
            self.handle_error(e)
            return []
        
    def get_by_id_nhanvien(self, id_nhanvien: str) -> List[PhieuXuatSach]:
        try:
            phieu_list = self.dao.get_by_id_nhanvien(id_nhanvien)
            for phieu in phieu_list:
                phieu.Danhsachchitietxuat = self.ct_service.get_by_phieu(phieu.ID_PhieuXuat)
            return phieu_list
        except Exception as e:
            self.handle_error(e)
            return []
        
    def get_total_revenue(self, start_date: date, end_date: date) -> Decimal:
        try:
            result = self.dao.get_total_revenue(start_date, end_date)
            if result:
                self.log_action("GET TOTAL REVENUE", f"Đã tính tổng tiền phiếu xuất trong khoảng {start_date} đến {end_date}")
            return result
        except Exception as e:
            self.handle_error(e)
            return Decimal("0.0")
        
    def count_by_employee(self) -> List[tuple[str, int]]:
        try:
            return self.dao.count_by_employee()
        except Exception as e:
            self.handle_error(e)
            return []
        
    def get_monthly_revenue(self) -> List[tuple[int, Decimal]]:
        try:
            return self.dao.get_monthly_revenue()
        except Exception as e:
            self.handle_error(e)
            return []
        
    def get_highest_value_invoice(self) -> Optional[PhieuXuatSach]:
        try:
            result = self.dao.get_highest_value_invoice()
            if result:
                self.log_action("GET HIGHEST VALUE INVOICE", "Đã lấy phiếu xuất có tổng tiền lớn nhất")
            return result
        except Exception as e:
            self.handle_error(e)
            return None
        
    def get_by_sach(self, id_sach: str) -> List[PhieuXuatSach]:
        try:
            phieu_list = self.dao.get_by_sach(id_sach)
            for phieu in phieu_list:
                phieu.Danhsachchitietxuat = self.ct_service.get_by_phieu(phieu.ID_PhieuXuat)
            return phieu_list
        except Exception as e:
            self.handle_error(e)
            return []
        
    def get_summary_by_date_range(self, start_date: date, end_date: date) -> tuple[int, Decimal]:
        try:
            return self.dao.get_summary_by_date_range(start_date, end_date)
        except Exception as e:
            self.handle_error(e)
            return (0, Decimal("0.0"))
        
    def get_current_month(self) -> List[PhieuXuatSach]:
        try:
            result = self.dao.get_current_month()
            if result:
                self.log_action("GET CURRENT MONTH", "Đã lấy các phiếu xuất trong tháng này")
            return result
        except Exception as e:
            self.handle_error(e)
            return []
        
    def count_current_month(self) -> int:
        try:
            return self.dao.count_current_month()
        except Exception as e:
            self.handle_error(e)
            return 0
        
    def get_current_month_revenue(self) -> Decimal:
        try:
            return self.dao.get_current_month_revenue()
        except Exception as e:
            self.handle_error(e)
            return Decimal('0')

    def get_monthly_statistics(self, year: int) -> List[tuple[int, int, Decimal]]:
        try:
            return self.dao.get_monthly_statistics(year)
        except Exception as e:
            self.handle_error(e)
            return [] 

    def search(self, keyword: str) -> List[PhieuXuatSach]:
        try:
            phieu_list = self.dao.search(keyword)
            for phieu in phieu_list:
                phieu.Danhsachchitietxuat = self.ct_service.get_by_phieu(phieu.ID_PhieuXuat)
            return phieu_list
        except Exception as e:
            self.handle_error(e)
            return []
