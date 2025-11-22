# source/ui/table/employee_table.py
from source.ui.card.employees_card import EmployeeCard
from source.ui.Table.base_table import TableBase

class EmployeeTable(TableBase):
    def __init__(self, employees, *, page, columns=3, mode="available"):
        super().__init__(items=employees, columns=columns, card_class=EmployeeCard, page=page, mode=mode)
