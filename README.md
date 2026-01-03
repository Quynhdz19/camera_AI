# SAR-BOT PRO - AI Camera System

Hệ thống camera AI nhận diện người sử dụng OpenCV với giao diện hiện đại.

## Tính năng

- 🎥 Kết nối camera EZVIZ qua RTSP stream hoặc webcam local
- 👤 Nhận diện người sử dụng HOG descriptor
- 🔄 Auto-reconnect khi mất kết nối RTSP
- 📊 Hiển thị thông số cảm biến (Gas, PM2.5)
- 📝 System logs theo thời gian thực
- 🎯 Giao diện HUD phong cách SAR-BOT

## Cấu hình EZVIZ Camera

### Cách 1: Tìm RTSP URL của camera EZVIZ

**Cách lấy thông tin RTSP từ camera EZVIZ:**

1. **Qua EZVIZ App:**
   - Mở app EZVIZ > Chọn camera > Settings > Advanced Settings
   - Tìm mục "Verification Code" (mã xác minh in trên camera)
   - Username mặc định thường là: `admin`
   - Password: verification code hoặc password bạn đã đặt

2. **RTSP URL Format:**
```
rtsp://username:password@ip_address:port/h264/ch01/main/av_stream
```

**Ví dụ:**
```
rtsp://admin:ABCDEF@192.168.1.100:554/h264/ch01/main/av_stream
```

### Cách 2: Cấu hình trong code

Mở file `app.py` và sửa dòng 17-22:

```python
# Thay đổi RTSP_URL với thông tin camera của bạn
RTSP_URL = "rtsp://admin:your_password@192.168.1.100:554/h264/ch01/main/av_stream"

# Đổi thành True để dùng RTSP, False để dùng webcam local
USE_RTSP = True
```

### Lưu ý EZVIZ Camera:

- Port mặc định: `554`
- Một số model EZVIZ dùng path: `/h264/ch01/sub/av_stream` (sub-stream chất lượng thấp hơn)
- Đảm bảo camera và máy tính cùng mạng LAN
- Bật RTSP trong cài đặt camera (nếu có)

## Cài đặt

### 1. Tạo môi trường ảo (khuyến nghị)

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# hoặc
.\venv\Scripts\activate  # Windows
```

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Chạy ứng dụng

```bash
python app.py
```

### 4. Truy cập giao diện

Mở trình duyệt và truy cập: **http://localhost:5000**

## Cấu trúc dự án

```
AI_camera/
├── app.py              # Flask backend + OpenCV
├── requirements.txt    # Python dependencies
├── README.md
├── templates/
│   └── index.html      # Giao diện chính
└── static/
    ├── style.css       # CSS styling
    └── script.js       # JavaScript frontend
```

## Phím tắt

- **F**: Bật/tắt chế độ toàn màn hình camera

## Yêu cầu hệ thống

- Python 3.8+
- Camera/Webcam
- Trình duyệt hiện đại (Chrome, Firefox, Safari)

## API Endpoints

| Endpoint | Mô tả |
|----------|-------|
| `/` | Trang chủ - Giao diện dashboard |
| `/video_feed` | Stream video từ camera |
| `/api/status` | Trạng thái hệ thống (JSON) |
| `/api/logs` | Logs hệ thống (JSON) |

## Các RTSP URL thường gặp với EZVIZ

| Stream Type | URL Path |
|-------------|----------|
| Main Stream (HD) | `/h264/ch01/main/av_stream` |
| Sub Stream (SD) | `/h264/ch01/sub/av_stream` |
| H.265 Main | `/h265/ch01/main/av_stream` |
| H.265 Sub | `/h265/ch01/sub/av_stream` |

**Ví dụ đầy đủ:**
```bash
# Main stream (chất lượng cao, tốn băng thông)
rtsp://admin:password123@192.168.1.100:554/h264/ch01/main/av_stream

# Sub stream (chất lượng thấp hơn, ít tốn băng thông - khuyến nghị cho AI)
rtsp://admin:password123@192.168.1.100:554/h264/ch01/sub/av_stream
```

## Troubleshooting

### Camera không kết nối được?

1. **Kiểm tra kết nối mạng:**
```bash
ping 192.168.1.100  # Thay bằng IP camera của bạn
```

2. **Test RTSP bằng VLC Media Player:**
   - Mở VLC > Media > Open Network Stream
   - Nhập RTSP URL
   - Nếu không xem được thì có vấn đề về URL/credentials

3. **Kiểm tra firewall:**
   - Port 554 có thể bị chặn
   - Tắt firewall tạm thời để test

4. **Bật RTSP trên camera:**
   - Một số camera EZVIZ cần bật RTSP trong settings
   - Truy cập web interface camera hoặc qua app

5. **Sử dụng Sub Stream:**
   - Nếu Main Stream bị lag, dùng Sub Stream
   - Thay `/main/` thành `/sub/` trong URL

## Ghi chú

- Ứng dụng sử dụng HOG (Histogram of Oriented Gradients) để nhận diện người
- Có thể thay thế bằng YOLO hoặc các model deep learning khác để tăng độ chính xác
- Dữ liệu cảm biến đang được mô phỏng, có thể kết nối với thiết bị thật qua Serial/MQTT
- RTSP stream có auto-reconnect khi mất kết nối
- Sub stream khuyến nghị hơn Main stream cho AI processing (ít lag hơn)


# camera_AI
