import flet as ft
from source.ui.Table.base_table import TableBase
from source.ui.card.supplier_card import SupplierCard

class SupplierTable(TableBase):
    def __init__(self, supplier, page, columns = 3, mode="available"):
        super().__init__(items = supplier, columns = columns, card_class = SupplierCard, page=page, mode=mode)