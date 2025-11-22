from decimal import Decimal
from typing import TYPE_CHECKING

from source.models.Sach import Sach
from config.basemodel import BaseModel
from util.decimal_util import validate_money

if TYPE_CHECKING:
    from source.models.PhieuXuatSach import PhieuXuatSach

class ChiTietPhieuXuat(BaseModel):
    def __init__(self, phieu_xuat: "PhieuXuatSach", sach: Sach, SoLuong: int, DonGia: float):
        self.phieu_xuat = phieu_xuat
        self.sach = sach
        self.SoLuong = SoLuong
        self.DonGia = DonGia if DonGia is not None else sach.Gia

    @property
    def phieu_xuat(self):
        return self.__phieu_xuat
    @phieu_xuat.setter
    def phieu_xuat(self, new_ctpx: "PhieuXuatSach"):
        if new_ctpx and new_ctpx.__class__.__name__ != 'PhieuXuatSach':
            raise ValueError("chi tiết phiếu xuất phải dựa trên 1 phiếu xuất tồn tại!")
        self.__phieu_xuat = new_ctpx
    
    @property
    def sach(self):
        return self.__sach
    @sach.setter
    def sach(self, new_sach: Sach):
        if not isinstance(new_sach, Sach):
            raise ValueError("Sách được truy xuất trong Phiếu xuất phải tồn tại!")
        self.__sach = new_sach

    @property
    def SoLuong(self):
        return self.__SoLuong
    @SoLuong.setter
    def SoLuong(self, new_SoLuong: int):
        if not isinstance(new_SoLuong, int) or new_SoLuong <= 0:
            raise ValueError("Số lượng phải số nguyên dương!")
        self.__SoLuong = new_SoLuong
    
    @property
    def DonGia(self):
        return self.__DonGia
    @DonGia.setter
    def DonGia(self, new_DonGia: Decimal):
        self.__DonGia = validate_money(new_DonGia, "Đơn Giá Xuất")

    @property
    def ThanhTien(self):
        return self.SoLuong * self.DonGia
    
    def to_dict(self):
        return {
            "phieu_xuat": self.phieu_xuat.ID_PhieuXuat,
            "sach": self.sach.to_dict(),
            "SoLuong": self.SoLuong,
            "DonGia": self.DonGia
        }
    @classmethod
    def from_dict(cls, data, phieu_xuat_obj: "PhieuXuatSach"):
        # Xử lý dữ liệu phẳng từ JOIN
        sach_obj = Sach.from_dict(data) if "TenSach" in data else None
        if not sach_obj and "sach" in data:
             sach_obj = Sach.from_dict(data["sach"])
        return cls(
            phieu_xuat = phieu_xuat_obj,
            sach = sach_obj,
            SoLuong = data["SoLuongXuat"], # Sửa để đọc đúng cột
            DonGia = data["DonGia"]
        )