import re
from decimal import Decimal

from config.validator import is_valid_year
from config.validator import is_non_empty_string
from config.basemodel import BaseModel
from config.validator import to_decimal
from util.decimal_util import validate_money
from util.get_absolute_path import get_absolute_path

class Sach(BaseModel):
    DEFAULT_IMAGE_PATH = get_absolute_path("source/ui/picture/book_pic/default_book.jpg")
    def __init__(self, ID_Sach: str, TenSach: str, TacGia: str, TheLoai: str, NamXuatBan: str, NhaXuatBan: str, NgonNgu: str, SoLuong: int, TrangThai: str, Gia: Decimal, TinhKhaDung: str, HinhAnh: str = DEFAULT_IMAGE_PATH):
        self.ID_Sach = ID_Sach
        self.TenSach = TenSach
        self.TacGia = TacGia
        self.TheLoai = TheLoai
        self.NamXuatBan = NamXuatBan
        self.NhaXuatBan = NhaXuatBan
        self.NgonNgu = NgonNgu
        self.SoLuong = SoLuong
        self.TrangThai = TrangThai 
        self.Gia = Gia
        self.TinhKhaDung = TinhKhaDung
        self.HinhAnh = HinhAnh if HinhAnh else self.DEFAULT_IMAGE_PATH

    @property
    def ID_Sach(self):
        return self.__ID_Sach
    
    @ID_Sach.setter
    def ID_Sach(self, new_ID_Sach: str):
        if not is_non_empty_string(new_ID_Sach):
            raise ValueError("Mã sách không được để trống")
        if not re.fullmatch(r"S\d+", new_ID_Sach.strip()):
            raise ValueError("Mã sách phải bắt đầu từ chữ 'S' và theo sau là các chữ số!")
        self.__ID_Sach = new_ID_Sach.strip()

    @property
    def TenSach(self):
        return self.__TenSach
    
    @TenSach.setter
    def TenSach(self, new_TenSach: str):
        if not is_non_empty_string(new_TenSach):
            raise ValueError("Tên sách không được để trống")
        self.__TenSach = new_TenSach.strip()

    @property
    def TacGia(self):
        return self.__TacGia
    
    @TacGia.setter
    def TacGia(self, new_TacGia: str):
        if not is_non_empty_string(new_TacGia):
            raise ValueError("Tác giả không được để trống")
        self.__TacGia = new_TacGia.strip()

    @property
    def TheLoai(self):
        return self.__TheLoai
    
    @TheLoai.setter
    def TheLoai(self, new_TheLoai: str):
        if not is_non_empty_string(new_TheLoai):
            raise ValueError("Thể loại không được để trống")
        self.__TheLoai = new_TheLoai.strip()

    @property
    def NamXuatBan(self):
        return self.__NamXuatBan
    
    @NamXuatBan.setter
    def NamXuatBan(self, new_NamXuatBan: str):
        clean_year = str(new_NamXuatBan).strip()
        if not clean_year:
            raise ValueError("Năm xuất bản không được để trống")
        if not re.fullmatch(r"\d{4}", clean_year):
            raise ValueError("Năm xuất bản phải gồm 4 chữ số!")
        if not is_valid_year(int(clean_year)):
            raise ValueError("Năm xuất bản không hợp lê!")
        self.__NamXuatBan = clean_year
    
    @property
    def NhaXuatBan(self):
        return self.__NhaXuatBan
    
    @NhaXuatBan.setter
    def NhaXuatBan(self, new_NhaXuatBan: str):
        if not is_non_empty_string(new_NhaXuatBan):
            raise ValueError("Nhà xuất bản không được để trống")
        self.__NhaXuatBan = new_NhaXuatBan.strip()

    @property
    def NgonNgu(self):
        return self.__NgonNgu
    @NgonNgu.setter
    def NgonNgu(self, new_NgonNgu: str):
        if not is_non_empty_string(new_NgonNgu):
            raise ValueError("Ngôn ngữ không được để trống")
        self.__NgonNgu = new_NgonNgu.strip()
    
    @property
    def SoLuong(self):
        return self.__SoLuong
    @SoLuong.setter
    def SoLuong(self, new_SoLuong: int):
        if not isinstance(new_SoLuong, int):
            raise ValueError("Số lượng phải là một số nguyên!")
        if new_SoLuong < 0:
            raise ValueError("Số lượng phải là một số nguyên không âm!")
        self.__SoLuong = new_SoLuong

    @property
    def TrangThai(self):
        return self.__TrangThai
    @TrangThai.setter
    def TrangThai(self, new_TrangThai: str):
        if not is_non_empty_string(new_TrangThai):
            raise ValueError("Trạng thái không được để trống!")
        if new_TrangThai not in ("Còn hàng", "Hết hàng"):
            raise ValueError("Trạng thái phải là 'Còn hàng' hoặc 'Hết hàng'!")
        self.__TrangThai = new_TrangThai

    @property
    def Gia(self):
        return self.__Gia
    @Gia.setter
    def Gia(self, new_Gia: Decimal):
        self.__Gia = validate_money(new_Gia, "Giá")

    @property
    def TinhKhaDung(self):
        return self.__TinhKhaDung
    @TinhKhaDung.setter
    def TinhKhaDung(self, new_TinhKhaDung: str):
        if not is_non_empty_string(new_TinhKhaDung):
            raise ValueError("Tính khả dụng không được để trống!")
        if new_TinhKhaDung not in ("Khả dụng", "Không khả dụng"):
            raise ValueError("Tính khả dụng phải là 'Khả dụng' hoặc 'Không khả dụng'!")
        self.__TinhKhaDung = new_TinhKhaDung


    @property
    def HinhAnh(self):
        return self.__HinhAnh

    @HinhAnh.setter
    def HinhAnh(self, new_HinhAnh: str):
        """Nếu ảnh bị thiếu hoặc không hợp lệ → gán ảnh mặc định."""
        if not new_HinhAnh or str(new_HinhAnh).strip() == "":
            self.__HinhAnh = self.DEFAULT_IMAGE_PATH
            return

        if not isinstance(new_HinhAnh, str):
            raise ValueError("Hình ảnh phải là đường dẫn dạng chuỗi!")

        if not re.search(r"\.(jpg|jpeg|png|gif|bmp|webp)$", new_HinhAnh.lower()):
            self.__HinhAnh = self.DEFAULT_IMAGE_PATH
            return

        self.__HinhAnh = new_HinhAnh.strip()

    def to_dict(self):
        return {
            "ID_Sach": self.ID_Sach,
            "TenSach": self.TenSach,
            "TacGia": self.TacGia,
            "TheLoai": self.TheLoai,
            "NamXuatBan": self.NamXuatBan,
            "NhaXuatBan": self.NhaXuatBan,
            "NgonNgu": self.NgonNgu,
            "SoLuong": self.SoLuong,
            "TrangThai": self.TrangThai,
            "Gia": self.Gia,
            "TinhKhaDung": self.TinhKhaDung,
            "HinhAnh": self.HinhAnh,
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            ID_Sach = data["ID_Sach"],
            TenSach = data["TenSach"],
            TacGia = data["TacGia"],
            TheLoai = data["TheLoai"],
            NamXuatBan = data["NamXuatBan"],
            NhaXuatBan = data["NhaXuatBan"],
            NgonNgu = data["NgonNgu"],
            SoLuong = data["SoLuong"],
            TrangThai = data["TrangThai"],
            Gia = data["Gia"],
            TinhKhaDung = data["TinhKhaDung"],
            HinhAnh = data.get("HinhAnh")
        )
    