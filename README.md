<div align="center">
  <h1>🏥 HT Beauty Clinic Management System</h1>
  <p><b>Hệ thống Quản trị Viện thẩm mỹ Chuẩn Y khoa trên nền tảng Odoo ERP</b></p>
  <br>

  [![Hướng dẫn tải và demo thao tác app Quản lý Viện thẩm mỹ HT Beauty](https://img.youtube.com/vi/AOqt3BUsX_c/maxresdefault.jpg)](https://youtu.be/AOqt3BUsX_c)
  
  <p><i>📺 Click vào ảnh để xem video Hướng dẫn tải và Demo hệ thống</i></p>
</div>

---

## 🌟 Tổng quan Dự án

HT Beauty Management System là bộ custom addons được phát triển trên nền tảng Odoo Open Source. Dự án tập trung số hóa luồng vận hành dịch vụ cốt lõi của phòng khám da liễu, quản lý tài nguyên lịch hẹn và tự động hóa quy trình chăm sóc khách hàng.

## 🚀 Tính năng Nổi bật

* **📅 Quản lý Lịch hẹn & Tài nguyên:** Tự động kiểm tra xung đột tài nguyên (Bác sĩ, Kỹ thuật viên, Phòng điều trị) để ngăn chặn xếp trùng lịch.
* **📋 Quản lý Phác đồ & Nhật ký điều trị:** Số hóa hồ sơ bệnh án, quản lý liệu trình đa buổi và tự động trừ lùi số buổi khi hoàn thành ca điều trị.
* **🤖 Tự động hóa CSKH:** Tiến trình chạy ngầm (cron jobs) nhắc lịch hẹn và phân bổ công việc cho bộ phận CSKH theo các mốc thời gian (sau 1 ngày, sau 3 ngày).
* **🎯 Quản lý Khách hàng (CRM):** Đồng bộ dữ liệu Lead từ các kênh, tự động lọc trùng và gộp hồ sơ liên hệ.

## 🛠 Nền tảng Công nghệ

* **Framework:** Odoo Community Phiên bản 19.0
* **Ngôn ngữ:** Python 3.10+
* **Cơ sở dữ liệu:** PostgreSQL
* **Giao diện:** QWeb, XML

## 🚀 Kích hoạt toàn bộ hệ thống chỉ với một thao tác

Dự án được cấu hình sẵn cơ chế **module dependency** trong Odoo, cho phép triển khai toàn bộ hệ thống thông qua một module quản lý tổng thể.

### Các bước thực hiện

1. Truy cập **Apps** trong Odoo.
2. Tìm kiếm module:

```text
ht_beauty_management
```

3. Nhấn **Activate** (hoặc **Install**).

### Kết quả

Sau khi kích hoạt, Odoo sẽ tự động:

- Biên dịch và tải các thành phần của hệ thống.
- Thiết lập cấu hình cơ sở dữ liệu cần thiết.
- Cài đặt đồng bộ toàn bộ các module phụ thuộc.

Các module được tự động triển khai bao gồm:

```text
ht_beauty_management
├── ht_beauty_core
├── ht_beauty_appointment
├── ht_beauty_treatment
├── ht_beauty_automation
└── ht_beauty_website
```

> ⚡ Không cần cài đặt thủ công từng module riêng lẻ.  
> Chỉ cần kích hoạt `ht_beauty_management`, toàn bộ hệ sinh thái quản lý spa sẽ được triển khai tự động.
