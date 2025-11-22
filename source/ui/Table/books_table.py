from source.ui.card.books_card import BookCard
from source.ui.Table.base_table import TableBase

class BookTable(TableBase):
    def __init__(self, books, page, columns=3, mode="available"):
        super().__init__(items=books, columns=columns, card_class=BookCard, page=page, mode=mode)
