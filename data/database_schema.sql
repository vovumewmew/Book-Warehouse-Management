-- Tạo cơ sở dữ liệu nếu chưa tồn tại
CREATE DATABASE IF NOT EXISTS `bookwarehousemanagement` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Sử dụng cơ sở dữ liệu vừa tạo
USE `bookwarehousemanagement`;

DROP TABLE IF EXISTS chitietphieuxuat;
DROP TABLE IF EXISTS phieuxuatsach;
DROP TABLE IF EXISTS chitietphieunhap;
DROP TABLE IF EXISTS phieunhapsach;
DROP TABLE IF EXISTS nhaphanphoi;
DROP TABLE IF EXISTS nguonnhapsach;
DROP TABLE IF EXISTS nhanvien;
DROP TABLE IF EXISTS sach;
--
-- Cấu trúc bảng cho `sach`
--
CREATE TABLE `sach` (
  `ID_Sach` varchar(20) NOT NULL,
  `TenSach` varchar(255) NOT NULL,
  `TacGia` varchar(100) DEFAULT NULL,
  `TheLoai` varchar(100) DEFAULT NULL,
  `NamXuatBan` varchar(4) DEFAULT NULL,
  `NhaXuatBan` varchar(100) DEFAULT NULL,
  `NgonNgu` varchar(50) DEFAULT NULL,
  `SoLuong` int(11) NOT NULL DEFAULT 0,
  `TrangThai` varchar(50) DEFAULT 'Còn hàng', /* Hết hàng */
  `Gia` decimal(10,0) NOT NULL DEFAULT 0,
  `TinhKhaDung` varchar(20) NOT NULL DEFAULT 'Khả dụng',
  `HinhAnh` varchar(255) DEFAULT 'source/ui/picture/book_pic/default_book.jpg'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Cấu trúc bảng cho `nhanvien`
--
CREATE TABLE `nhanvien` (
  `ID_NhanVien` varchar(20) NOT NULL,
  `HoTen` varchar(100) NOT NULL,
  `GioiTinh` varchar(10) DEFAULT NULL,
  `ChucVu` varchar(100) DEFAULT NULL,
  `SoDienThoai` varchar(15) DEFAULT NULL,
  `Email` varchar(100) DEFAULT NULL,
  `TrangThaiNhanVien` varchar(50) NOT NULL DEFAULT 'Đang làm việc',
  `HinhAnh` varchar(255) DEFAULT 'source/ui/picture/employee_pic/default_employee_pic.jpg'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Cấu trúc bảng cho `nguonnhapsach`
--
CREATE TABLE `nguonnhapsach` (
  `ID_NguonNhap` varchar(20) NOT NULL,
  `TenCoSo` varchar(100) NOT NULL,
  `HinhThucNhap` varchar(50) DEFAULT NULL,
  `DiaChi` varchar(255) DEFAULT NULL,
  `SoDienThoai` varchar(15) DEFAULT NULL,
  `Email` varchar(100) DEFAULT NULL,
  `TrangThaiNCC` varchar(50) NOT NULL DEFAULT 'Hoạt Động',
  `TinhKhaDung` varchar(20) NOT NULL DEFAULT 'Khả dụng',
  `HinhAnh` varchar(255) DEFAULT 'source/ui/picture/supplier_pic/supplier_default_pic.jpg'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Cấu trúc bảng cho `nhaphanphoi`
--
CREATE TABLE `nhaphanphoi` (
  `ID_NguonXuat` varchar(20) NOT NULL,
  `TenCoSo` varchar(100) NOT NULL,
  `DiaChi` varchar(255) DEFAULT NULL,
  `SoDienThoai` varchar(15) DEFAULT NULL,
  `Email` varchar(100) DEFAULT NULL,
  `TrangThaiNPP` varchar(50) NOT NULL DEFAULT 'Hoạt Động',
  `TinhKhaDung` varchar(20) NOT NULL DEFAULT 'Khả dụng',
  `HinhAnh` varchar(255) DEFAULT 'source/ui/picture/contributors_pic/contributor_default_pic.jpg'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Cấu trúc bảng cho `phieunhapsach`
--
CREATE TABLE `phieunhapsach` (
  `ID_PhieuNhap` varchar(20) NOT NULL,
  `NgayNhap` date NOT NULL,
  `TongSoLuong` int(11) DEFAULT 0,
  `TongTien` decimal(18,2) DEFAULT 0,
  `ID_NhanVien` varchar(20) NOT NULL,
  `ID_NguonNhap` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Cấu trúc bảng cho `chitietphieunhap`
--
CREATE TABLE `chitietphieunhap` (
  `ID_PhieuNhap` varchar(20) NOT NULL,
  `ID_Sach` varchar(20) NOT NULL,
  `SoLuong` int(11) NOT NULL,
  `DonGia` decimal(18,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Cấu trúc bảng cho `phieuxuatsach`
--
CREATE TABLE `phieuxuatsach` (
  `ID_PhieuXuat` varchar(20) NOT NULL,
  `NgayXuat` date NOT NULL,
  `TongSoLuong` int(11) DEFAULT 0,
  `TongTien` decimal(18,2) DEFAULT 0,
  `ID_NhanVien` varchar(20) NOT NULL,
  `ID_NguonXuat` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Cấu trúc bảng cho `chitietphieuxuat`
--
CREATE TABLE `chitietphieuxuat` (
  `ID_PhieuXuat` varchar(20) NOT NULL,
  `ID_Sach` varchar(20) NOT NULL,
  `SoLuong` int(11) NOT NULL,
  `DonGia` decimal(18,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Thêm các khóa chính và khóa ngoại
--
ALTER TABLE `sach` ADD PRIMARY KEY (`ID_Sach`);
ALTER TABLE `nhanvien` ADD PRIMARY KEY (`ID_NhanVien`);
ALTER TABLE `nguonnhapsach` ADD PRIMARY KEY (`ID_NguonNhap`);
ALTER TABLE `nhaphanphoi` ADD PRIMARY KEY (`ID_NguonXuat`);
ALTER TABLE `phieunhapsach` ADD PRIMARY KEY (`ID_PhieuNhap`), ADD KEY `fk_pns_nv` (`ID_NhanVien`), ADD KEY `fk_pns_nns` (`ID_NguonNhap`);
ALTER TABLE `chitietphieunhap` ADD PRIMARY KEY (`ID_PhieuNhap`,`ID_Sach`), ADD KEY `fk_ctpn_sach` (`ID_Sach`);
ALTER TABLE `phieuxuatsach` ADD PRIMARY KEY (`ID_PhieuXuat`), ADD KEY `fk_pxs_nv` (`ID_NhanVien`), ADD KEY `fk_pxs_npp` (`ID_NguonXuat`);
ALTER TABLE `chitietphieuxuat` ADD PRIMARY KEY (`ID_PhieuXuat`,`ID_Sach`), ADD KEY `fk_ctpx_sach` (`ID_Sach`);

--
-- Ràng buộc khóa ngoại
--
ALTER TABLE `phieunhapsach`
  ADD CONSTRAINT `fk_pns_nv` FOREIGN KEY (`ID_NhanVien`) REFERENCES `nhanvien` (`ID_NhanVien`),
  ADD CONSTRAINT `fk_pns_nns` FOREIGN KEY (`ID_NguonNhap`) REFERENCES `nguonnhapsach` (`ID_NguonNhap`);

ALTER TABLE `chitietphieunhap`
  ADD CONSTRAINT `fk_ctpn_phieu` FOREIGN KEY (`ID_PhieuNhap`) REFERENCES `phieunhapsach` (`ID_PhieuNhap`),
  ADD CONSTRAINT `fk_ctpn_sach` FOREIGN KEY (`ID_Sach`) REFERENCES `sach` (`ID_Sach`);

ALTER TABLE `phieuxuatsach`
  ADD CONSTRAINT `fk_pxs_nv` FOREIGN KEY (`ID_NhanVien`) REFERENCES `nhanvien` (`ID_NhanVien`),
  ADD CONSTRAINT `fk_pxs_npp` FOREIGN KEY (`ID_NguonXuat`) REFERENCES `nhaphanphoi` (`ID_NguonXuat`);

ALTER TABLE `chitietphieuxuat`
  ADD CONSTRAINT `fk_ctpx_phieu` FOREIGN KEY (`ID_PhieuXuat`) REFERENCES `phieuxuatsach` (`ID_PhieuXuat`),
  ADD CONSTRAINT `fk_ctpx_sach` FOREIGN KEY (`ID_Sach`) REFERENCES `sach` (`ID_Sach`);

  -- Dữ liệu cho bảng `sach`
-- Đã được chuẩn hóa đường dẫn ảnh để tương thích trên nhiều máy.
INSERT INTO `sach` (`ID_Sach`, `TenSach`, `TacGia`, `TheLoai`, `NamXuatBan`, `NhaXuatBan`, `NgonNgu`, `SoLuong`, `TrangThai`, `Gia`, `TinhKhaDung`, `HinhAnh`) VALUES
('S01', 'Lập Trình Python Cơ Bản', 'Bernie Marchand', 'Lập trình', '2021', 'NXB Công Nghệ', 'Tiếng Việt', 12, 'Còn hàng', 95000.00, 'Khả dụng', 'source/ui/picture/book_pic/pythonprogramming_pic.jpg'),
('S02', 'Phân tích thiết kế hệ thống thông tin', 'Nguyễn Hồng Phương', 'Lập trình', '1996', 'NXB Trẻ', 'Tiếng Việt', 10, 'Còn hàng', 105000.00, 'Khả dụng', 'source/ui/picture/book_pic/pttkhttt_pic.jpg'),
('S03', 'Toán Ứng Dụng', 'Nguyễn Hồng Phương', 'Lập trình', '2005', 'NXB Đại học Sư phạm', 'Tiếng Việt', 5, 'Còn hàng', 120000.00, 'Khả dụng', 'source/ui/picture/book_pic/toanungdung_pic.jpg'),
('S04', 'Vũ Trụ Trong Vỏ Hạt Dẻ', 'Stephen Hawking', 'Khoa học', '2020', 'NXB Thế Giới', 'Tiếng Việt', 13, 'Còn hàng', 190000.00, 'Khả dụng', 'source/ui/picture/book_pic/vutrutrongvohatde_pic.jpg'),
('S05', 'Lược Sử Thời Gian', 'Stephen Hawking', 'Khoa học', '2019', 'NXB Thế Giới', 'Tiếng Việt', 11, 'Còn hàng', 170000.00, 'Khả dụng', 'source/ui/picture/book_pic/luocsuthoigian_pic.jpg'),
('S06', 'Các Thế Giới Song Song', 'Michio Kaku', 'Khoa học', '2019', 'NXB Nhã Nam', 'Tiếng Việt', 9, 'Còn hàng', 150000.00, 'Khả dụng', 'source/ui/picture/book_pic/cacthegioisongsong_pic.jpeg'),
('S07', 'Tuổi Trẻ Đáng Giá Bao Nhiêu', 'Rosie Nguyễn', 'Sách tự lực', '2018', 'NXB Hội Nhà Văn', 'Tiếng Việt', 12, 'Còn hàng', 98000.00, 'Khả dụng', 'source/ui/picture/book_pic/tuoitredanggiabaonhieu_pic.jpg'),
('S08', 'Hạt Giống Tâm Hồn', 'Nhiều tác giả', 'Sách tự lực', '2021', 'NXB Tổng hợp', 'Tiếng Việt', 15, 'Còn hàng', 95000.00, 'Khả dụng', 'source/ui/picture/book_pic/hatgiongtamhon_pic.jpg'),
('S09', 'Trên Đường Băng', 'Tony Buổi Sáng', 'Sách tự lực', '2020', 'NXB Trẻ', 'Tiếng Việt', 14, 'Còn hàng', 99000.00, 'Khả dụng', 'source/ui/picture/book_pic/trenduongbang_pic.jpg'),
('S10', 'Đắc Nhân Tâm', 'Dale Carnegie', 'Kỹ năng sống', '2020', 'NXB Trẻ', 'Tiếng Việt', 12, 'Còn hàng', 85000.00, 'Khả dụng', 'source/ui/picture/book_pic/dacnhantam_pic.jpg'),
('S11', 'Khéo Ăn Nói Sẽ Có Được Thiên Hạ', 'Trác Nhã', 'Kỹ năng sống', '2017', 'NXB Lao Động', 'Tiếng Việt', 18, 'Còn hàng', 87000.00, 'Khả dụng', 'source/ui/picture/book_pic/kheoannoisecoduocthienha_pic.png'),
('S1123', 'Tôi muốn khóc', 'Tôi', 'Truyện Buồn', '2024', 'NXB Tự Thân', 'Tiếng Mèo', 10, 'Còn hàng', 100000.00, 'Không khả dụng', 'source/ui/picture/employee_pic/default_employee_pic.jpg'),
('S12', 'Sách Test Con mèo', 'Tác giả là con mèo', 'Lịch sử', '2025', 'NXB Test', 'Tiếng Việt', 10, 'Còn hàng', 120000.00, 'Không khả dụng', 'source/ui/picture/book_pic/default_book.jpg'),
('S120', 'Con mèo ngại ngùng', 'Con mèo', 'Ngôn Tình', '2024', 'NXB Con mèo', 'Tiếng Mèo', 20, 'Còn hàng', 40000.00, 'Không khả dụng', 'source/ui/picture/employee_pic/meongaingung_pic.jpg'),
('S123', 'Sách Test Con mèo', 'Tác giả là con gà', 'Lịch sử', '2025', 'NXB Test', 'Tiếng Việt', 10, 'Còn hàng', 120000.00, 'Không khả dụng', 'source/ui/picture/book_pic/default_book.jpg'),
('S1256', 'con mèo mew mew', 'Con mèo', 'Ngôn tình', '2024', 'NXB Con mèo', 'Tiếng mèo', 50, 'Còn hàng', 40000.00, 'Không khả dụng', 'source/ui/picture/book_pic/default_book.jpg'),
('S13', 'Dế Mèn Phiêu Lưu Ký', 'Tô Hoài', 'Văn học', '2017', 'NXB Kim Đồng', 'Tiếng Việt', 16, 'Còn hàng', 45000.00, 'Khả dụng', 'source/ui/picture/book_pic/demenphieuluuky_pic.jpg'),
('S14', 'Truyện Cười Việt Nam Thời @', 'Nguyễn Cừ', 'Truyện cười', '2021', 'NXB Văn Học', 'Tiếng Việt', 17, 'Còn hàng', 45000.00, 'Khả dụng', 'source/ui/picture/book_pic/truyencuoivietnam_pic.png'),
('S15', 'Truyện Cười Dân Gian Việt Nam', 'Nhiều Tác Giả', 'Truyện cười', '2021', 'NXB Dân Trí', 'Tiếng Việt', 20, 'Còn hàng', 38000.00, 'Không khả dụng', 'source/ui/picture/book_pic/truyencuoidangian_pic.jpg'),
('S28', 'Con gà la la', 'Con gà', 'Truyện cười', '2025', 'NXB Con gà', 'Tiếng Gà', 10, 'Còn hàng', 40000.00, 'Không khả dụng', 'source/ui/picture/book_pic/default_book.jpg'),
('S4444', 'Xin Chào', 'Con Mèo', 'Truyện Buồn', '2024', 'NXB Tự Thân', 'Tiếng Việt', 10, 'Còn hàng', 10000.00, 'Không khả dụng', 'source/ui/picture/book_pic/default_book.jpg'),
('S46', 'Ông Minh', 'Minh Lê', 'Truyện Cười', '2024', 'NXB Con mèo', 'Tiếng Việt', 0, 'Hết hàng', 100000.00, 'Không khả dụng', 'source/ui/picture/book_pic/default_book.jpg'),
('S5555', 'Con mèo vui vẻ', 'Con mèo', 'Truyện Cười', '2024', 'NXB Con mèo', 'Tiếng Mèo', 40, 'Còn hàng', 50000.00, 'Không khả dụng', 'source/ui/picture/book_pic/default_book.jpg'),
('S56', 'Bé Nhi Xinh Đẹp', 'Vũ cute', 'Ngôn Tình', '2025', 'NXB Nhã Nham', 'Tiếng Việt', 0, 'Hết hàng', 10000.00, 'Không khả dụng', 'source/ui/picture/book_pic/default_book.jpg'),
('S59', 'mèo chụp ảnh thẻ', 'Con mèo', 'Truyện cười', '2024', 'NXB Con mèo', 'Tiếng Mèo', 10, 'Còn hàng', 40000.00, 'Không khả dụng', 'source/ui/picture/employee_pic/default_employee_pic.jpg'),
('S666', 'Chào ngày mới', 'Con mèo', 'Truyện Cười', '2024', 'NXB Tự Thân', 'Tiếng Việt', 10, 'Còn hàng', 10000.00, 'Không khả dụng', 'source/ui/picture/book_pic/default_book.jpg'),
('S678', 'mèo hung dữ', 'Con mèo', 'Giật gân', '2024', 'NXB Con mèo', 'Tiếng Mèo', 10, 'Còn hàng', 20000.00, 'Không khả dụng', 'source/ui/picture/employee_pic/meohungdu_pic.jpg'),
('S777', 'Xin Chào', 'Con mèo', 'Truyện Vui', '2024', 'NXB Tự Thân', 'Tiếng Việt', 10, 'Còn hàng', 100000.00, 'Không khả dụng', 'source/ui/picture/book_pic/default_book.jpg'),
('S78', 'Con mèo phi công', 'Con mèo', 'Máy bay', '2024', 'NXB Nhã Nam', 'Tiếng Mèo', 10, 'Còn hàng', 100000.00, 'Không khả dụng', 'source/ui/picture/book_pic/default_book.jpg'),
('S883', 'Trên Đường Băng', 'Con mèo béo', 'Viễn Tưởng', '2021', 'NXB Tự Thân', 'Tiếng Việt', 10, 'Còn hàng', 10000.00, 'Không khả dụng', 'source/ui/picture/book_pic/default_book.jpg'),
('S8888', 'Cầu trời cho con thành công', 'Con mèo', 'Kinh', '2025', 'NXB Tâm Thức', 'Tiếng Việt', 10, 'Còn hàng', 2000.00, 'Khả dụng', 'source/ui/picture/book_pic/default_book.jpg'),
('S90', 'Con mèo trắng đen', 'con mèo', 'mew mew', '2024', 'NXB Con mèo', 'Tiếng Mèo', 10, 'Còn hàng', 10000.00, 'Không khả dụng', 'source/ui/picture/book_pic/default_book.jpg'),
('S91', 'Con mèo im mồm', 'Con mèo mew mew', 'Giật gân', '2024', 'NXB Con mèo', 'Tiếng mèo', 10, 'Còn hàng', 10000.00, 'Không khả dụng', 'source/ui/picture/employee_pic/meoimmom_pic.jpg'),
('S911', 'Test 1 lần cuối cùng', 'Tôi là con mèo', 'Truyện Cười', '2024', 'NXB Con mèo', 'Tiếng Mèo', 10, 'Còn hàng', 10000.00, 'Khả dụng', 'source/ui/picture/book_pic/default_book.jpg'),
('S912', 'Test 2 lần cuối cùng', 'Tôi', 'Truyện Buồn', '2025', 'NXB Con mèo', 'Tiếng mèo', 10, 'Còn hàng', 80000.00, 'Khả dụng', 'source/ui/picture/book_pic/default_book.jpg'),
('S913', 'Test 3 lần cuối cùng', 'Tôi', 'Buồn', '2024', 'NXB Tôi', 'Tiếng Việt', 10, 'Còn hàng', 20000.00, 'Khả dụng', 'source/ui/picture/book_pic/default_book.jpg'),
('S916', 'Sách test lần 5', 'Tôi', 'Truyện Buồn', '2024', 'NXB Tự Thân', 'Tiếng Việt', 10, 'Còn hàng', 10000.00, 'Khả dụng', 'source/ui/picture/book_pic/default_book.jpg'),
('S917', 'Sách test lần 6', 'Tôi', 'Truyện Buồn', '2025', 'NXB Tự Thân', 'Tiếng Việt', 10, 'Còn hàng', 100000.00, 'Khả dụng', 'source/ui/picture/book_pic/default_book.jpg'),
('S918', 'Sách test lần 8', 'Tôi', 'Truyện Buồn', '2024', 'NXB Tự Thân', 'Tiếng Mèo', 10, 'Còn hàng', 100000.00, 'Khả dụng', 'source/ui/picture/book_pic/default_book.jpg'),
('S919', 'Sách test lần 9', 'Tôi', 'Tự Thân', '2024', 'NXB Tự Thân', 'Tiếng Việt', 9, 'Còn hàng', 10000.00, 'Khả dụng', 'source/ui/picture/book_pic/default_book.jpg'),
('S92', 'Con mèo cam chịu', 'Con mèo', 'Buồn', '2025', 'NXB Con mèo', 'tiếng Mèo', 10, 'Còn hàng', 50000.00, 'Không khả dụng', 'source/ui/picture/employee_pic/meocamchiu_pic.jpg'),
('S920', 'Con mèo phán xét', 'Con mèo', 'Buồn', '2024', 'NXB Con mèo', 'Tiếng Việt', 12, 'Còn hàng', 120000.00, 'Không khả dụng', 'source/ui/picture/employee_pic/meophanxet_pic.jpg'),
('S921', 'Sách test lần 11', 'Tôi', 'Truyện Buồn', '2024', 'NXB Tự Thân', 'Tiếng Mèo', 9, 'Còn hàng', 10000.00, 'Khả dụng', 'source/ui/picture/book_pic/default_book.jpg'),
('S923', 'Sách test lần thứ 12', 'Con mèo', 'Truyện Buồn', '2024', 'NXB Tự Thân', 'Tiếng Mèo', 11, 'Còn hàng', 80000.00, 'Khả dụng', 'source/ui/picture/book_pic/default_book.jpg'),
('S924', 'Sách test lần thứ 13', 'Tôi', 'Truyện Buồn', '2024', 'NXB Tự Thân', 'Tiếng Mèo', 10, 'Còn hàng', 80000.00, 'Khả dụng', 'source/ui/picture/book_pic/default_book.jpg'),
('S925', 'Sách test lần thứ 14', 'Tôi', 'Truyện Buồn', '2024', 'NXB Tự Thân', 'Tiếng Mèo', 11, 'Còn hàng', 70000.00, 'Khả dụng', 'source/ui/picture/book_pic/default_book.jpg'),
('S93', 'Con mèo cầm hoa', 'Con mèo', 'Tình cảm', '2024', 'NXB Con mèo', 'Tiếng Mèo', 50, 'Còn hàng', 50000.00, 'Không khả dụng', 'source/ui/picture/employee_pic/meocamhoa_pic.jpg'),
('S931', 'Sách test lần thứ 15', 'Tôi', 'Truyện Buồn', '2024', 'NXB Tự Thân', 'Tiếng Mèo', 9, 'Còn hàng', 60000.00, 'Khả dụng', 'source/ui/picture/book_pic/default_book.jpg'),
('S936', 'Sách test lần thứ 16', 'Tôi', 'Truyện Buồn', '2024', 'NXB Tự Thân', 'Tiếng Mèo', 7, 'Còn hàng', 90000.00, 'Khả dụng', 'source/ui/picture/book_pic/default_book.jpg'),
('S937', 'Sách test lần thứ 17', 'Tôi', 'Truyện Buồn', '2024', 'NXB Tự Thân', 'Tiếng Mèo', 11, 'Còn hàng', 50000.00, 'Khả dụng', 'source/ui/picture/book_pic/default_book.jpg'),
('S938', 'Sách test lần thứ 18', 'Tôi', 'Truyện Buồn', '2024', 'NXB Tự Thân', 'Tiếng Mèo', 10, 'Còn hàng', 50000.00, 'Khả dụng', 'source/ui/picture/book_pic/default_book.jpg'),
('S939', 'Sách test lần thứ 19', 'Tôi', 'Truyện Buồn', '2024', 'NXB Tự Thân', 'Tiếng Mèo', 10, 'Còn hàng', 80000.00, 'Không khả dụng', 'source/ui/picture/book_pic/default_book.jpg'),
('S94', 'Con mèo căng thẳng', 'Con mèo', 'Giật gân', '2024', 'NXB Con mèo', 'Tiếng mèo', 60, 'Còn hàng', 60000.00, 'Không khả dụng', 'source/ui/picture/employee_pic/meocangthang_pic.jpg'),
('S940', 'Sách test lần thứ 20', 'Tôi', 'Truyện Buồn', '2024', 'NXB Tự Thân', 'Tiếng Mèo', 10, 'Còn hàng', 10000.00, 'Không khả dụng', 'source/ui/picture/book_pic/default_book.jpg'),
('S942', 'Sách test lần thứ 21', 'Tôi', 'Truyện Buồn', '2024', 'NXB Tự Thân', 'Tiếng Mèo', 10, 'Còn hàng', 60000.00, 'Không khả dụng', 'source/ui/picture/book_pic/default_book.jpg'),
('S946', 'Sách test lần thứ 22', 'Tôi', 'Truyện Buồn', '2024', 'NXB Tự Thân', 'Tiếng Mèo', 10, 'Còn hàng', 60000.00, 'Khả dụng', 'source/ui/picture/book_pic/default_book.jpg'),
('S947', 'Sách test lần thứ 23', 'Tôi', 'Truyện Buồn', '2025', 'NXB Tự Thân', 'Tiếng Việt', 4, 'Còn hàng', 70000.00, 'Khả dụng', 'source/ui/picture/book_pic/default_book.jpg'),
('S948', 'Sách test lần thứ 24', 'Tôi', 'Truyện Buồn', '2025', 'NXB Tự Thân', 'Tiếng Việt', 3, 'Còn hàng', 80000.00, 'Khả dụng', 'source/ui/picture/book_pic/default_book.jpg'),
('S98', 'Mèo lag', 'Con mèo', 'Câu đố', '2024', 'NXB Con mèo', 'Tiếng Mèo', 10, 'Còn hàng', 80000.00, 'Không khả dụng', 'source/ui/picture/employee_pic/meolag_pic.jpg'),
('S9999', 'Con mèo phán xét', 'Con mèo', 'Buồn', '2024', 'NXB Con Mèo', 'Tiếng Việt', 20, 'Còn hàng', 20000.00, 'Không khả dụng', 'source/ui/picture/employee_pic/meophanxet_pic.jpg');

-- Dữ liệu cho bảng `nhanvien`
-- Đã được chuẩn hóa đường dẫn ảnh để tương thích trên nhiều máy.
INSERT INTO `nhanvien` (`ID_NhanVien`, `HoTen`, `GioiTinh`, `ChucVu`, `TrangThaiNhanVien`, `SoDienThoai`, `Email`, `HinhAnh`) VALUES
('NV01', 'Lê Tấn Nhật Minh', 'Nam', 'Quản lý kho sách', 'Đang làm việc', '0905237841', 'nhatminh.le@gmail.com', 'source/ui/picture/employee_pic/meocamhoa_pic.jpg'),
('NV02', 'Nguyễn Thị Thu Thảo', 'Nữ', 'Nhân viên nhập sách', 'Đang làm việc', '0918642753', 'thuthao.nguyen@gmail.com', 'source/ui/picture/employee_pic/meophanxet_pic.jpg'),
('NV03', 'Hoàng Mai Thanh Trúc', 'Nữ', 'Nhân viên nhập sách', 'Đang làm việc', '0932874690', 'thanhhtruc.hoang@gmail.com', 'source/ui/picture/employee_pic/meongaingung_pic.jpg'),
('NV04', 'Võ Văn Truyền Vũ', 'Nam', 'Nhân viên xuất sách', 'Đang làm việc', '0976290967', 'truyenvu.vo@gmail.com', 'source/ui/picture/employee_pic/meocamchiu_pic.jpg'),
('NV05', 'Trương Thị Ngọc Nhi', 'Nữ', 'Nhân viên xuất sách', 'Đang làm việc', '0368449634', 'ngocnhi.truong@gmail.com', 'source/ui/picture/employee_pic/meohungdu_pic.jpg'),
('NV06', 'Phạm Thanh Trúc', 'Nữ', 'Nhân viên kiểm kê kho', 'Đang làm việc', '0926513804', 'thanhtruc.pham@gmail.com', 'source/ui/picture/employee_pic/meolag_pic.jpg'),
('NV07', 'Vương Tâm Nguyên', 'Nam', 'Nhân viên kiểm kê kho', 'Đang làm việc', '0968702415', 'tamnguyen.vuong@gmail.com', 'source/ui/picture/employee_pic/meocangthang_pic.jpg'),
('NV201', 'Nhân Viên test A', 'Nữ', 'Nhân viên nhập sách', 'Đang làm việc', '0163202203', 'nhanviena@gmail.com', 'source/ui/picture/employee_pic/default_employee_pic.jpg'),
('NV202', 'Nhân viên test B', 'Nam', 'Nhân viên xuất sách', 'Đang làm việc', '0367209602', 'nhanvienb@gmail.com', 'source/ui/picture/employee_pic/default_employee_pic.jpg'),
('NV203', 'Nhân viên test C', 'Nữ', 'Quản lý kho sách', 'Đã nghỉ việc', '0693022011', 'nhanvienc@gmail.com', 'source/ui/picture/employee_pic/default_employee_pic.jpg'),
('NV204', 'Nhân viên test D', 'Nữ', 'Nhân viên nhập sách', 'Đang làm việc', '4444444444', 'nhanviend@gmail.com', 'source/ui/picture/employee_pic/default_employee_pic.jpg'),
('NV205', 'Nhân viên test E', 'Nam', 'Nhân viên xuất sách', 'Đang làm việc', '5555555555', 'nhanviene@gmail.com', 'source/ui/picture/employee_pic/default_employee_pic.jpg'),
('NV206', 'Nhân viên test F', 'Nam', 'Nhân viên kiểm kê kho', 'Đang làm việc', '6666666666', 'nhanvienf@gmail.com', 'source/ui/picture/employee_pic/default_employee_pic.jpg'),
('NV97', 'Trịnh Trần Phương Tuấn', 'Nam', 'Nhân viên nhập sách', 'Đã nghỉ việc', '0976201997', 'jack97@gmail.com', 'source/ui/picture/employee_pic/default_employee_pic.jpg');

-- Dữ liệu cho bảng `nhaphanphoi`
-- Đã được chuẩn hóa đường dẫn ảnh để tương thích trên nhiều máy.
INSERT INTO `nhaphanphoi` (`ID_NguonXuat`, `TenCoSo`, `DiaChi`, `SoDienThoai`, `Email`, `TrangThaiNPP`, `TinhKhaDung`, `HinhAnh`) VALUES
('NX001', 'Công ty CP Phát Hành Sách TP.HCM', '60-62 Lê Lợi, Quận 1, TP.HCM', '02838223344', 'phathanh@hcmbook.vn', 'Hoạt Động', 'Khả dụng', 'source/ui/picture/contributors_pic/nppsaigon_pic.jpg'),
('NX002', 'Công ty Phân Phối Fahasa Sài Gòn', '12 Nguyễn Văn Cừ, Quận 5, TP.HCM', '02838383838', 'fahasa.sg@fahasa.com', 'Hoạt Động', 'Khả dụng', 'source/ui/picture/contributors_pic/fahasa_pic.png'),
('NX003', 'Nhà sách Nguyễn Huệ', '55 Trần Ðình Xu, Phường Ông Lãnh, TP.HCM', '02839029315', 'nhasachnguyenhue@gmail.com', 'Hoạt Động', 'Khả dụng', 'source/ui/picture/contributors_pic/nhasachnguyenhue_pic.webp'),
('NX004', 'Nhà sách Hải An', '2B Nguyễn Thị Minh Khai, Đa Kao, Quận 1, TP.HCM', '02822299261', 'nhasachhaian@gmail.com', 'Hoạt Động', 'Khả dụng', 'source/ui/picture/contributors_pic/nhasachhaian_pic.jpg'),
('NX005', 'Công ty Nhã Nam', '59 Đặng Thai Mai, Tây Hồ, Hà Nội', '02437255555', 'contact@nhanam.vn', 'Hoạt Động', 'Khả dụng', 'source/ui/picture/contributors_pic/nhasachnhanam_pic.webp'),
('NX006', 'Công ty Sách AlphaBooks', '176 Thái Hà, Đống Đa, Hà Nội', '02438383838', 'info@alphabooks.vn', 'Hoạt Động', 'Khả dụng', 'source/ui/picture/contributors_pic/alphabooks_pic.jpg'),
('NX202', 'Nhà phân phối test 2', 'địa chỉ test 2', '2222222222', 'nhaphanphoi2@gmail.com', 'Hoạt Động', 'Không khả dụng', 'source/ui/picture/contributors_pic/contributor_default_pic.jpg'),
('NX302', 'Nhà phân phối test 3', 'địa chỉ test 3', '33333333333', 'nhaphanphoi3@gmail.com', 'Hoạt Động', 'Khả dụng', 'source/ui/picture/contributors_pic/contributor_default_pic.jpg'),
('NX303', 'Nhà phân phối test 4', 'Địa chỉ test 4', '4444444444', 'nhaphanphoi4@gmail.com', 'Hoạt Động', 'Không khả dụng', 'source/ui/picture/contributors_pic/contributor_default_pic.jpg'),
('NX304', 'Nhà phân phối test 5', 'Địa chỉ test 5', '5555555555', 'nhaphanphoi5@gmail.com', 'Hoạt Động', 'Khả dụng', 'source/ui/picture/contributors_pic/contributor_default_pic.jpg'),
('NX305', 'Nhà phân phối test 6', 'địa chỉ test 6', '6666666666', 'nhaphanphoi6@gmail.com', 'Hoạt Động', 'Khả dụng', 'source/ui/picture/contributors_pic/contributor_default_pic.jpg');

-- Dữ liệu cho bảng `nguonnhapsach`
-- Đã được chuẩn hóa đường dẫn ảnh để tương thích trên nhiều máy.
INSERT INTO `nguonnhapsach` (`ID_NguonNhap`, `TenCoSo`, `HinhThucNhap`, `DiaChi`, `SoDienThoai`, `Email`, `TrangThaiNCC`, `TinhKhaDung`, `HinhAnh`) VALUES
('NN01', 'Nhà sách Fahasa', 'Mua sỉ', '123 Lê Lợi, Quận 1, TP.HCM', '02838222222', 'fahasa@fahasa.com', 'Hoạt Động', 'Khả dụng', 'source/ui/picture/supplier_pic/supplier_default_pic.jpg'),
('NN02', 'Nhà Sách Phương Nam', 'Mua sỉ', '161B Lý Chính Thắng, Quận 3, TP.HCM', '02839309309', 'phuongnam@nhasach.vn', 'Hoạt Động', 'Khả dụng', 'source/ui/picture/supplier_pic/supplier_default_pic.jpg'),
('NN03', 'Nhà Sách Nguyễn Văn Cừ', 'Ký gửi', '45 Nguyễn Thị Minh Khai, Quận 1, TP.HCM', '0909123456', 'nguyenvancu@gmail.com', 'Hoạt Động', 'Khả dụng', 'source/ui/picture/supplier_pic/supplier_default_pic.jpg'),
('NN04', 'Nhà Sách Tân Bình', 'Hợp tác', '35 Cộng Hòa, Quận Tân Bình, TP.HCM', '02838383838', 'tanbinh@nhasach.vn', 'Hoạt Động', 'Khả dụng', 'source/ui/picture/supplier_pic/supplier_default_pic.jpg'),
('NN05', 'Chương trình Tặng Sách Thiện Nguyện', 'Tặng', '77 Hoàng Hoa Thám, Quận Bình Thạnh, TP.HCM', '0938123123', 'thiennguyen@gmail.com', 'Hoạt Động', 'Khả dụng', 'source/ui/picture/supplier_pic/supplier_default_pic.jpg'),
('NN402', 'Nhà cung cấp test 2', 'Kí Gửi', 'Địa chỉ test 2', '2222222222', 'nhacungcap2@gmail.com', 'Hoạt Động', 'Không khả dụng', 'source/ui/picture/supplier_pic/supplier_default_pic.jpg'),
('NN403', 'Nhà cung cấp test 3', 'Kí Gửi', 'Địa chỉ test 3', '3333333333', 'nhacungcap3@gmail.com', 'Hoạt Động', 'Khả dụng', 'source/ui/picture/supplier_pic/supplier_default_pic.jpg'),
('NN404', 'Nhà cung cấp test 4', 'Nhập', 'Địa chỉ test 4', '4444444444', 'nhacungcap4@gmail.com', 'Hoạt Động', 'Khả dụng', 'source/ui/picture/supplier_pic/supplier_default_pic.jpg'),
('NN911', 'Nhà cung cấp vui vẻ', 'Gửi Tặng', '42, Yên Lãng, phường Đống Đa, Hà Nội', '0901203204', 'nhacungcapvuive@gmail.com', 'Hoạt Động', 'Không khả dụng', 'source/ui/picture/supplier_pic/supplier_default_pic.jpg');

-- Dữ liệu cho bảng `phieunhapsach`
INSERT INTO `phieunhapsach` (`ID_PhieuNhap`, `NgayNhap`, `TongSoLuong`, `TongTien`, `ID_NhanVien`, `ID_NguonNhap`) VALUES
('PN01', '2025-09-11', 10, 950000.00, 'NV02', 'NN01'),
('PN02', '2025-09-12', 11, 1155000.00, 'NV02', 'NN02'),
('PN03', '2025-09-13', 12, 1440000.00, 'NV03', 'NN03'),
('PN04', '2025-09-14', 10, 1900000.00, 'NV03', 'NN04'),
('PN05', '2025-09-15', 13, 2210000.00, 'NV02', 'NN05'),
('PN06', '2025-09-16', 14, 2100000.00, 'NV03', 'NN05'),
('PN07', '2025-09-17', 15, 1455000.00, 'NV03', 'NN04'),
('PN08', '2025-09-18', 14, 1274000.00, 'NV02', 'NN03'),
('PN09', '2025-09-19', 16, 904000.00, 'NV02', 'NN02'),
('PN501', '2025-11-24', 30, 1100000.00, 'NV02', 'NN01'),
('PN502', '2025-11-24', 32, 1776000.00, 'NV03', 'NN04'),
('PN503', '2025-05-10', 27, 3856000.00, 'NV201', 'NN403'),
('PN504', '2025-05-10', 18, 1790000.00, 'NV03', 'NN01'),
('PN505', '2025-05-10', 20, 1990000.00, 'NV02', 'NN02'),
('PN506', '2025-08-07', 22, 2190000.00, 'NV03', 'NN03'),
('PN507', '2025-10-25', 22, 2190000.00, 'NV03', 'NN05'),
('PN508', '2025-07-28', 2, 200000.00, 'NV02', 'NN02'),
('PN509', '2025-11-08', 1, 100000.00, 'NV02', 'NN03'),
('PN510', '2025-09-08', 1, 10000.00, 'NV03', 'NN03'),
('PN511', '2025-01-25', 1, 80000.00, 'NV02', 'NN02'),
('PN512', '2024-06-08', 1, 90000.00, 'NV03', 'NN01'),
('PN513', '2025-09-04', 1, 70000.00, 'NV201', 'NN04'),
('PN514', '2024-08-05', 1, 70000.00, 'NV201', 'NN02'),
('PN515', '2025-08-24', 1, 50000.00, 'NV03', 'NN03');

-- Dữ liệu cho bảng `chitietphieunhap`
INSERT INTO `chitietphieunhap` (`ID_PhieuNhap`, `ID_Sach`, `SoLuong`, `DonGia`) VALUES
('PN01', 'S01', 10, 95000.00),
('PN02', 'S02', 11, 105000.00),
('PN03', 'S03', 12, 120000.00),
('PN04', 'S04', 10, 190000.00),
('PN05', 'S05', 13, 170000.00),
('PN06', 'S06', 14, 150000.00),
('PN07', 'S07', 10, 98000.00),
('PN07', 'S08', 5, 95000.00),
('PN08', 'S09', 6, 99000.00),
('PN08', 'S10', 8, 85000.00),
('PN09', 'S11', 2, 87000.00),
('PN09', 'S12', 10, 55000.00),
('PN09', 'S13', 2, 45000.00),
('PN09', 'S14', 2, 45000.00),
('PN501', 'S919', 10, 10000.00),
('PN501', 'S937', 20, 50000.00),
('PN501', 'S938', 20, 50000.00),
('PN502', 'S07', 1, 98000.00),
('PN502', 'S916', 20, 10000.00),
('PN502', 'S937', 50, 50000.00),
('PN503', 'S04', 30, 190000.00),
('PN503', 'S09', 20, 99000.00),
('PN504', 'S01', 1, 95000.00),
('PN504', 'S02', 1, 105000.00),
('PN505', 'S01', 1, 95000.00),
('PN505', 'S02', 1, 105000.00),
('PN506', 'S01', 1, 95000.00),
('PN506', 'S02', 1, 105000.00),
('PN507', 'S01', 1, 95000.00),
('PN507', 'S02', 1, 105000.00),
('PN508', 'S01', 1, 95000.00),
('PN508', 'S02', 1, 105000.00),
('PN509', 'S918', 1, 100000.00),
('PN510', 'S919', 1, 10000.00),
('PN511', 'S923', 1, 80000.00),
('PN512', 'S936', 1, 90000.00),
('PN513', 'S925', 1, 70000.00),
('PN514', 'S925', 1, 70000.00),
('PN515', 'S937', 1, 50000.00);

-- Dữ liệu cho bảng `phieuxuatsach`
INSERT INTO `phieuxuatsach` (`ID_PhieuXuat`, `NgayXuat`, `TongSoLuong`, `TongTien`, `ID_NhanVien`, `ID_NguonXuat`) VALUES
('PX001', '2025-09-21', 10, 950000.00, 'NV04', 'NX001'),
('PX002', '2025-09-22', 8, 840000.00, 'NV05', 'NX002'),
('PX003', '2025-09-23', 5, 600000.00, 'NV04', 'NX003'),
('PX004', '2025-09-24', 7, 1330000.00, 'NV05', 'NX004'),
('PX005', '2025-09-25', 6, 1020000.00, 'NV04', 'NX005'),
('PX006', '2025-09-26', 10, 940000.00, 'NV04', 'NX006'),
('PX007', '2025-09-27', 13, 1259000.00, 'NV05', 'NX003'),
('PX008', '2025-09-28', 9, 835000.00, 'NV05', 'NX002'),
('PX009', '2025-09-29', 11, 651000.00, 'NV04', 'NX001'),
('PX601', '2025-05-10', 17, 980000.00, 'NV05', 'NX004'),
('PX602', '2025-05-20', 20, 1990000.00, 'NV05', 'NX005'),
('PX603', '2025-10-08', 2, 200000.00, 'NV04', 'NX001'),
('PX604', '2025-11-08', 1, 10000.00, 'NV05', 'NX003'),
('PX605', '2025-09-08', 1, 90000.00, 'NV05', 'NX002'),
('PX606', '2025-10-25', 1, 90000.00, 'NV04', 'NX004'),
('PX607', '2024-11-08', 1, 60000.00, 'NV04', 'NX004'),
('PX609', '2025-06-06', 1, 90000.00, 'NV202', 'NX004'),
('PX610', '2025-10-08', 1, 90000.00, 'NV05', 'NX003'),
('PX611', '2025-06-05', 1, 70000.00, 'NV05', 'NX002');

-- Dữ liệu cho bảng `chitietphieuxuat`
INSERT INTO `chitietphieuxuat` (`ID_PhieuXuat`, `ID_Sach`, `SoLuong`, `DonGia`) VALUES
('PX001', 'S01', 10, 95000.00),
('PX002', 'S02', 8, 105000.00),
('PX003', 'S03', 5, 120000.00),
('PX004', 'S04', 7, 190000.00),
('PX005', 'S05', 6, 170000.00),
('PX006', 'S06', 5, 150000.00),
('PX006', 'S15', 5, 38000.00),
('PX007', 'S07', 8, 98000.00),
('PX007', 'S08', 5, 95000.00),
('PX008', 'S09', 5, 99000.00),
('PX008', 'S10', 4, 85000.00),
('PX009', 'S11', 3, 87000.00),
('PX009', 'S12', 3, 55000.00),
('PX009', 'S13', 3, 45000.00),
('PX009', 'S14', 2, 45000.00),
('PX601', 'S918', 1, 100000.00),
('PX601', 'S919', 2, 10000.00),
('PX602', 'S01', 1, 95000.00),
('PX602', 'S02', 1, 105000.00),
('PX603', 'S01', 1, 95000.00),
('PX603', 'S02', 1, 105000.00),
('PX604', 'S921', 1, 10000.00),
('PX605', 'S936', 1, 90000.00),
('PX606', 'S936', 1, 90000.00),
('PX607', 'S931', 1, 60000.00),
('PX609', 'S936', 1, 90000.00),
('PX610', 'S936', 1, 90000.00),
('PX611', 'S925', 1, 70000.00);
