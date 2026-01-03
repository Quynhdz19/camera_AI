"""
SAR-BOT PRO - AI Camera System
Hệ thống camera AI nhận diện người sử dụng OpenCV
"""

from flask import Flask, render_template, Response, jsonify
import cv2
import numpy as np
from datetime import datetime
import threading
import time
import random

app = Flask(__name__)

# EZVIZ RTSP Configuration
# Dùng SUB STREAM để giảm lag (thay /main/ bằng /sub/)
RTSP_URL = "rtsp://admin:EEZSQY@192.168.1.5:554/h264/ch01/sub/av_stream"

# Nếu không có RTSP, fallback về webcam local
USE_RTSP = True  # Đổi thành False để dùng webcam local

# Global variables
camera = None
camera_lock = threading.Lock()
system_logs = []
detected_persons = 0
is_recording = False
camera_reconnect_attempts = 0

# Sensor data (simulated)
sensor_data = {
    "gas_level": 77,
    "dust_pm25": 18,
    "temperature": 24.5,  # Nhiệt độ (°C)
    "co_level": 8,  # Nồng độ CO (ppm)
    "signal_strength": 95,
    "battery_level": 84
}

# Initialize HOG descriptor for person detection
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

def add_log(message):
    """Add a new log entry"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    system_logs.insert(0, {"time": timestamp, "message": message})
    if len(system_logs) > 50:
        system_logs.pop()

def init_camera():
    """Initialize camera - RTSP or Local Webcam"""
    global camera, camera_reconnect_attempts
    with camera_lock:
        if camera is None:
            try:
                if USE_RTSP:
                    # Kết nối EZVIZ camera qua RTSP (SUB STREAM để giảm lag)
                    add_log("Đang kết nối EZVIZ camera...")
                    
                    # Sử dụng environment variable OPENCV_FFMPEG_CAPTURE_OPTIONS để giảm latency
                    import os
                    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|fflags;nobuffer"
                    
                    camera = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
                    
                    # Tối ưu để giảm độ trễ
                    camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Buffer tối thiểu
                    camera.set(cv2.CAP_PROP_FPS, 15)  # Giảm FPS để ổn định hơn
                    
                    # Set timeout ngắn hơn
                    camera.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)
                    camera.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 5000)
                else:
                    # Fallback: Webcam local
                    add_log("Đang kết nối webcam local...")
                    camera = cv2.VideoCapture(0)
                    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                
                # Kiểm tra kết nối
                if camera.isOpened():
                    add_log("✓ Camera đã kết nối thành công.")
                    if USE_RTSP:
                        add_log(f"RTSP Stream: {RTSP_URL.split('@')[1] if '@' in RTSP_URL else RTSP_URL}")
                    camera_reconnect_attempts = 0
                else:
                    add_log("✗ LỖI: Không thể kết nối camera.")
                    camera = None
                    
            except Exception as e:
                add_log(f"✗ LỖI kết nối camera: {str(e)}")
                camera = None

def detect_persons(frame):
    """Detect persons in frame using HOG descriptor"""
    global detected_persons
    
    # Resize for faster detection
    scale = 0.5
    small_frame = cv2.resize(frame, None, fx=scale, fy=scale)
    
    # Detect persons
    boxes, weights = hog.detectMultiScale(
        small_frame,
        winStride=(8, 8),
        padding=(4, 4),
        scale=1.05
    )
    
    detected_persons = len(boxes)
    
    # Draw detection boxes
    for (x, y, w, h) in boxes:
        # Scale back to original size
        x, y, w, h = int(x/scale), int(y/scale), int(w/scale), int(h/scale)
        
        # Draw bounding box with cyan color
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 2)
        
        # Draw corner accents
        corner_len = 20
        thickness = 3
        color = (0, 255, 255)  # Cyan
        
        # Top-left
        cv2.line(frame, (x, y), (x + corner_len, y), color, thickness)
        cv2.line(frame, (x, y), (x, y + corner_len), color, thickness)
        # Top-right
        cv2.line(frame, (x + w, y), (x + w - corner_len, y), color, thickness)
        cv2.line(frame, (x + w, y), (x + w, y + corner_len), color, thickness)
        # Bottom-left
        cv2.line(frame, (x, y + h), (x + corner_len, y + h), color, thickness)
        cv2.line(frame, (x, y + h), (x, y + h - corner_len), color, thickness)
        # Bottom-right
        cv2.line(frame, (x + w, y + h), (x + w - corner_len, y + h), color, thickness)
        cv2.line(frame, (x + w, y + h), (x + w, y + h - corner_len), color, thickness)
        
        # Label
        label = f"PERSON [{weights[list(boxes).index((x*scale, y*scale, w*scale, h*scale))]:.1%}]" if len(weights) > 0 else "PERSON"
        cv2.putText(frame, "PERSON DETECTED", (x, y - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    
    if detected_persons > 0:
        add_log(f"AI VISION: PHÁT HIỆN {detected_persons} NGƯỜI")
    
    return frame

def draw_crosshair(frame):
    """Draw targeting crosshair in center"""
    h, w = frame.shape[:2]
    cx, cy = w // 2, h // 2
    
    color = (255, 255, 0)  # Cyan in BGR
    
    # Outer circle
    cv2.circle(frame, (cx, cy), 40, color, 1)
    cv2.circle(frame, (cx, cy), 5, color, -1)
    
    # Cross lines
    gap = 15
    line_len = 25
    cv2.line(frame, (cx - gap - line_len, cy), (cx - gap, cy), color, 2)
    cv2.line(frame, (cx + gap, cy), (cx + gap + line_len, cy), color, 2)
    cv2.line(frame, (cx, cy - gap - line_len), (cx, cy - gap), color, 2)
    cv2.line(frame, (cx, cy + gap), (cx, cy + gap + line_len), color, 2)
    
    return frame

def draw_scan_line(frame, offset):
    """Draw scanning line effect"""
    h, w = frame.shape[:2]
    y = int((offset % 100) / 100 * h)
    
    # Create gradient scan line
    overlay = frame.copy()
    cv2.line(overlay, (0, y), (w, y), (0, 255, 255), 2)
    cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
    
    return frame

def reconnect_camera():
    """Reconnect camera if connection lost"""
    global camera, camera_reconnect_attempts
    
    with camera_lock:
        if camera is not None:
            camera.release()
            camera = None
        
        camera_reconnect_attempts += 1
        add_log(f"Đang thử kết nối lại camera... (lần {camera_reconnect_attempts})")
        
    time.sleep(2)  # Wait before reconnecting
    init_camera()

def generate_frames():
    """Generate video frames for streaming with auto-reconnect"""
    global camera, camera_reconnect_attempts
    init_camera()
    
    frame_count = 0
    failed_reads = 0
    max_failed_reads = 10  # Reconnect after 10 failed reads
    last_detection_time = time.time()
    
    while True:
        with camera_lock:
            if camera is None or not camera.isOpened():
                if camera_reconnect_attempts < 5:  # Max 5 reconnection attempts
                    reconnect_camera()
                time.sleep(1)
                continue
            
            # Skip buffered frames để lấy frame mới nhất (giảm lag)
            if USE_RTSP:
                camera.grab()  # Skip old frames
            
            success, frame = camera.read()
        
        if not success:
            failed_reads += 1
            if failed_reads >= max_failed_reads:
                add_log("⚠ Mất kết nối camera. Đang thử kết nối lại...")
                reconnect_camera()
                failed_reads = 0
            time.sleep(0.1)
            continue
        
        # Reset failed reads counter on successful read
        failed_reads = 0
        frame_count += 1
        
        # Only run detection every 10 frames or every 2 seconds (giảm lag)
        current_time = time.time()
        if frame_count % 10 == 0 or (current_time - last_detection_time) > 2:
            frame = detect_persons(frame)
            last_detection_time = current_time
        
        # Draw overlays
        frame = draw_crosshair(frame)
        frame = draw_scan_line(frame, frame_count)
        
        # Encode frame với quality thấp hơn để giảm bandwidth
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        # Giảm xuống 20 FPS để ổn định hơn với RTSP
        time.sleep(0.05)

def update_sensors():
    """Background thread to simulate sensor updates"""
    while True:
        sensor_data["gas_level"] = max(0, min(100, sensor_data["gas_level"] + random.randint(-2, 2)))
        sensor_data["dust_pm25"] = max(0, min(100, sensor_data["dust_pm25"] + random.randint(-1, 1)))
        
        # Cập nhật nhiệt độ (20-30°C)
        sensor_data["temperature"] = max(20, min(35, sensor_data["temperature"] + random.uniform(-0.5, 0.5)))
        
        # Cập nhật CO (0-50 ppm, an toàn < 9 ppm)
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
    # Add initial log
    add_log("Hệ thống khởi động thành công.")
    add_log("AI VISION: PHÁT HIỆN DẤU HIỆU SỰ SỐNG")
    
    # Start sensor update thread
    sensor_thread = threading.Thread(target=update_sensors, daemon=True)
    sensor_thread.start()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5001, debug=True, threaded=True)

