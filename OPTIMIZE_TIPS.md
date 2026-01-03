# Tối ưu Video Streaming - Khắc phục LAG/ĐƠ

## ✅ Đã áp dụng

### 1. **Dùng SUB STREAM thay vì MAIN STREAM**
```python
# app.py line 19
RTSP_URL = "rtsp://admin:EEZSQY@192.168.1.5:554/h264/ch01/sub/av_stream"
                                                              ^^^
```
- Sub stream: 480p/360p - ít tốn băng thông
- Main stream: 1080p/720p - tốn băng thông, dễ lag

### 2. **Giảm Buffer Size**
```python
camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Buffer tối thiểu
```
- Buffer = 1: Độ trễ thấp nhất
- Buffer > 1: Video mượt hơn nhưng trễ nhiều

### 3. **Skip Buffered Frames**
```python
camera.grab()  # Bỏ qua frames cũ trong buffer
camera.read()  # Lấy frame mới nhất
```

### 4. **Giảm FPS & JPEG Quality**
```python
time.sleep(0.05)  # 20 FPS thay vì 30 FPS
cv2.IMWRITE_JPEG_QUALITY, 70  # Quality 70% thay vì 85%
```

### 5. **Giảm tần suất Detection**
```python
if frame_count % 10 == 0:  # Detect mỗi 10 frames thay vì 5
    frame = detect_persons(frame)
```

### 6. **TCP Transport + No Buffer**
```python
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|fflags;nobuffer"
```

---

## 🔧 Nếu vẫn còn lag

### Option 1: Giảm resolution stream
Trong camera EZVIZ settings, đổi sub stream về:
- **360p** thay vì 480p
- **Bitrate**: 256 Kbps thay vì 512 Kbps

### Option 2: Giảm FPS trong code
```python
# app.py - trong generate_frames()
time.sleep(0.1)  # 10 FPS (chậm hơn nhưng ổn định)
```

### Option 3: Tắt Person Detection tạm thời
```python
# app.py - comment dòng 223-225
# if frame_count % 10 == 0 or (current_time - last_detection_time) > 2:
#     frame = detect_persons(frame)
#     last_detection_time = current_time
```

### Option 4: Dùng H.265 (nếu camera hỗ trợ)
```python
RTSP_URL = "rtsp://admin:EEZSQY@192.168.1.5:554/h265/ch01/sub/av_stream"
                                                    ^^^^
```
H.265 nén tốt hơn H.264 = ít bandwidth hơn

### Option 5: Kiểm tra mạng
```bash
# Test ping
ping 192.168.1.5

# Test bandwidth
iperf3 -c 192.168.1.5
```

---

## 📊 So sánh hiệu suất

| Setting | FPS | Bandwidth | Latency | CPU Usage |
|---------|-----|-----------|---------|-----------|
| Main + 30fps + Q85 | 30 | 2-4 Mbps | 2-3s | 60-80% |
| Sub + 30fps + Q85 | 30 | 512 Kbps | 1-2s | 40-60% |
| **Sub + 20fps + Q70** ⭐ | 20 | 256 Kbps | 0.5-1s | 30-40% |
| Sub + 10fps + Q60 | 10 | 128 Kbps | 0.3-0.5s | 20-30% |

⭐ **Khuyến nghị**: Sub + 20fps + Q70 (đang dùng)

---

## 🎯 Settings cho các trường hợp

### Mạng chậm (< 1 Mbps):
```python
RTSP_URL = "rtsp://...sub/av_stream"  # Sub stream
time.sleep(0.1)  # 10 FPS
cv2.IMWRITE_JPEG_QUALITY, 60  # Quality 60%
frame_count % 15 == 0  # Detect mỗi 15 frames
```

### Mạng nhanh (> 5 Mbps):
```python
RTSP_URL = "rtsp://...main/av_stream"  # Main stream
time.sleep(0.033)  # 30 FPS
cv2.IMWRITE_JPEG_QUALITY, 85  # Quality 85%
frame_count % 5 == 0  # Detect mỗi 5 frames
```

### Ưu tiên Detection:
```python
RTSP_URL = "rtsp://...main/av_stream"  # Main stream (chất lượng cao)
time.sleep(0.05)  # 20 FPS
frame_count % 3 == 0  # Detect thường xuyên hơn
```

### Ưu tiên Real-time:
```python
RTSP_URL = "rtsp://...sub/av_stream"  # Sub stream
time.sleep(0.066)  # 15 FPS
# Tắt detection hoặc detect rất ít
```

---

## 🐛 Debug Commands

### Test RTSP stream trực tiếp với FFmpeg:
```bash
ffmpeg -rtsp_transport tcp -i "rtsp://admin:EEZSQY@192.168.1.5:554/h264/ch01/sub/av_stream" -f null -

# Xem thông tin stream
ffprobe -rtsp_transport tcp "rtsp://admin:EEZSQY@192.168.1.5:554/h264/ch01/sub/av_stream"
```

### Test với VLC (recommended):
1. Open VLC Media Player
2. Media > Open Network Stream
3. Paste: `rtsp://admin:EEZSQY@192.168.1.5:554/h264/ch01/sub/av_stream`
4. Tools > Codec Information để xem stats

### Monitor network usage:
```bash
# macOS
nettop -p 5001

# Linux
iftop -i eth0
```

---

## 💡 Pro Tips

1. **Restart camera** mỗi vài ngày để clear buffer
2. **Wired connection** tốt hơn WiFi rất nhiều
3. **Router QoS**: Ưu tiên traffic cho IP camera
4. **Camera settings**: Tắt các tính năng không cần (motion detection, audio)
5. **Time of day**: Mạng ít người dùng = ít lag hơn

---

**Current Configuration**: Sub Stream + 20 FPS + Q70 + Detection/10 frames

