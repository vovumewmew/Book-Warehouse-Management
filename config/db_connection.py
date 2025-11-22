import mysql.connector
from mysql.connector import Error
class DatabaseConnection:
    def __init__(self, host = "127.0.0.1", user = "root", password = "Vu24112004", database = "bookwarehousemanagement"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        """tạo kết nối tới CSDL"""
        try:
            self.connection = mysql.connector.connect(
                host = self.host,
                user = self.user,
                password = self.password,
                database = self.database
            )
            if self.connection.is_connected():
                print("Đã kết nối tới database thành công")
                return self.connection
        except Error as e:
            print(f"không thể kết nối với database {e}")
            return None

    def disconnect(self):
        """đóng kết nối với database"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Đã đóng kết nối với database")

    def get_connection(self):
        """trả về đối tượng connection (nếu đã kết nối)"""
        if not self.connection or not self.connection.is_connected():
            print("🔄 Reconnecting to database...")
            self.connect()
        return self.connection
