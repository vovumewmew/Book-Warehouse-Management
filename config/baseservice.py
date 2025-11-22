from abc import ABC, abstractmethod
from typing import List, Any, Optional
import logging

class BaseService(ABC):
    def __init__(self, dao):
        self.dao = dao
        logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    @abstractmethod
    def get_all(self) -> List[Any]:
        pass
    
    @abstractmethod
    def create(self, obj: Any) -> bool:
        pass

    @abstractmethod
    def update(self, obj: Any) -> bool:
        pass

    @abstractmethod
    def find_by_id(self, obj_id: Any) -> Any:
        pass

    @abstractmethod
    def delete(self, obj_id: Any) -> bool:
        pass 

    def log_action(self, action: str, message: str):
        logging.info(f"[{action}] {message}")

    def handle_error(self, error: Exception):
        logging.error(f"Lỗi trong service: {error}")

    def validate_not_null(self, value, field_name):
        if not value:
            logging.warning(f"{field_name} không được để trống!")
            return False
        return True
    
    def a_numerical_value_greater_than_zero(self, interger):
        if interger < 0:
            logging.error(f"{interger} không được là số âm!")
            return False
        return True

    def execute_transaction(self, func, *args, **kwargs):
        try: 
            result = func(*args, **kwargs)
            self.dao.conn.commit()
            return result
        except Exception as e:
            self.dao.conn.rollback()
            self.handle_error(e)
            return False
