import os

def get_absolute_path(relative_path: str) -> str:
    """
    Chuyển đường dẫn tương đối (từ thư mục gốc project, chứa MainFrame.py) sang tuyệt đối.
    Chuẩn hóa đường dẫn + đổi \ thành / cho Flet.
    """
    # --- Thư mục gốc project (chứa MainFrame.py) ---
    project_root = os.path.dirname(os.path.abspath(__file__))
    # Nếu file này nằm trong util/, lên 1 cấp để về thư mục gốc project
    project_root = os.path.abspath(os.path.join(project_root, ".."))

    # --- Nối với đường dẫn tương đối ---
    abs_path = os.path.join(project_root, relative_path)

    # --- Chuẩn hóa đường dẫn + đổi \ thành / ---
    return os.path.normpath(abs_path).replace("\\", "/")
