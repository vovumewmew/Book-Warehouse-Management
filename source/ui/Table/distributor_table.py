from source.ui.Table.base_table import TableBase
from source.ui.card.distributor_card import DistributorsCard

class DistributorTable(TableBase):
    def __init__(self, distributors, page, columns=3, mode="available"):
        super().__init__(items=distributors, columns=columns, card_class=DistributorsCard, page=page, mode=mode)
