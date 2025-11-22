# file: source/ui/card/supplier_card.py
from source.ui.card.card_base import CardBase
from source.ui.form.display_form.supplier_form import SupplierForm

class SupplierCard(CardBase):
    def __init__(self, ncc, *, page, mode="available"):
        super().__init__(
            page=page,
            title=ncc.TenCoSo,
            subtitle=f"Email: {ncc.Email}",
            extra_info=f"Địa Chỉ: {ncc.DiaChi}",
            image_path=ncc.HinhAnh,
            form_class=SupplierForm,
            form_data=ncc,
            width=220,
            height=320,  
            mode=mode,
        )
        self.ncc = ncc
