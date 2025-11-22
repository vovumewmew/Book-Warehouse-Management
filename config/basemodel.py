from abc import ABC, abstractmethod
class BaseModel(ABC):
    @abstractmethod
    def to_dict(self) -> dict:
        """ hàm chuyển dữ liệu thành phần tử trong dict"""
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict):
        """hàm khởi tạo đối tượng từ dict (ghi DB)"""
        pass

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash(tuple(self.__dict__.values()))
    
    def __repr__(self):
        return f"<{self.__class__.__name__}-{self.__dict__}>"
    
    def __str__(self):
        return self.__repr__()
    
    
