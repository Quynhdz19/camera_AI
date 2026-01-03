# Quick Start - SAR-BOT PRO

## 🚀 Khởi động nhanh với EZVIZ Camera

### 1. Cài đặt (đã hoàn tất)

```bash
cd /Users/quynhlx/Documents/AI_camera
source venv/bin/activate
```

### 2. Cấu hình EZVIZ Camera

Hiện tại camera của bạn đã được cấu hình:
- **IP**: 192.168.1.5
- **Username**: admin
- **Password**: EEZSQY (Verification Code)
- **RTSP URL**: `rtsp://admin:EEZSQY@192.168.1.5:554/h264/ch01/main/av_stream`

### 3. Chạy ứng dụng

```bash
python app.py
```

### 4. Truy cập giao diện

Mở trình duyệt: **http://localhost:5001**

---

## 📝 Thay đổi cấu hình

### Cách 1: Sửa file `app.py` (dòng 19)

```python
RTSP_URL = "rtsp://admin:EEZSQY@192.168.1.5:554/h264/ch01/main/av_stream"
```

### Cách 2: Sửa file `config.py`

```python
RTSP_CONFIG = {
    "username": "admin",
    "password": "EEZSQY",
    "ip_address": "192.168.1.5",
    "port": 554,
    "stream_path": "/h264/ch01/main/av_stream",  # hoặc /sub/ cho chất lượng thấp hơn
}
```

---

## 🔧 Troubleshooting

### Camera không kết nối?

**1. Kiểm tra kết nối mạng:**
```bash
ping 192.168.1.5
```

**2. Test RTSP bằng VLC:**
- Mở VLC Player
- Media > Open Network Stream
- Nhập: `rtsp://admin:EEZSQY@192.168.1.5:554/h264/ch01/main/av_stream`
- Nếu không xem được → kiểm tra IP/password/port

**3. Thử Sub Stream (ít lag hơn):**

Đổi trong `app.py` dòng 19:
```python
RTSP_URL = "rtsp://admin:EEZSQY@192.168.1.5:554/h264/ch01/sub/av_stream"
                                                              ^^^
```

**4. Kiểm tra firewall:**
```bash
# macOS
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# Tạm thời tắt để test
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off
```

**5. Thử port khác:**
Một số camera EZVIZ dùng port 8554:
```python
RTSP_URL = "rtsp://admin:EEZSQY@192.168.1.5:8554/h264/ch01/main/av_stream"
```

---

## 💡 Tips

### Giảm độ trễ (latency):
1. Dùng **sub stream** thay vì main stream
2. Giảm `RTSP_BUFFER_SIZE` trong `config.py`
3. Tăng `DETECTION_FREQUENCY` (detect ít hơn, nhanh hơn)

### Tăng độ chính xác nhận diện:
1. Dùng **main stream** (chất lượng cao)
2. Giảm `DETECTION_SCALE` (0.5 → 0.7)
3. Giảm `DETECTION_FREQUENCY` (5 → 3)

### Tắt nhận diện người (chỉ xem camera):
Trong `app.py`, comment dòng 224-225:
```python
# if frame_count % 5 == 0:
#     frame = detect_persons(frame)
```

---

## 🎯 Các stream paths EZVIZ thường gặp

| Stream | Path | Độ phân giải | Bandwidth |
|--------|------|--------------|-----------|
| Main H.264 | `/h264/ch01/main/av_stream` | 1080p/720p | Cao |
| Sub H.264 | `/h264/ch01/sub/av_stream` | 480p/360p | Thấp ⭐ |
| Main H.265 | `/h265/ch01/main/av_stream` | 1080p/720p | Trung bình |
| Sub H.265 | `/h265/ch01/sub/av_stream` | 480p/360p | Rất thấp |

⭐ **Khuyến nghị**: Dùng Sub H.264 cho AI processing (ít lag, đủ chất lượng)

---

## ❓ FAQ

**Q: Camera bị disconnect sau vài phút?**
A: Tăng timeout trong `config.py`:
```python
RTSP_OPEN_TIMEOUT = 30000  # 30 giây
RTSP_READ_TIMEOUT = 30000
```

**Q: Video bị giật lag?**
A: Dùng sub stream hoặc tăng `VIDEO_FPS` trong `config.py`

**Q: Muốn dùng webcam laptop thay vì EZVIZ?**
A: Đổi `USE_RTSP = False` trong `app.py` dòng 22

**Q: Port 5001 bị chiếm?**
A: Đổi port trong `app.py` dòng 285:
```python
app.run(host='0.0.0.0', port=5002, debug=True, threaded=True)
```

---

## 📱 Lấy Verification Code từ camera EZVIZ

1. Mở app **EZVIZ** trên điện thoại
2. Chọn camera > ⚙️ Settings
3. **Device Information** > **Verification Code**
4. Code có dạng: `ABCDEF` (6 ký tự)
5. Password RTSP = Verification Code này

---

**Chúc bạn sử dụng vui vẻ! 🎉**

