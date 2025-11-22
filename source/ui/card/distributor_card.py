from source.ui.card.card_base import CardBase
from source.ui.form.display_form.distributor_form import DistributorForm

class DistributorsCard(CardBase):
    def __init__(self, nhaphanphoi, *, page, mode="available"):
        super().__init__(
            page=page,
            title = nhaphanphoi.TenCoSo,
            subtitle = f"Email: {nhaphanphoi.Email}",
            extra_info=f"Địa Chỉ: {nhaphanphoi.DiaChi}",
            image_path=nhaphanphoi.HinhAnh,
            form_class=DistributorForm,
            form_data=nhaphanphoi,
            width=220,
            height=320,
            mode=mode,
            )