import re

from config.validator import is_non_empty_string
from config.validator import is_a_phonenumber
from config.validator import is_valid_email
from config.basemodel import BaseModel
from util.get_absolute_path import get_absolute_path

class NhanVien(BaseModel):
    DEFAULT_IMAGE_PATH = get_absolute_path("source/ui/picture/employee_pic/default_employee_pic.jpg")
    def __init__(self, ID_NhanVien: str,HoTen: str, GioiTinh: str, ChucVu: str, TrangThaiNhanVien: str, SoDienThoai: str, Email: str, HinhAnh: str = DEFAULT_IMAGE_PATH):
        self.ID_NhanVien = ID_NhanVien
        self.HoTen = HoTen
        self.GioiTinh = GioiTinh
        self.ChucVu = ChucVu  
        self.SoDienThoai = SoDienThoai 
        self.Email = Email
        self.TrangThaiNhanVien = TrangThaiNhanVien
        self.HinhAnh = HinhAnh if HinhAnh else self.DEFAULT_IMAGE_PATH
    @property 
    def ID_NhanVien(self):
        return self.__ID_NhanVien
    @ID_NhanVien.setter
    def ID_NhanVien(self, new_ID_NhanVien: str):
        if not is_non_empty_string(new_ID_NhanVien):
            raise ValueError("Mã nhân viên không được để trống!")
        if not re.fullmatch(r"NV\d+", new_ID_NhanVien.strip()):
            raise ValueError("Mã nhân viên phải bắt đầu từ 'NV' và theo sau là các chữ số!")
        self.__ID_NhanVien = new_ID_NhanVien.strip()

    @property
    def HoTen(self):
        return self.__HoTen
    @HoTen.setter
    def HoTen(self, new_name: str):
        if not is_non_empty_string(new_name):
            raise ValueError("Tên nhân viên không được để trống!")
        new_name = new_name.strip()
        if not re.fullmatch(r"[A-Za-zÀ-ỹ\s]+", new_name):
            raise ValueError("Tên nhân viên chỉ được chứa chữ cái và khoảng trắng!")
        if len(new_name) > 50:
            raise ValueError("Tên nhân viên quá dài, tối đa 50 ký tự!")
        self.__HoTen = new_name.strip()

    @property
    def GioiTinh(self):
        return self.__GioiTinh
    @GioiTinh.setter
    def GioiTinh(self, new_GioiTinh: str):
        if not is_non_empty_string(new_GioiTinh):
            raise ValueError("Giới tính không được để trống!")
        if new_GioiTinh not in ("Nam", "Nữ"):
            raise ValueError("Giới tính phải là 'Nam' hoặc 'Nữ'!")
        self.__GioiTinh = new_GioiTinh.strip()

    @property
    def ChucVu(self):
        return self.__ChucVu
    @ChucVu.setter
    def ChucVu(self, new_ChucVu: str):
        if not is_non_empty_string(new_ChucVu):
            raise ValueError("Chức vụ không được để trống!")
        if new_ChucVu not in ("Quản lý kho sách", "Nhân viên nhập sách", "Nhân viên xuất sách", "Nhân viên kiểm kê kho"):
            raise ValueError("Chức vụ không hợp lệ")
        self.__ChucVu = new_ChucVu.strip()

    @property
    def SoDienThoai(self):
        return self.__SoDienThoai
    @SoDienThoai.setter
    def SoDienThoai(self, new_SoDienThoai: str):
        if not is_non_empty_string(new_SoDienThoai):
            raise ValueError("Số điện thoại không được để trống!")
        if not is_a_phonenumber(new_SoDienThoai):
            raise ValueError("Số điện thoại phải là chuỗi số gồm 10 hoặc 11 chữ số!")
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
    def TrangThaiNhanVien(self):
        return self.__TrangThaiNhanVien
    @TrangThaiNhanVien.setter
    def TrangThaiNhanVien(self, new_TrangThaiNhanVien: str):
        if not is_non_empty_string(new_TrangThaiNhanVien):
            raise ValueError("Trạng thái nhân viên không được để trống!")
        if new_TrangThaiNhanVien not in ("Đang làm việc","Đã nghỉ việc"):
            raise ValueError("Trạng thái nhân viên phải là 'Đang làm việc' hoặc 'Đã nghỉ việc'")
        self.__TrangThaiNhanVien = new_TrangThaiNhanVien.strip()

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
            "ID_NhanVien": self.ID_NhanVien,
            "HoTen": self.HoTen,
            "GioiTinh": self.GioiTinh,
            "ChucVu": self.ChucVu,
            "SoDienThoai": self.SoDienThoai,
            "Email": self.Email,
            "TrangThaiNhanVien": self.TrangThaiNhanVien,
            "HinhAnh": self.HinhAnh,
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            ID_NhanVien = data["ID_NhanVien"],
            HoTen = data["HoTen"],
            GioiTinh = data["GioiTinh"],
            ChucVu = data["ChucVu"],
            SoDienThoai = data["SoDienThoai"],
            Email = data["Email"],
            TrangThaiNhanVien = data["TrangThaiNhanVien"],
            HinhAnh = data.get("HinhAnh")
        )