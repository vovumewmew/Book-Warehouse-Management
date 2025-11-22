import re
import datetime
from decimal import Decimal
from typing import List, TYPE_CHECKING

from config.validator import is_non_empty_string
from config.validator import is_valid_date
from config.basemodel import BaseModel

from source.models.NhanVien import NhanVien
from source.models.NhaPhanPhoi import NhaPhanPhoi
from source.models.NhanVien import NhanVien

from util.decimal_util import validate_money

if TYPE_CHECKING:
    from source.models.ChiTietPhieuXuat import ChiTietPhieuXuat

class PhieuXuatSach(BaseModel):
    def __init__(self, ID_PhieuXuat: str, NgayXuat: str, TongSoLuong: int, TongTien: Decimal, nhan_vien_xuat: NhanVien, nha_phan_phoi: NhaPhanPhoi):
        self.ID_PhieuXuat = ID_PhieuXuat
        self.NgayXuat = NgayXuat
        self.TongSoLuong = TongSoLuong
        self.TongTien = TongTien
        self.nhan_vien_xuat = nhan_vien_xuat
        self.nha_phan_phoi = nha_phan_phoi
        self.Danhsachchitietxuat: List = []

        # Thuộc tính thêm để hiển thị, không có trong DB
        self.TenNhanVien: str = ""
        self.TenNhaPhanPhoi: str = ""
    
    @property
    def ID_PhieuXuat(self):
        return self.__ID_PhieuXuat
    @ID_PhieuXuat.setter
    def ID_PhieuXuat(self, new_ID_PhieuXuat: str):
        if not is_non_empty_string(new_ID_PhieuXuat):
            raise ValueError("ID_NguonNhap không được để trống!")
        if not re.fullmatch(r"PX\d+", new_ID_PhieuXuat.strip()):
            raise ValueError("Mã phiếu nhập phải là 'PX' và theo sau là số!")
        self.__ID_PhieuXuat = new_ID_PhieuXuat.strip()
    
    @property
    def NgayXuat(self) -> datetime.date:
        return self.__NgayXuat

    @NgayXuat.setter
    def NgayXuat(self, new_date):
        if isinstance(new_date, str):
            if not is_valid_date(new_date):
                raise ValueError("Ngày nhập không hợp lệ, định dạng phải dd/mm/yyyy")
            new_date = datetime.datetime.strptime(new_date.strip(), "%d/%m/%Y").date()

        if not isinstance(new_date, datetime.date):
            raise ValueError("Ngày nhập phải là kiểu date")
        self.__NgayXuat = new_date

    @property
    def TongSoLuong(self):
        return self.__TongSoLuong
    @TongSoLuong.setter
    def TongSoLuong(self, new_TongSoLuong: int): 
        if not isinstance(new_TongSoLuong,int) or new_TongSoLuong < 0:
            raise ValueError("Tổng số lượng phải là số nguyên và không âm!")
        self.__TongSoLuong = new_TongSoLuong

    @property
    def TongTien(self):
        return self.__TongTien
    @TongTien.setter
    def TongTien(self, new_TongTien: Decimal): 
        self.__TongTien = validate_money(new_TongTien, "Tổng Tiền Xuất")
        
    @property
    def nhan_vien_xuat(self):
        return self.__nhan_vien_xuat
    @nhan_vien_xuat.setter
    def nhan_vien_xuat(self, new_nhan_vien_xuat: NhanVien):
        if not isinstance(new_nhan_vien_xuat, NhanVien):
            raise ValueError("đối tượng tạo phiếu xuất sách phải là 1 nhân viên!")
        self.__nhan_vien_xuat = new_nhan_vien_xuat
    
    @property
    def nha_phan_phoi(self):
        return self.__nha_phan_phoi
    @nha_phan_phoi.setter
    def nha_phan_phoi(self, new_nha_phan_phoi: NhaPhanPhoi):
        if not isinstance(new_nha_phan_phoi, NhaPhanPhoi):
            raise ValueError("đối tượng nhận hàng phải là 1 nhà phân phối!")
        self.__nha_phan_phoi = new_nha_phan_phoi

    def add_chitiet_xuat(self, chitiet):
        self.Danhsachchitietxuat.append(chitiet)
        self.cap_nhat_tong_xuat()

    def load_chitiet_xuat(self, list_chitiet: List["ChiTietPhieuXuat"]):
        self.Danhsachchitietxuat = list_chitiet
        self.cap_nhat_tong_xuat()
    
    def cap_nhat_tong_xuat(self):
        self.TongSoLuong = sum(ct.SoLuong for ct in self.Danhsachchitietxuat)
        self.TongTien = sum(ct.ThanhTien for ct in self.Danhsachchitietxuat)

    def to_dict(self):
        return {
            "ID_PhieuXuat": self.ID_PhieuXuat,
            "NgayXuat": self.NgayXuat.strftime("%d/%m/%Y"),
            "TongSoLuong": self.TongSoLuong,
            "TongTien": self.TongTien,
            "nhan_vien_xuat": self.nhan_vien_xuat.to_dict() if self.nhan_vien_xuat else None,
            "nha_phan_phoi": self.nha_phan_phoi.to_dict() if self.nha_phan_phoi else None,
            "Danhsachchitietxuat": [ct.to_dict() for ct in  self.Danhsachchitietxuat]
        }
    
    @classmethod
    def from_dict(cls, data):
        # Tạo đối tượng NhanVien và NhaPhanPhoi từ các ID và tên có trong data
        nhan_vien_obj = NhanVien(
            ID_NhanVien=data.get("ID_NhanVien"),
            HoTen=data.get("TenNhanVien", ""), # Lấy tên từ JOIN
            GioiTinh="Nam", ChucVu="Nhân viên xuất sách", SoDienThoai="0123456789", Email="placeholder@email.com", TrangThaiNhanVien="Đang làm việc" # Các trường không cần thiết
        )
        nha_phan_phoi_obj = NhaPhanPhoi(
            ID_NguonXuat=data.get("ID_NguonXuat"),
            TenCoSo=data.get("TenNhaPhanPhoi", ""), # Lấy tên từ JOIN
            DiaChi="Không có", SoDienThoai="0123456789", Email="placeholder@email.com", TrangThaiNPP="Hoạt Động", TinhKhaDung="Khả dụng" # Các trường không cần thiết
        )
        obj = cls(
            ID_PhieuXuat = data["ID_PhieuXuat"],
            NgayXuat = data["NgayXuat"],
            TongSoLuong = data.get("TongSoLuong", 0),
            TongTien = data.get("TongTien", 0.0),
            nhan_vien_xuat = nhan_vien_obj,
            nha_phan_phoi = nha_phan_phoi_obj
        )
        # Gán các trường được JOIN thêm
        if "TenNhanVien" in data:
            obj.TenNhanVien = data["TenNhanVien"]
        if "TenNhaPhanPhoi" in data:
            obj.TenNhaPhanPhoi = data["TenNhaPhanPhoi"]

        obj.Danhsachchitietxuat = []
        return obj