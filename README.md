# 📚 Đồ Án Quản Lý Kho Sách (Book Warehouse Management)

Đây là đồ án môn học Phân Tích Thiết Kế Hệ Thống Thông Tin, xây dựng một ứng dụng desktop để quản lý hoạt động của một kho sách bằng Python và thư viện Flet.

## ✨ Tính Năng Nổi Bật

*   **Giao Diện Hiện Đại:** Giao diện người dùng được thiết kế theo phong cách hiện đại, trực quan và dễ sử dụng với thư viện Flet.
*   **Dashboard Tổng Quan:** Trang chủ cung cấp cái nhìn toàn cảnh về hoạt động của kho sách thông qua các thẻ số liệu và biểu đồ phân tích (doanh thu, chi phí, thể loại sách, đối tác hàng đầu).
*   **Quản Lý Toàn Diện (CRUD):**
    *   Quản lý **Sách**: Thêm, sửa, xóa, tìm kiếm và xem chi tiết thông tin sách.
    *   Quản lý **Nhân Viên**: Quản lý thông tin nhân viên trong kho.
    *   Quản lý **Nhà Cung Cấp**: Quản lý các nguồn nhập sách.
    *   Quản lý **Nhà Phân Phối**: Quản lý các đối tác lấy sách.
*   **Quản Lý Phiếu Nhập/Xuất:**
    *   Tạo, sửa, xóa phiếu nhập và phiếu xuất kho.
    *   Hệ thống tự động cập nhật số lượng tồn kho của sách khi có giao dịch.
    *   Cơ chế giao dịch (transaction) đảm bảo tính toàn vẹn dữ liệu: nếu có lỗi xảy ra, toàn bộ thao tác sẽ được hoàn tác.
*   **Thùng Rác (Soft Delete):** Các đối tượng khi xóa sẽ được chuyển vào thùng rác, cho phép xem lại, phục hồi hoặc xóa vĩnh viễn.
*   **Xuất Dữ Liệu Chuyên Nghiệp:**
    *   **Xuất file PDF:** In các phiếu nhập, phiếu xuất ra file PDF với định dạng chuyên nghiệp.
    *   **Xuất file Excel:** Xuất danh sách (Sách, Nhân viên, NCC, NPP) ra file Excel (`.xlsx`) để dễ dàng lưu trữ và phân tích.
*   **Tìm Kiếm Thông Minh:** Chức năng tìm kiếm nhanh trên các trang danh sách.

## 🛠️ Công Nghệ Sử Dụng

*   **Ngôn ngữ:** Python 3.11+
*   **Giao diện người dùng (GUI):** Flet
*   **Cơ sở dữ liệu:** MySQL
*   **Thư viện hỗ trợ:**
    *   `mysql-connector-python`: Kết nối và thao tác với CSDL MySQL.
    *   `reportlab`: Tạo và xuất file PDF.
    *   `openpyxl`: Tạo và xuất file Excel.
    *   `pillow`: Xử lý và hiển thị hình ảnh.

## 🚀 Cài Đặt và Khởi Chạy

1.  **Cài đặt các phần mềm cần thiết:**
    *   Python 3.11+ (Nhớ tick vào ô "Add Python to PATH" khi cài đặt).
    *   XAMPP (để có Apache và MySQL Server).

2.  **Thiết lập Cơ sở dữ liệu:**
    *   Khởi động Apache và MySQL trong XAMPP Control Panel.
    *   Truy cập `http://localhost/phpmyadmin`.
    *   Sử dụng chức năng "Import" để nhập file `data/database_schema.sql` đã có sẵn trong đồ án.

3.  **Cài đặt các thư viện Python:**
    *   Mở Command Prompt (cmd) tại thư mục gốc của đồ án.
    *   Chạy lệnh:
        ```bash
        pip install flet flet-core mysql-connector-python pillow reportlab openpyxl
        ```

4.  **Chạy ứng dụng:**
    *   Vẫn tại cửa sổ cmd đó, chạy lệnh:
        ```bash
        python MainFrame.py
        ```

## 📸 Hình Ảnh Giao Diện

*(Bạn có thể thêm các ảnh chụp màn hình của ứng dụng vào đây để minh họa)*

*Trang chủ Dashboard*
!Dashboard

*Trang quản lý Sách*
!Books Page