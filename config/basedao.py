from abc import ABC, abstractmethod
from typing import Any, Optional, List

class BaseDAO(ABC):
    @abstractmethod
    def insert(self, obj: Any):
        """hàm thêm đối tượng"""
        pass

    @abstractmethod
    def update(self, obj: Any):
        """hàm sửa thông tin"""
        pass

    @abstractmethod
    def find_by_key(self, id_: str):
        """hàm tìm kiếm theo mã"""
        pass

    @abstractmethod
    def delete(self, id_: str):
        """hàm xóa đối tượng theo mã"""
        pass

    @abstractmethod
    def get_all(self) -> List[Any]:
        """hàm lấy tất cả thông tin trong database"""
        pass