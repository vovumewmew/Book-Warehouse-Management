from typing import List, Optional
from datetime import date
from decimal import Decimal
import logging

from config.baseservice import BaseService
from config.db_connection import DatabaseConnection

from source.dao.PhieuNhapSachDAO import PhieuNhapSachDAO
from source.services.ChiTietPhieuNhapService import ChiTietPhieuNhapService
from source.services.SachService import SachService
from source.models.PhieuNhapSach import PhieuNhapSach

class PhieuNhapSachService(BaseService):
    def __init__(self, dao: PhieuNhapSachDAO):
        super().__init__(dao)
        self.dao: PhieuNhapSachDAO = dao
        self.ct_service = None  # sẽ được set sau (để tránh import vòng)
        self.sach_service = None # sẽ được set sau

    def set_chitiet_service(self, ct_service: 'ChiTietPhieuNhapService'):
        self.ct_service = ct_service

    def set_sach_service(self, sach_service: 'SachService'):
        self.sach_service = sach_service

    def create(self, phieu: PhieuNhapSach) -> bool:
        def action():
            # Kiểm tra mã phiếu đã tồn tại chưa
            if self.dao.find_by_key(phieu.ID_PhieuNhap):
                return False # Trả về False nếu đã tồn tại

            if not self.dao.insert(phieu):
                raise Exception("Không thể thêm phiếu nhập sách vào CSDL!")
            
            if not phieu.Danhsachchitietnhap:
                raise Exception("Phiếu nhập không có chi tiết nào!")

            for ct in phieu.Danhsachchitietnhap:
                ct.phieu_nhap = phieu

            if not self.ct_service.dao.bulk_insert(phieu.Danhsachchitietnhap):
                raise Exception("Thêm chi tiết phiếu nhập thất bại!")
            
            # Cập nhật số lượng sách trong kho
            for ct in phieu.Danhsachchitietnhap:
                sach_trong_kho = self.sach_service.find_by_id(ct.sach.ID_Sach)
                so_luong_moi = sach_trong_kho.SoLuong + ct.SoLuong
                if not self.sach_service.update_stock(ct.sach.ID_Sach, so_luong_moi):
                    raise Exception(f"Cập nhật số lượng cho sách {ct.sach.ID_Sach} thất bại!")

            if not self.dao.auto_update_total(phieu.ID_PhieuNhap):
                raise Exception(f"Không thể cập nhật tổng cho phiếu {phieu.ID_PhieuNhap}")

            self.log_action("CREATE", f"Đã tạo phiếu nhập {phieu.ID_PhieuNhap} với {len(phieu.Danhsachchitietnhap)} chi tiết")
            return True

        return self.execute_transaction(lambda: action())


    def get_all(self) -> List[PhieuNhapSach]:
        try:
            phieu_list = self.dao.get_all()
            for phieu in phieu_list:
                phieu.Danhsachchitietnhap = self.ct_service.get_by_phieu(phieu.ID_PhieuNhap)
            return phieu_list
        except Exception as e:
            self.handle_error(e)
            return []

    def find_by_id(self, id_phieunhap: str) -> Optional[PhieuNhapSach]:
        try:
            phieu = self.dao.find_by_key(id_phieunhap)
            if phieu:
                phieu.Danhsachchitietnhap = self.ct_service.get_by_phieu(id_phieunhap)
            return phieu
        except Exception as e:
            self.handle_error(e)
            return None

    def update(self, phieu: PhieuNhapSach) -> bool:
        try:
            # Gọi trực tiếp dao.update trong transaction, giống như SachService
            result = self.execute_transaction(self.dao.update, phieu)
            if result:
                self.log_action("UPDATE", f"Đã cập nhật phiếu nhập {phieu.ID_PhieuNhap}")
            return result
        except Exception as e:
            self.handle_error(e)
            return False

    def delete(self, id_phieunhap: str) -> bool:
        def action(id_pns: str):
            # Lấy thông tin chi tiết phiếu nhập TRƯỚC KHI XÓA
            phieu_can_xoa = self.find_by_id(id_pns)
            if not phieu_can_xoa:
                raise Exception(f"Không tìm thấy phiếu nhập {id_pns} để xóa.")

            # Hoàn tác số lượng sách trong kho (TRỪ đi số lượng đã nhập)
            for ct in phieu_can_xoa.Danhsachchitietnhap:
                sach_trong_kho = self.sach_service.find_by_id(ct.sach.ID_Sach)
                if sach_trong_kho.SoLuong < ct.SoLuong:
                    raise Exception(f"Không thể hoàn tác: Số lượng tồn kho của sách '{ct.sach.TenSach}' ({sach_trong_kho.SoLuong}) nhỏ hơn số lượng đã nhập ({ct.SoLuong}).")
                
                so_luong_moi = sach_trong_kho.SoLuong - ct.SoLuong
                if not self.sach_service.update_stock(ct.sach.ID_Sach, so_luong_moi):
                    raise Exception(f"Cập nhật (hoàn tác) số lượng cho sách {ct.sach.ID_Sach} thất bại!")

            # Xóa tất cả chi tiết phiếu nhập
            if not self.ct_service.delete_all_by_phieu(id_pns):
                # Có thể không có chi tiết nào để xóa, nên không cần raise Exception
                logging.warning(f"Không có chi tiết nào để xóa cho phiếu {id_pns} hoặc đã có lỗi.")
            # Xóa phiếu nhập
            if not self.dao.delete(id_phieunhap):
                raise Exception("Không thể xóa phiếu nhập.")
            self.log_action("DELETE", f"Đã xóa phiếu nhập {id_phieunhap} và hoàn tác số lượng kho.")
            return True

        return self.execute_transaction(action, id_phieunhap)
    
    #các hàm nâng cao

    def get_total(self, id_phieunhap: str) -> tuple[int, Decimal]:
        try:
            return self.dao.get_total(id_phieunhap)
        except Exception as e:
            self.handle_error(e)
            return (0, Decimal("0.0"))
        
    def auto_update_total(self, id_phieunhap: str) -> bool:
        def action():
            success = self.dao.auto_update_total(id_phieunhap)
            if not success:
                raise Exception(f"Cập nhật tổng thất bại cho phiếu nhập {id_phieunhap}!")
            return True

        return self.execute_transaction(action, id_phieunhap)
    
    def get_recent(self, limit: int = 10) -> List[PhieuNhapSach]:
        try:
            result = self.dao.get_recent(limit)
            if result:
                self.log_action("GET RECENT", f"Đã lấy {limit} phiếu nhập gần nhất")
            return result
        except Exception as e:
            self.handle_error(e)
            return []
    
    def search_by_date_range(self, start_date: date, end_date: date) -> List[PhieuNhapSach]:
        try:
            result = self.dao.search_by_date_range(start_date, end_date)
            if result:
                self.log_action("SEARCH BY DATE RANGE", f"Đã lấy các phiếu nhập trong khoảng {start_date} đến {end_date}")
            return result
        except Exception as e:
            self.handle_error(e)
            return []
        
    def get_by_id_nhanvien(self, id_nhanvien: str) -> List[PhieuNhapSach]:
        try:
            phieu_list = self.dao.get_by_id_nhanvien(id_nhanvien)
            for phieu in phieu_list:
                phieu.Danhsachchitietnhap = self.ct_service.get_by_phieu(phieu.ID_PhieuNhap)
            return phieu_list
        except Exception as e:
            self.handle_error(e)
            return []
        
    def get_total_import_cost(self, start_date: date, end_date: date) -> Decimal:
        try:
            result = self.dao.get_total_import_cost(start_date, end_date)
            if result:
                self.log_action("GET TOTAL IMPORT COST", f"Đã tính tổng tiền phiếu nhập trong khoảng {start_date} đến {end_date}")
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
        
    def get_monthly_import_cost(self) -> List[tuple[int, Decimal]]:
        try:
            return self.dao.get_monthly_import_cost()
        except Exception as e:
            self.handle_error(e)
            return []
        
    def get_largest_value_invoice(self) -> Optional[PhieuNhapSach]:
        try:
            result = self.dao.get_largest_import_invoice()
            if result:
                self.log_action("GET LARGEST VALUE INVOICE", "Đã lấy phiếu nhập có tổng tiền lớn nhất")
            return result
        except Exception as e:
            self.handle_error(e)
            return None
        
    def get_by_sach(self, id_sach: str) -> List[PhieuNhapSach]:
        try:
            phieu_list = self.dao.get_by_sach(id_sach)
            for phieu in phieu_list:
                phieu.Danhsachchitietnhap = self.ct_service.get_by_phieu(phieu.ID_PhieuNhap)
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
        
    def get_current_month(self) -> List[PhieuNhapSach]:
        try:
            result = self.dao.get_current_month()
            if result:
                self.log_action("GET CURRENT MONTH", "Đã lấy các phiếu nhập trong tháng này")
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
        
    def get_current_month_cost(self) -> Decimal:
        try:
            return self.dao.get_current_month_cost()
        except Exception as e:
            self.handle_error(e)
            return Decimal('0')

    def get_monthly_statistics(self, year: int) -> List[tuple[int, int, Decimal]]:
        try:
            return self.dao.get_monthly_statistics(year)
        except Exception as e:
            self.handle_error(e)
            return [] 

    def get_top_suppliers(self, limit: int = 5) -> List[dict]:
        try:
            return self.dao.get_top_supplier(limit)
        except Exception as e:
            self.handle_error(e)
            return []

    def search(self, keyword: str) -> List[PhieuNhapSach]:
        try:
            phieu_list = self.dao.search(keyword)
            for phieu in phieu_list:
                phieu.Danhsachchitietnhap = self.ct_service.get_by_phieu(phieu.ID_PhieuNhap)
            return phieu_list
        except Exception as e:
            self.handle_error(e)
            return []
