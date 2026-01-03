# Hướng dẫn Tuning - Điều chỉnh theo nhu cầu

## 🎛️ Quick Settings - Chỉnh trong app.py

### Vị trí các settings chính:
```python
# Line 18: RTSP URL
RTSP_URL = "rtsp://admin:EEZSQY@192.168.1.5:554/h264/ch01/sub/av_stream"

# Line 24-27: Optimization settings
STREAM_WIDTH = 640      # Độ rộng video hiển thị
STREAM_HEIGHT = 360     # Độ cao video hiển thị
DETECTION_INTERVAL = 3  # Detect mỗi bao nhiêu giây
JPEG_QUALITY = 65       # Chất lượng ảnh (0-100)
```

---

## 🎯 Preset Configurations

### Preset 1: Ultra Smooth (Mạng chậm < 500 Kbps)
```python
STREAM_WIDTH = 480
STREAM_HEIGHT = 270
DETECTION_INTERVAL = 5  # Detect mỗi 5 giây
JPEG_QUALITY = 55
time.sleep(0.1)  # Line 315: 10 FPS
```
**Kết quả:** Cực mượt, chất lượng thấp

---

### Preset 2: Balanced (Default - Đang dùng)
```python
STREAM_WIDTH = 640
STREAM_HEIGHT = 360
DETECTION_INTERVAL = 3
JPEG_QUALITY = 65
time.sleep(0.066)  # 15 FPS
```
**Kết quả:** Cân bằng tốt, khuyến nghị ⭐

---

### Preset 3: High Quality (Mạng nhanh > 3 Mbps)
```python
STREAM_WIDTH = 960
STREAM_HEIGHT = 540
DETECTION_INTERVAL = 2
JPEG_QUALITY = 75
time.sleep(0.05)  # 20 FPS
```
**Kết quả:** Chất lượng cao, cần mạng tốt

---

### Preset 4: Max Detection (Ưu tiên nhận diện)
```python
STREAM_WIDTH = 640
STREAM_HEIGHT = 360
DETECTION_INTERVAL = 1  # Detect mỗi giây
JPEG_QUALITY = 70
time.sleep(0.066)  # 15 FPS
```
**Kết quả:** Detection nhanh, CPU tăng 15%

---

### Preset 5: Minimum Latency (Độ trễ thấp nhất)
```python
STREAM_WIDTH = 320
STREAM_HEIGHT = 180
DETECTION_INTERVAL = 10  # Tắt detection gần như
JPEG_QUALITY = 50
time.sleep(0.1)  # 10 FPS

# Line 245: Tăng skip frames
for _ in range(3):  # Skip 3 frames thay vì 2
    camera.grab()
```
**Kết quả:** Latency < 0.3s, chất lượng rất thấp

---

## 🔧 Tuning Individual Settings

### 1. Resolution (STREAM_WIDTH, STREAM_HEIGHT)

**Ảnh hưởng:** Bandwidth, CPU, Chất lượng hình ảnh

| Resolution | Bandwidth | CPU | Quality | Recommended |
|------------|-----------|-----|---------|-------------|
| 320x180 | ~100 Kbps | 10% | ⭐ | Mạng cực chậm |
| 480x270 | ~200 Kbps | 15% | ⭐⭐ | Mạng chậm |
| **640x360** | ~300 Kbps | 25% | ⭐⭐⭐ | **Default** ⭐ |
| 800x450 | ~500 Kbps | 35% | ⭐⭐⭐⭐ | Mạng ổn |
| 960x540 | ~800 Kbps | 45% | ⭐⭐⭐⭐⭐ | Mạng tốt |
| 1280x720 | ~1.5 Mbps | 60% | ⭐⭐⭐⭐⭐ | Mạng rất tốt |

**Cách chỉnh:**
```python
# Line 24-25
STREAM_WIDTH = 960   # Thay đổi ở đây
STREAM_HEIGHT = 540  # Thay đổi ở đây
```

---

### 2. JPEG Quality (JPEG_QUALITY)

**Ảnh hưởng:** Bandwidth, Chất lượng hình ảnh

| Quality | Bandwidth | Visual Quality | Note |
|---------|-----------|----------------|------|
| 40-50 | Thấp | ⭐ | Chỉ khi mạng cực chậm |
| 55-60 | Trung bình | ⭐⭐ | Tốt cho sub stream |
| **65-70** | Vừa | ⭐⭐⭐ | **Sweet spot** ⭐ |
| 75-80 | Cao | ⭐⭐⭐⭐ | Cho mạng tốt |
| 85-95 | Rất cao | ⭐⭐⭐⭐⭐ | Overkill, không cần |

**Cách chỉnh:**
```python
# Line 27
JPEG_QUALITY = 70  # Thay đổi ở đây (40-95)
```

---

### 3. Detection Interval (DETECTION_INTERVAL)

**Ảnh hưởng:** CPU, Tần suất nhận diện

| Interval | CPU Usage | Detection Speed | Use Case |
|----------|-----------|-----------------|----------|
| 1 giây | 40-50% | Rất nhanh | Người di chuyển nhanh |
| 2 giây | 30-40% | Nhanh | Cân bằng tốt |
| **3 giây** | 25-35% | Vừa | **Default** ⭐ |
| 5 giây | 20-25% | Chậm | Người ít di chuyển |
| 10 giây | 15-20% | Rất chậm | Chỉ để monitor |

**Cách chỉnh:**
```python
# Line 26
DETECTION_INTERVAL = 2  # Thay đổi ở đây (1-10 giây)
```

---

### 4. FPS (Frame Per Second)

**Ảnh hưởng:** Bandwidth, Độ mượt

| FPS | Sleep Time | Bandwidth | Smoothness | Note |
|-----|------------|-----------|------------|------|
| 10 | 0.1 | Thấp | ⭐⭐ | Hơi giật |
| **15** | 0.066 | Vừa | ⭐⭐⭐ | **Default** ⭐ |
| 20 | 0.05 | Cao | ⭐⭐⭐⭐ | Mượt |
| 25 | 0.04 | Rất cao | ⭐⭐⭐⭐⭐ | Rất mượt |
| 30 | 0.033 | Cực cao | ⭐⭐⭐⭐⭐ | Overkill |

**Cách chỉnh:**
```python
# Line 315 (trong generate_frames)
time.sleep(0.05)  # 20 FPS
# hoặc
time.sleep(0.033)  # 30 FPS
# hoặc
time.sleep(0.1)  # 10 FPS
```

**Công thức:** `sleep_time = 1 / desired_fps`

---

### 5. Frame Skipping

**Ảnh hưởng:** Latency

| Skip Frames | Latency | Tradeoff |
|-------------|---------|----------|
| 0 (none) | 2-3s | Nhiều lag |
| 1 | 1-2s | Vẫn hơi lag |
| **2** | 0.5-1s | **Balanced** ⭐ |
| 3 | 0.3-0.5s | Có thể miss frames |
| 5 | < 0.3s | Rất nhiều miss frames |

**Cách chỉnh:**
```python
# Line 245 (trong generate_frames)
for _ in range(2):  # Thay 2 bằng 0, 1, 3, hoặc 5
    camera.grab()
```

---

## 🎨 Overlay Effects

### Tắt/Bật Effects

**Tắt Crosshair:**
```python
# Line 303: Comment dòng này
# frame_display = draw_simple_overlay(frame_display)
```

**Tắt Detection Boxes:**
```python
# Line 298-301: Comment block này
# if detection_boxes:
#     scale_x = STREAM_WIDTH / detection_width
#     scale_y = STREAM_HEIGHT / detection_height
#     frame_display = draw_detections(frame_display, scale_x, scale_y)
```

**Tắt hoàn toàn Detection (chỉ xem camera):**
```python
# Line 282-289: Comment block này
# current_time = time.time()
# if (current_time - last_detection_time) >= DETECTION_INTERVAL:
#     if detection_queue.empty():
#         frame_detect = cv2.resize(frame, (detection_width, detection_height))
#         try:
#             detection_queue.put_nowait(frame_detect)
#         except:
#             pass
```

---

## 🌐 Network Optimization

### Test Network Speed
```bash
# Test ping
ping 192.168.1.5

# Test bandwidth (cần iperf3 cài trên camera)
iperf3 -c 192.168.1.5 -t 10
```

### Router QoS Settings
1. Login router admin (thường 192.168.1.1)
2. Tìm **QoS** hoặc **Traffic Priority**
3. Add rule:
   - Device IP: `192.168.1.5` (camera)
   - Priority: **High**
   - Bandwidth: Reserve 1 Mbps

### WiFi Optimization
- Dùng **5GHz** thay vì 2.4GHz
- Đặt camera gần router
- Tránh vật cản (tường, tủ)
- Ưu tiên: **Ethernet cable** > WiFi

---

## 📊 Monitoring Performance

### Check CPU Usage
```bash
# Terminal 1: Run app
python app.py

# Terminal 2: Monitor CPU
top -pid $(pgrep -f "python app.py")
```

### Check Network Usage
```bash
# macOS
nettop -p 5001

# Linux
iftop -i eth0
```

### Check Latency
```bash
# Test RTSP latency
ffmpeg -rtsp_transport tcp \
  -i "rtsp://admin:EEZSQY@192.168.1.5:554/h264/ch01/sub/av_stream" \
  -f null - \
  2>&1 | grep "speed="
```

### Browser DevTools
1. F12 > Network tab
2. Filter: `video_feed`
3. Check:
   - Transfer size
   - Time (should be < 200ms per frame)

---

## 🔄 Quick Restart

### Method 1: Kill & Restart
```bash
pkill -f "python app.py"
cd /Users/quynhlx/Documents/AI_camera
source venv/bin/activate
python app.py
```

### Method 2: Systemd Service (Linux)
```bash
sudo systemctl restart sarbot
```

### Method 3: Auto-restart on crash
```python
# Run với auto-restart
while true; do
    python app.py
    echo "Crashed! Restarting in 3s..."
    sleep 3
done
```

---

## 🎓 Advanced Tuning

### 1. Thay đổi Detection Algorithm

**Hiện tại:** HOG (nhanh, ít chính xác)

**Option A: Faster (trade accuracy)**
```python
# Line 175-182: Tăng stride và scale
boxes, weights = hog.detectMultiScale(
    frame_small,
    winStride=(32, 32),  # 16 → 32 (nhanh gấp đôi)
    padding=(8, 8),
    scale=1.2,           # 1.1 → 1.2
    hitThreshold=0.7,    # 0.5 → 0.7 (ít detection hơn)
    finalThreshold=2.5   # 2.0 → 2.5
)
```

**Option B: More Accurate (slower)**
```python
boxes, weights = hog.detectMultiScale(
    frame_small,
    winStride=(8, 8),    # 16 → 8 (chậm hơn 4x)
    padding=(4, 4),
    scale=1.05,          # 1.1 → 1.05 (nhiều levels)
    hitThreshold=0.3,    # 0.5 → 0.3 (nhạy hơn)
    finalThreshold=1.5
)
```

### 2. Multi-threaded Detection
```python
# Thay đổi detection_width/height tùy CPU
detection_width = 320   # 320 → 256 hoặc 384
detection_height = 180  # 180 → 144 hoặc 216
```

### 3. Custom FFmpeg Options
```python
# Line 64: Thêm options
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = (
    "rtsp_transport;tcp|"
    "fflags;nobuffer|"
    "flags;low_delay|"
    "framedrop;1|"
    "stimeout;5000000"  # Thêm: Socket timeout
)
```

---

## 💾 Save/Load Presets

### Create Preset File
```python
# presets.py
PRESETS = {
    "ultra_smooth": {
        "width": 480,
        "height": 270,
        "quality": 55,
        "detect_interval": 5,
        "fps": 10
    },
    "balanced": {
        "width": 640,
        "height": 360,
        "quality": 65,
        "detect_interval": 3,
        "fps": 15
    },
    "high_quality": {
        "width": 960,
        "height": 540,
        "quality": 75,
        "detect_interval": 2,
        "fps": 20
    }
}
```

### Load Preset
```python
# app.py - top
from presets import PRESETS

preset = PRESETS["balanced"]  # Chọn preset
STREAM_WIDTH = preset["width"]
STREAM_HEIGHT = preset["height"]
JPEG_QUALITY = preset["quality"]
DETECTION_INTERVAL = preset["detect_interval"]
```

---

## ❓ FAQ

**Q: Làm sao biết setting nào phù hợp?**
A: Test từng preset, chọn cái mượt nhất với quality chấp nhận được.

**Q: CPU > 60% có sao không?**
A: Tốt nhất < 50%. Nếu > 60%, giảm resolution hoặc tăng detection interval.

**Q: Bandwidth tối thiểu cần bao nhiêu?**
A: 
- Minimum: 200 Kbps (480p, Q55)
- Recommended: 500 Kbps (640p, Q65)
- Optimal: 1 Mbps+ (960p, Q75)

**Q: Tắt detection có làm mượt hơn không?**
A: Có! Detection tốn 10-20% CPU. Tắt = mượt hơn + CPU thấp hơn.

**Q: Main stream vs Sub stream?**
A:
- Main: 1080p/720p, 2-4 Mbps, LAG nếu mạng chậm
- **Sub: 480p/360p, 256-512 Kbps, SMOOTH** ⭐

**Q: H.264 vs H.265?**
A: 
- H.264: Compatible, mọi thiết bị đều hỗ trợ ⭐
- H.265: Ít bandwidth hơn 30%, nhưng không phải camera nào cũng có

---

**Happy Tuning! 🎛️**

