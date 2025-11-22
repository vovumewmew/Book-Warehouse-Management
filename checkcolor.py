from PIL import Image

# Mở ảnh và lấy màu trung bình
img = Image.open(r"C:\Users\ADMIN\OneDrive\HOC TREN TRUONG\Phan Tich Thiet Ke He Thong Thong Tin\Book Warehouse Management\source\ui\picture\redpink.jpg")
color = img.convert("RGB").getpixel((img.width // 2, img.height // 2))
hex_color = "#{:02x}{:02x}{:02x}".format(*color)
print(hex_color.upper())
