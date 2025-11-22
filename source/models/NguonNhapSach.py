import re

from config.validator import is_non_empty_string
from config.validator import is_a_phonenumber
from config.validator import is_valid_email
from config.basemodel import BaseModel
from util.get_absolute_path import get_absolute_path

class NguonNhapSach(BaseModel):
    DEFAULT_IMAGE_PATH = get_absolute_path("source/ui/picture/supplier_pic/supplier_default_pic.jpg")
    def __init__(self, ID_NguonNhap: str, TenCoSo: str, HinhThucNhap: str, DiaChi:str, SoDienThoai: str, Email: str, TrangThaiNCC: str, TinhKhaDung: str, HinhAnh: str = DEFAULT_IMAGE_PATH):
        self.ID_NguonNhap = ID_NguonNhap
        self.TenCoSo = TenCoSo
        self.HinhThucNhap = HinhThucNhap
        self.DiaChi = DiaChi
        self.SoDienThoai = SoDienThoai
        self.Email = Email
        self.TrangThaiNCC = TrangThaiNCC
        self.TinhKhaDung = TinhKhaDung
        self.HinhAnh = HinhAnh if HinhAnh else self.DEFAULT_IMAGE_PATH
    
    @property
    def ID_NguonNhap(self):
        return self.__ID_NguonNhap
    @ID_NguonNhap.setter
    def ID_NguonNhap(self, new_ID_NguonNhap: str):
        if not is_non_empty_string(new_ID_NguonNhap):
            raise ValueError("Mã nhà cung cấp không được để trống!")
        if not re.fullmatch(r"NN\d+", new_ID_NguonNhap.strip()):
            raise ValueError("Mã nhà cung cấp phải có dạng 'NN' và theo sau là 1 số!")
        self.__ID_NguonNhap = new_ID_NguonNhap.strip()
    
    @property
    def TenCoSo(self):
        return self.__TenCoSo
    @TenCoSo.setter
    def TenCoSo(self, new_TenCoSo: str):
        if not is_non_empty_string(new_TenCoSo):
            raise ValueError("Tên nhà cung cấp không được để trống!")
        self.__TenCoSo = new_TenCoSo.strip()
    
    @property
    def HinhThucNhap(self):
        return self.__HinhThucNhap
    @HinhThucNhap.setter
    def HinhThucNhap(self, new_HinhThucNhap: str):
        if not is_non_empty_string(new_HinhThucNhap):
            raise ValueError("Hình thức nhập không được để trống!")
        self.__HinhThucNhap = new_HinhThucNhap.strip()

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
            raise ValueError("Số điện thoại không hợp lệ!")
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
    def TrangThaiNCC(self):
        return self.__TrangThai
    @TrangThaiNCC.setter
    def TrangThaiNCC(self, new_TrangThai: str):
        if not is_non_empty_string(new_TrangThai):
            raise ValueError("Trạng thái không được để trống")
        if new_TrangThai not in ("Hoạt Động", "Ngừng Hoạt Động"):
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
            "ID_NguonNhap": self.ID_NguonNhap,
            "TenCoSo": self.TenCoSo,
            "HinhThucNhap": self.HinhThucNhap,
            "DiaChi": self.DiaChi,
            "SoDienThoai": self.SoDienThoai,
            "Email": self.Email,
            "TrangThaiNCC": self.TrangThaiNCC,
            "TinhKhaDung": self.TinhKhaDung,
            "HinhAnh": self.HinhAnh,
        }
     
    @classmethod
    def from_dict(cls, data):
        return cls(
            ID_NguonNhap = data["ID_NguonNhap"],
            TenCoSo = data["TenCoSo"],
            HinhThucNhap = data["HinhThucNhap"],
            DiaChi = data["DiaChi"],
            SoDienThoai = data["SoDienThoai"],
            Email = data["Email"],
            TrangThaiNCC = data["TrangThaiNCC"],
            TinhKhaDung = data["TinhKhaDung"],
            HinhAnh = data.get("HinhAnh")
        )