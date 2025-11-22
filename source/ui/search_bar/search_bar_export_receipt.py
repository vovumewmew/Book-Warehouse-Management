import flet as ft
from source.ui.search_bar.search_bar_base import SearchBarBase
from source.services.PhieuXuatSachService import PhieuXuatSachService

class SearchBarExportReceipt(SearchBarBase):
    def __init__(self, page: ft.Page, service: PhieuXuatSachService, on_search_result):
        """
        on_search_result: Một hàm callback nhận vào một danh sách các phiếu xuất.
        """
        super().__init__(on_search=self.perform_search)
        self.page = page
        self.service = service
        self.on_search_result = on_search_result

    def perform_search(self, query: str):
        """
        Thực hiện tìm kiếm và gọi callback với kết quả.
        """
        if not query:
            # Nếu query rỗng, lấy tất cả
            results = self.service.get_all()
        else:
            # Ngược lại, thực hiện tìm kiếm
            results = self.service.search(query)
        
        if self.on_search_result:
            self.on_search_result(results)

        self.page.update()