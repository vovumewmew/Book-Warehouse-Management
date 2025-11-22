import re

from config.validator import is_non_empty_string
from config.validator import is_a_phonenumber
from config.validator import is_valid_email
from config.basemodel import BaseModel
from util.get_absolute_path import get_absolute_path

class NhaPhanPhoi(BaseModel):
    DEFAULT_IMAGE_PATH = get_absolute_path("source/ui/picture/contributors_pic/contributor_default_pic.jpg")
    def __init__(self, ID_NguonXuat: str, TenCoSo: str, DiaChi: str, SoDienThoai: str, Email: str, TrangThaiNPP: str, TinhKhaDung: str, HinhAnh: str = DEFAULT_IMAGE_PATH):
        self.ID_NguonXuat = ID_NguonXuat
        self.TenCoSo = TenCoSo
        self.DiaChi = DiaChi
        self.SoDienThoai = SoDienThoai
        self.Email = Email
        self.TrangThaiNPP = TrangThaiNPP
        self.TinhKhaDung = TinhKhaDung
        self.HinhAnh = HinhAnh if HinhAnh else self.DEFAULT_IMAGE_PATH

    @property
    def ID_NguonXuat(self):
        return self.__ID_NguonXuat
    @ID_NguonXuat.setter
    def ID_NguonXuat(self, new_ID_NguonXuat: str):
        if not is_non_empty_string(new_ID_NguonXuat):
            raise ValueError("Mã nhà phân phối không được để trống!")
        if not re.fullmatch(r"NX\d+", new_ID_NguonXuat.strip()):
            raise ValueError("Mã nhà phân phối phải có dạng 'NX' theo sau là số!")
        self.__ID_NguonXuat = new_ID_NguonXuat.strip()
    
    @property 
    def TenCoSo(self):
        return self.__TenCoSo
    @TenCoSo.setter
    def TenCoSo(self, new_TenCoSo: str):
        if not is_non_empty_string(new_TenCoSo):
            raise ValueError("Tên cơ sở không được để trống!")
        self.__TenCoSo = new_TenCoSo.strip()

    @property
    def DiaChi(self):
        return self.__DiaChi
    @DiaChi.setter
    def DiaChi(self, new_DiaChi: str):
        if not is_non_empty_string(new_DiaChi):
            raise ValueError("Địa chỉ không được để trống!")
        self.__DiaChi = new_DiaChi.strip()

    @property
    def SoDienThoai(self):
        return self.__SoDienThoai
    @SoDienThoai.setter
    def SoDienThoai(self, new_SoDienThoai: str):
        if not is_non_empty_string(new_SoDienThoai):
            raise ValueError("Số điện thoại không được để trống!")
        if not is_a_phonenumber(new_SoDienThoai):
            raise ValueError("Số điện thoại phải là chuỗi gồm 10 hoặc 11 chữ số!")
        self.__SoDienThoai = new_SoDienThoai.strip()

    @property
    def Email(self):
        return self.__Email
    @Email.setter
    def Email(self, new_Email: str):
        if not is_non_empty_string(new_Email):
            raise ValueError("Email không được để trống!")
        if not is_valid_email(new_Email):
            raise ValueError("Email không hợp lệ!")
        self.__Email = new_Email.strip()

    @property
    def TrangThaiNPP(self):
        return self.__TrangThai
    @TrangThaiNPP.setter
    def TrangThaiNPP(self, new_TrangThai: str):
        if not is_non_empty_string(new_TrangThai):
            raise ValueError("Trạng thái không được để trống!")
        if new_TrangThai not in("Hoạt Động", "Ngừng Hoạt Động"):
            raise ValueError("Trạng thái phải là 'Hoạt Động' hoặc 'Ngừng Hoạt Động'!")
        self.__TrangThai = new_TrangThai.strip()

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
            "ID_NguonXuat": self.ID_NguonXuat,
            "TenCoSo": self.TenCoSo,
            "DiaChi": self.DiaChi,
            "SoDienThoai": self.SoDienThoai,
            "Email": self.Email,
            "TrangThaiNPP": self.TrangThaiNPP,
            "TinhKhaDung": self.TinhKhaDung,
            "HinhAnh": self.HinhAnh,
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            ID_NguonXuat = data["ID_NguonXuat"],
            TenCoSo = data["TenCoSo"],
            DiaChi = data["DiaChi"],
            SoDienThoai = data["SoDienThoai"],
            Email = data["Email"],
            TrangThaiNPP = data["TrangThaiNPP"],
            TinhKhaDung = data["TinhKhaDung"],
            HinhAnh = data.get("HinhAnh")
        )