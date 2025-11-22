from decimal import Decimal, InvalidOperation

def to_decimal(value) -> Decimal:
    """
    Chuyển đổi giá trị sang Decimal và làm tròn 2 chữ số sau dấu phẩy.
    """
    if value is None:
        return Decimal("0.00")
    try:
        return Decimal(str(value)).quantize(Decimal("0.00"))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError(f"Giá trị '{value}' không hợp lệ cho Decimal")


def is_decimal(value) -> bool:
    """
    Kiểm tra xem giá trị có phải kiểu Decimal hợp lệ hay không.
    """
    if isinstance(value, Decimal):
        return True
    try:
        Decimal(str(value))
        return True
    except (InvalidOperation, ValueError, TypeError):
        return False


def validate_money(value, field_name: str = "Giá trị") -> Decimal:
    """
    Kiểm tra và chuẩn hóa giá trị tiền tệ.
    - Phải là số (Decimal, float, int, hoặc chuỗi số)
    - Không được âm
    - Làm tròn 2 chữ số
    """
    if value is None:
        raise ValueError(f"{field_name} không được để trống!")

    try:
        dec_value = to_decimal(value)
    except Exception:
        raise ValueError(f"{field_name} phải là số hợp lệ!")

    if dec_value < Decimal("0.00"):
        raise ValueError(f"{field_name} không được âm!")

    if dec_value > Decimal("9999999999.99"):
        raise ValueError(f"{field_name} vượt quá giới hạn cho phép!")

    return dec_value
