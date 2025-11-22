# source/ui/card/employee_card.py
from source.ui.card.card_base import CardBase
from source.ui.form.display_form.employee_form import EmployeeForm

class EmployeeCard(CardBase):
    def __init__(self, nhanvien, *, page, mode="available"):
        super().__init__(
            page=page,
            title=nhanvien.HoTen,
            subtitle=f"Chức vụ: {nhanvien.ChucVu}",
            image_path=nhanvien.HinhAnh,
            extra_info=f"Email: {nhanvien.Email}",
            form_class=EmployeeForm,
            form_data=nhanvien,
            width=220,
            height=290,
            mode=mode,
        )
