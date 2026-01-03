"""
SAR-BOT PRO - ULTRA LIGHT MODE
Tối ưu tối đa cho đường truyền chậm + Nhận diện người rõ ràng
"""

from flask import Flask, render_template, Response, jsonify
import cv2
import numpy as np
from datetime import datetime
import threading
import time
import random
from queue import Queue

app = Flask(__name__)

# EZVIZ RTSP Configuration
RTSP_URL = "rtsp://admin:EEZSQY@192.168.1.5:554/h264/ch01/sub/av_stream"
USE_RTSP = True

# ULTRA LIGHT Settings - Tối ưu cho đường truyền chậm
STREAM_WIDTH = 480      # Giảm xuống 480px
STREAM_HEIGHT = 270     # Giảm xuống 270px
DETECTION_INTERVAL = 2  # Detect mỗi 2 giây
JPEG_QUALITY = 55       # Quality thấp
TARGET_FPS = 12         # 12 FPS thay vì 15

# Global variables
camera = None
camera_lock = threading.Lock()
system_logs = []
detected_persons = 0
detection_boxes = []
last_detection_time = 0
is_recording = False
camera_reconnect_attempts = 0
detection_active = False  # Flag để hiển thị detection status

# Sensor data
sensor_data = {
    "gas_level": 77,
    "dust_pm25": 18,
    "temperature": 24.5,
    "co_level": 8,
    "signal_strength": 95,
    "battery_level": 84
}

# Initialize HOG descriptor
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# Frame queue for detection
detection_queue = Queue(maxsize=1)

def add_log(message):
    """Add a new log entry"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    system_logs.insert(0, {"time": timestamp, "message": message})
    if len(system_logs) > 50:
        system_logs.pop()

def init_camera():
    """Initialize camera"""
    global camera, camera_reconnect_attempts
    with camera_lock:
        if camera is None:
            try:
                if USE_RTSP:
                    add_log("🔌 Đang kết nối EZVIZ camera...")
                    
                    import os
                    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = (
                        "rtsp_transport;tcp|"
                        "fflags;nobuffer|"
                        "flags;low_delay|"
                        "framedrop;1|"
                        "max_delay;0"
                    )
                    
                    camera = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
                    
                    # Ultra low latency
                    camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    camera.set(cv2.CAP_PROP_FPS, TARGET_FPS)
                    camera.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)
                    camera.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 5000)
                else:
                    add_log("🔌 Đang kết nối webcam local...")
                    camera = cv2.VideoCapture(0)
                    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
                
                if camera.isOpened():
                    add_log("✅ Camera đã kết nối - ULTRA LIGHT MODE")
                    add_log(f"📹 Stream: {STREAM_WIDTH}x{STREAM_HEIGHT} @ {TARGET_FPS}fps")
                    camera_reconnect_attempts = 0
                else:
                    add_log("❌ LỖI: Không thể kết nối camera")
                    camera = None
                    
            except Exception as e:
                add_log(f"❌ LỖI: {str(e)}")
                camera = None

def detect_persons_async(frame_small):
    """Detect persons - optimized & sensitive"""
    global detected_persons, detection_boxes, detection_active
    
    detection_active = True
    
    try:
        # HOG detection với settings NHẠY HƠN để dễ phát hiện người
        boxes, weights = hog.detectMultiScale(
            frame_small,
            winStride=(8, 8),      # Giảm từ 16 xuống 8 = nhạy hơn
            padding=(8, 8),
            scale=1.05,            # Giảm từ 1.15 xuống 1.05 = nhiều scale hơn
            hitThreshold=0,        # Giảm từ 0.5 xuống 0 = nhạy nhất
            finalThreshold=1.0     # Giảm từ 2.0 xuống 1.0 = dễ detect hơn
        )
        
        detected_persons = len(boxes)
        detection_boxes = [(box, weight) for box, weight in zip(boxes, weights)]
        
        if detected_persons > 0:
            add_log(f"👤 AI VISION: PHÁT HIỆN {detected_persons} NGƯỜI!")
            print(f"[DEBUG] Detected {detected_persons} persons with boxes: {boxes}")
        else:
            print(f"[DEBUG] No person detected in this frame")
            
    except Exception as e:
        print(f"Detection error: {e}")
    finally:
        detection_active = False

def detection_thread():
    """Background thread for person detection"""
    global last_detection_time
    
    add_log("🤖 AI Detection thread started")
    
    while True:
        try:
            if not detection_queue.empty():
                frame_small = detection_queue.get()
                detect_persons_async(frame_small)
                last_detection_time = time.time()
            time.sleep(0.1)
        except Exception as e:
            print(f"Detection thread error: {e}")
            time.sleep(1)

def draw_detections(frame, scale_x, scale_y):
    """Draw detection boxes - MÀU XANH LÁ NEON CỰC RÕ"""
    print(f"[DRAW] Drawing {len(detection_boxes)} detection boxes")
    
    for idx, ((x, y, w, h), weight) in enumerate(detection_boxes):
        # Scale to display size
        x, y, w, h = int(x * scale_x), int(y * scale_y), int(w * scale_x), int(h * scale_y)
        
        print(f"[DRAW] Person #{idx+1} at ({x},{y}) size ({w}x{h})")
        
        # KHUNG CHÍNH - MÀU XANH LÁ NEON CỰC RÕ
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 4)  # GREEN, thickness 4
        
        # KHUNG PHỤ BÊN TRONG - MÀU VÀNG
        cv2.rectangle(frame, (x+2, y+2), (x + w-2, y + h-2), (0, 255, 255), 2)  # YELLOW
        
        # VẼ GÓC - MÀU ĐỎ NEON
        corner_len = 25
        corner_color = (0, 0, 255)  # RED
        thickness = 5
        
        # Top-left
        cv2.line(frame, (x, y), (x + corner_len, y), corner_color, thickness)
        cv2.line(frame, (x, y), (x, y + corner_len), corner_color, thickness)
        # Top-right
        cv2.line(frame, (x + w, y), (x + w - corner_len, y), corner_color, thickness)
        cv2.line(frame, (x + w, y), (x + w, y + corner_len), corner_color, thickness)
        # Bottom-left
        cv2.line(frame, (x, y + h), (x + corner_len, y + h), corner_color, thickness)
        cv2.line(frame, (x, y + h), (x, y + h - corner_len), corner_color, thickness)
        # Bottom-right
        cv2.line(frame, (x + w, y + h), (x + w - corner_len, y + h), corner_color, thickness)
        cv2.line(frame, (x + w, y + h), (x + w, y + h - corner_len), corner_color, thickness)
        
        # LABEL LỚN với background VÀNG
        label = f"PERSON #{idx+1}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.0  # Tăng size
        font_thickness = 3
        label_size = cv2.getTextSize(label, font, font_scale, font_thickness)[0]
        
        # Background VÀNG NEON
        label_x = max(x, 0)
        label_y = max(y - label_size[1] - 15, label_size[1] + 10)
        cv2.rectangle(frame, 
                     (label_x, label_y - label_size[1] - 10), 
                     (label_x + label_size[0] + 10, label_y + 5), 
                     (0, 255, 255), -1)  # YELLOW background
        
        # Text ĐEN ĐẬM
        cv2.putText(frame, label, (label_x + 5, label_y), 
                    font, font_scale, (0, 0, 0), font_thickness)
    
    return frame

def draw_overlay(frame):
    """Draw overlay với detection counter"""
    h, w = frame.shape[:2]
    
    # Detection counter ở góc trái trên
    if detected_persons > 0:
        counter_text = f"DETECTED: {detected_persons} PERSON(S)"
        text_size = cv2.getTextSize(counter_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
        
        # Background
        cv2.rectangle(frame, (10, 10), (20 + text_size[0], 40 + text_size[1]), (0, 255, 0), -1)
        cv2.putText(frame, counter_text, (15, 35), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    
    # Detection status indicator
    if detection_active:
        cv2.circle(frame, (w - 30, 30), 10, (0, 255, 0), -1)  # Green = detecting
        cv2.putText(frame, "AI", (w - 45, 37), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Simple crosshair
    cx, cy = w // 2, h // 2
    color = (0, 255, 255)
    cv2.circle(frame, (cx, cy), 25, color, 1)
    cv2.circle(frame, (cx, cy), 3, color, -1)
    
    # Lines
    gap = 8
    length = 15
    cv2.line(frame, (cx - gap - length, cy), (cx - gap, cy), color, 1)
    cv2.line(frame, (cx + gap, cy), (cx + gap + length, cy), color, 1)
    cv2.line(frame, (cx, cy - gap - length), (cx, cy - gap), color, 1)
    cv2.line(frame, (cx, cy + gap), (cx, cy + gap + length), color, 1)
    
    return frame

def reconnect_camera():
    """Reconnect camera"""
    global camera, camera_reconnect_attempts
    
    with camera_lock:
        if camera is not None:
            camera.release()
            camera = None
        
        camera_reconnect_attempts += 1
        add_log(f"🔄 Thử kết nối lại... (lần {camera_reconnect_attempts})")
        
    time.sleep(2)
    init_camera()

def generate_frames():
    """Generate video frames - ULTRA OPTIMIZED"""
    global camera, camera_reconnect_attempts, last_detection_time
    init_camera()
    
    frame_count = 0
    failed_reads = 0
    max_failed_reads = 15
    
    # Detection scale (rất nhỏ để nhanh)
    detection_width = 240
    detection_height = 135
    
    add_log("🎬 Video stream started")
    
    while True:
        with camera_lock:
            if camera is None or not camera.isOpened():
                if camera_reconnect_attempts < 5:
                    reconnect_camera()
                time.sleep(1)
                continue
            
            # Skip nhiều buffered frames để giảm lag
            if USE_RTSP:
                for _ in range(3):  # Skip 3 frames
                    camera.grab()
            
            success, frame = camera.read()
        
        if not success:
            failed_reads += 1
            if failed_reads >= max_failed_reads:
                add_log("⚠️ Mất kết nối. Đang kết nối lại...")
                reconnect_camera()
                failed_reads = 0
            time.sleep(0.1)
            continue
        
        failed_reads = 0
        frame_count += 1
        
        # Resize frame for streaming (critical!)
        frame_display = cv2.resize(frame, (STREAM_WIDTH, STREAM_HEIGHT), 
                                   interpolation=cv2.INTER_LINEAR)
        
        # Send frame to detection thread
        current_time = time.time()
        if (current_time - last_detection_time) >= DETECTION_INTERVAL:
            if detection_queue.empty():
                frame_detect = cv2.resize(frame, (detection_width, detection_height))
                try:
                    detection_queue.put_nowait(frame_detect)
                except:
                    pass
        
        # Draw detection boxes - LUÔN LUÔN vẽ nếu có
        if len(detection_boxes) > 0:
            scale_x = STREAM_WIDTH / detection_width
            scale_y = STREAM_HEIGHT / detection_height
            frame_display = draw_detections(frame_display, scale_x, scale_y)
            print(f"[DEBUG] Drawing {len(detection_boxes)} boxes on frame")
        
        # Draw overlay
        frame_display = draw_overlay(frame_display)
        
        # Encode with low quality
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY]
        ret, buffer = cv2.imencode('.jpg', frame_display, encode_param)
        
        if not ret:
            continue
            
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        # 12 FPS
        time.sleep(1.0 / TARGET_FPS)

def update_sensors():
    """Background thread to simulate sensor updates"""
    while True:
        sensor_data["gas_level"] = max(0, min(100, sensor_data["gas_level"] + random.randint(-2, 2)))
        sensor_data["dust_pm25"] = max(0, min(100, sensor_data["dust_pm25"] + random.randint(-1, 1)))
        sensor_data["temperature"] = max(20, min(35, sensor_data["temperature"] + random.uniform(-0.5, 0.5)))
        sensor_data["co_level"] = max(0, min(50, sensor_data["co_level"] + random.randint(-2, 2)))
        sensor_data["battery_level"] = max(0, sensor_data["battery_level"] - random.random() * 0.1)
        time.sleep(2)

# Routes
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/status')
def get_status():
    """Get system status"""
    return jsonify({
        "sensor_data": sensor_data,
        "detected_persons": detected_persons,
        "is_recording": is_recording,
        "system_online": True
    })

@app.route('/api/logs')
def get_logs():
    """Get system logs"""
    return jsonify({"logs": system_logs[:20]})

if __name__ == '__main__':
    print("\n" + "="*70)
    print("  🚀 SAR-BOT PRO - ULTRA LIGHT MODE")
    print("="*70)
    print(f"  📹 Stream Resolution: {STREAM_WIDTH}x{STREAM_HEIGHT}")
    print(f"  🎯 Target FPS: {TARGET_FPS}")
    print(f"  🔍 Person Detection: Every {DETECTION_INTERVAL} seconds")
    print(f"  📊 JPEG Quality: {JPEG_QUALITY}%")
    print(f"  ⚡ Optimized for: SLOW NETWORK")
    print("="*70)
    print("  👤 Person detection: ✅ ENABLED")
    print("  🎨 Visual indicators: ✅ ENABLED")
    print("="*70 + "\n")
    
    # Add initial log
    add_log("🚀 Hệ thống khởi động - ULTRA LIGHT MODE")
    add_log("👤 AI Nhận diện người: ENABLED")
    
    # Start detection thread
    detection_worker = threading.Thread(target=detection_thread, daemon=True)
    detection_worker.start()
    
    # Start sensor update thread
    sensor_thread = threading.Thread(target=update_sensors, daemon=True)
    sensor_thread.start()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)

