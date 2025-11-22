from decimal import Decimal
from typing import TYPE_CHECKING

from source.models.Sach import Sach
from config.basemodel import BaseModel
from util.decimal_util import validate_money

if TYPE_CHECKING:
    from source.models.PhieuNhapSach import PhieuNhapSach

class ChiTietPhieuNhap(BaseModel):
    def __init__(self, phieu_nhap: "PhieuNhapSach", sach: Sach, SoLuong: int, DonGia: Decimal):
        self.phieu_nhap = phieu_nhap
        self.sach = sach
        self.SoLuong = SoLuong
        self.DonGia = DonGia if DonGia is not None else sach.Gia

    @property
    def phieu_nhap(self):
        return self.__phieu_nhap
    @phieu_nhap.setter
    def phieu_nhap(self, new_ctpn: "PhieuNhapSach"):
        if new_ctpn and new_ctpn.__class__.__name__ != 'PhieuNhapSach': # An toàn hơn khi dùng forward ref
            raise ValueError("Đối tượng có chi tiết phiếu nhập phải là 1 phiếu nhập cụ thể!")
        self.__phieu_nhap = new_ctpn
    
    @property
    def sach(self):
        return self.__sach
    @sach.setter
    def sach(self, new_sach: Sach):
        if not isinstance(new_sach, Sach):
            raise ValueError("Đối tượng được gọi đến phải là 1 sách có tồn tại!")
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
        self.__DonGia = validate_money(new_DonGia, "Đơn Giá Nhập")

    @property
    def ThanhTien(self):
        return self.SoLuong * self.DonGia
    
    def to_dict(self):
        return {
            "phieu_nhap": self.phieu_nhap.ID_PhieuNhap,
            "sach": self.sach.to_dict(),
            "SoLuong": self.SoLuong,
            "DonGia": self.DonGia,
            "ThanhTien": self.ThanhTien
        }
    
    @classmethod
    def from_dict(cls, data, phieu_nhap_obj: "PhieuNhapSach"):
        sach_obj = Sach.from_dict(data) if "TenSach" in data else None # Giả định nếu có TenSach thì là dict của sách
        if not sach_obj:
             sach_obj = Sach.from_dict(data["sach"])
        return cls(
            phieu_nhap = phieu_nhap_obj,
            sach = sach_obj,
            SoLuong = data["SoLuongNhap"], # Sửa để đọc đúng cột
            DonGia = data["DonGia"]
        )
