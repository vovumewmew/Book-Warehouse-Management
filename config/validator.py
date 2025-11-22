from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import re

def is_valid_year(year: int) -> bool:
    """ hàm kiểm tra năm hợp lệ"""

    curent_year = datetime.now().year
    return isinstance(year, int) and (1900 <= year <= curent_year)

def is_non_empty_string(value: str) -> bool:
    """ hàm kiểm tra chuỗi không rỗng"""
    return isinstance(value, str) and bool(value.strip())

def is_a_phonenumber(value: str) -> bool:
    """ hàm kiểm tra chuỗi có phải là số điện thoại không"""
    return bool(re.fullmatch(r"(?:\d{10}|\d{11})", value.strip()))

def is_valid_email(email: str) -> bool:
    """ hàm kiểm tra email hợp lệ"""
    return bool(re.fullmatch(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email.strip()))

def is_valid_date(date_str: str) -> bool:
    """Hàm kiểm tra chuỗi ngày tháng có hợp lệ theo định dạng dd/mm/YYYY hay không"""
    if not isinstance(date_str, str):
        return False
    try:
        datetime.strptime(date_str.strip(), "%d/%m/%Y")
        return True
    except ValueError:
        return False
    
def to_decimal(value, places: str = "0.01") -> Decimal:
    """
    Chuyển đổi giá trị sang Decimal với độ chính xác cố định.
    - value: giá trị đầu vào (str, float, int, Decimal)
    - places: số chữ số thập phân, mặc định là 2 (0.01)
    """
    if value is None:
        raise ValueError("Giá trị tiền tệ không được để trống")

    try:
        dec_value = Decimal(str(value)).quantize(Decimal(places), rounding=ROUND_HALF_UP)
        if dec_value < 0:
            raise ValueError("Giá trị tiền tệ không được âm")
        return dec_value
    except Exception as e:
        raise ValueError(f"Không thể chuyển '{value}' sang Decimal") from e
