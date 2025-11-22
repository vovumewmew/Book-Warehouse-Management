import re
import datetime
from decimal import Decimal
from typing import List, TYPE_CHECKING

from config.validator import is_non_empty_string
from config.validator import is_valid_date
from config.basemodel import BaseModel

from source.models.NhanVien import NhanVien
from source.models.NguonNhapSach import NguonNhapSach

from util.decimal_util import validate_money

if TYPE_CHECKING:
    from source.models.ChiTietPhieuNhap import ChiTietPhieuNhap

class PhieuNhapSach(BaseModel):
    def __init__(self, ID_PhieuNhap: str, NgayNhap: str, TongSoLuong: int, TongTien: float, nhan_vien_nhap: NhanVien, nguon_nhap: NguonNhapSach):
        self.ID_PhieuNhap = ID_PhieuNhap
        self.NgayNhap = NgayNhap
        self.TongSoLuong = TongSoLuong
        self.TongTien = TongTien
        self.nhan_vien_nhap = nhan_vien_nhap
        self.nguon_nhap = nguon_nhap
        self.Danhsachchitietnhap: List = []

        # Thuộc tính thêm để hiển thị, không có trong DB
        self.TenNhanVien: str = ""
        self.TenNguonNhap: str = ""
    
    @property
    def ID_PhieuNhap(self):
        return self.__ID_PhieuNhap
    @ID_PhieuNhap.setter
    def ID_PhieuNhap(self, new_ID_PhieuNhap: str):
        if not re.fullmatch(r"PN\d+", new_ID_PhieuNhap.strip()):
            raise ValueError("Mã phiếu nhập phải là 'PN' và theo sau là số!")
        if not is_non_empty_string(new_ID_PhieuNhap):
            raise ValueError("Mã phiếu nhập không được để trống!")
        self.__ID_PhieuNhap = new_ID_PhieuNhap.strip()
    
    @property
    def NgayNhap(self) -> datetime.date:
        return self.__NgayNhap

    @NgayNhap.setter
    def NgayNhap(self, new_date):
        if isinstance(new_date, str):
            if not is_valid_date(new_date):
                raise ValueError("Ngày nhập không hợp lệ, định dạng phải dd/mm/yyyy")
            new_date = datetime.datetime.strptime(new_date.strip(), "%d/%m/%Y").date()

        if not isinstance(new_date, datetime.date):
            raise ValueError("Ngày nhập phải là kiểu date")
        self.__NgayNhap = new_date

    @property
    def TongSoLuong(self):
        return self.__TongSoLuong
    @TongSoLuong.setter
    def TongSoLuong(self, new_TongSoLuong: int): #chưa xong
        if not isinstance(new_TongSoLuong, int) or new_TongSoLuong < 0:
            raise ValueError("Tổng số lượng phải là số nguyên và không âm!")
        self.__TongSoLuong = new_TongSoLuong

    @property
    def TongTien(self):
        return self.__TongTien
    @TongTien.setter
    def TongTien(self, new_TongTien: Decimal):
        self.__TongTien = validate_money(new_TongTien, "Tổng Tiền Nhập")

    @property
    def nhan_vien_nhap(self):
        return self.__nhan_vien_nhap
    @nhan_vien_nhap.setter
    def nhan_vien_nhap(self, new_nhan_vien_nhap: NhanVien):
        if not isinstance(new_nhan_vien_nhap, NhanVien):
            raise ValueError("người nhập đơn hàng phải là 1 nhân viên!")
        self.__nhan_vien_nhap = new_nhan_vien_nhap

    @property
    def nguon_nhap(self):
        return self.__nguon_nhap
    @nguon_nhap.setter
    def nguon_nhap(self, new_nguon_nhap: NguonNhapSach):
        if not isinstance(new_nguon_nhap, NguonNhapSach):
            raise ValueError("Đối tượng nhập sách phải là nguồn nhập sách!")
        self.__nguon_nhap = new_nguon_nhap

    def add_chitiet_nhap(self, chitiet):
        self.Danhsachchitietnhap.append(chitiet)
        self.cap_nhat_tong_nhap()

    def load_chitiet_nhap(self, list_chitiet: List["ChiTietPhieuNhap"]):
        self.Danhsachchitietnhap = list_chitiet
        self.cap_nhat_tong_nhap()

    def cap_nhat_tong_nhap(self):
        self.TongSoLuong = sum(ct.SoLuong for ct in self.Danhsachchitietnhap)
        self.TongTien = sum(ct.ThanhTien for ct in self.Danhsachchitietnhap if hasattr(ct, 'ThanhTien'))

    def to_dict(self):
        return {
            "ID_PhieuNhap": self.ID_PhieuNhap,
            "NgayNhap": self.NgayNhap.strftime("%d/%m/%Y"),
            "TongSoLuong": self.TongSoLuong,
            "TongTien": self.TongTien,
            "nhan_vien_nhap": self.nhan_vien_nhap.to_dict() if self.nhan_vien_nhap else None,
            "nguon_nhap": self.nguon_nhap.to_dict() if self.nguon_nhap else None,
            "Danhsachchitietnhap": [ct.to_dict() for ct in self.Danhsachchitietnhap]
        }
    
    @classmethod
    def from_dict(cls, data):
        # Tạo đối tượng NhanVien và NguonNhapSach từ các ID có trong data
        nhan_vien_obj = NhanVien(
            ID_NhanVien=data.get("ID_NhanVien"),
            HoTen=data.get("TenNhanVien", ""), # Lấy tên từ JOIN
            GioiTinh="Nam", ChucVu="Nhân viên nhập sách", SoDienThoai="0123456789", Email="placeholder@email.com", TrangThaiNhanVien="Đang làm việc" # Các trường không cần thiết
        )
        nguon_nhap_obj = NguonNhapSach(
            ID_NguonNhap=data.get("ID_NguonNhap"),
            TenCoSo=data.get("TenNguonNhap", ""),
            HinhThucNhap="Online", DiaChi="Không có", SoDienThoai="0123456789", Email="placeholder@email.com", TrangThaiNCC="Hoạt Động", TinhKhaDung="Khả dụng" # Các trường không cần thiết
        )
        obj = cls(
            ID_PhieuNhap = data["ID_PhieuNhap"],
            NgayNhap = data["NgayNhap"],
            TongSoLuong = data.get("TongSoLuong", 0),
            TongTien = data.get("TongTien", 0.0),
            nhan_vien_nhap = nhan_vien_obj,
            nguon_nhap = nguon_nhap_obj,
        )
        # Gán các trường được JOIN thêm
        if "TenNhanVien" in data:
            obj.TenNhanVien = data["TenNhanVien"]
        if "TenNguonNhap" in data:
            obj.TenNguonNhap = data["TenNguonNhap"]

        obj.Danhsachchitietnhap = []
        return obj