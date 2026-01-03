"""
SAR-BOT PRO - AI Camera System (ULTRA OPTIMIZED)
Tối ưu tối đa cho RTSP stream mượt mà + nhận diện người
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

# EZVIZ RTSP Configuration (SUB STREAM)
RTSP_URL = "rtsp://admin:EEZSQY@192.168.1.5:554/h264/ch01/sub/av_stream"
USE_RTSP = True

# Optimization settings
STREAM_WIDTH = 640  # Resize stream xuống 640px (từ 1280px) = giảm 75% data
STREAM_HEIGHT = 360
DETECTION_INTERVAL = 3  # Detect mỗi 3 giây (thay vì mỗi vài frames)
JPEG_QUALITY = 65  # Giảm quality

# Global variables
camera = None
camera_lock = threading.Lock()
system_logs = []
detected_persons = 0
detection_boxes = []  # Cache detection results
last_detection_time = 0
is_recording = False
camera_reconnect_attempts = 0

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

# Frame queue for detection (non-blocking)
detection_queue = Queue(maxsize=2)

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
                    add_log("Đang kết nối EZVIZ camera...")
                    
                    import os
                    # Ultra low latency settings
                    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = (
                        "rtsp_transport;tcp|"
                        "fflags;nobuffer|"
                        "flags;low_delay|"
                        "framedrop;1"
                    )
                    
                    camera = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
                    
                    # Ultra optimized settings
                    camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    camera.set(cv2.CAP_PROP_FPS, 15)
                    camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'H264'))
                    
                    # Timeout
                    camera.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)
                    camera.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 5000)
                else:
                    add_log("Đang kết nối webcam local...")
                    camera = cv2.VideoCapture(0)
                    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
                
                if camera.isOpened():
                    add_log("✓ Camera đã kết nối thành công.")
                    if USE_RTSP:
                        add_log(f"Stream: {RTSP_URL.split('@')[1] if '@' in RTSP_URL else RTSP_URL}")
                    camera_reconnect_attempts = 0
                else:
                    add_log("✗ LỖI: Không thể kết nối camera.")
                    camera = None
                    
            except Exception as e:
                add_log(f"✗ LỖI kết nối camera: {str(e)}")
                camera = None

def detect_persons_async(frame_small):
    """Detect persons asynchronously (optimized)"""
    global detected_persons, detection_boxes
    
    try:
        # Detect với scale nhỏ hơn = nhanh hơn
        boxes, weights = hog.detectMultiScale(
            frame_small,
            winStride=(16, 16),  # Tăng stride = nhanh hơn, ít chính xác hơn
            padding=(8, 8),
            scale=1.1,  # Tăng scale = ít level = nhanh hơn
            hitThreshold=0.5,  # Threshold cao hơn = ít false positive
            finalThreshold=2.0
        )
        
        detected_persons = len(boxes)
        detection_boxes = [(box, weight) for box, weight in zip(boxes, weights)]
        
        if detected_persons > 0:
            add_log(f"AI VISION: PHÁT HIỆN {detected_persons} NGƯỜI")
            
    except Exception as e:
        print(f"Detection error: {e}")

def detection_thread():
    """Background thread for person detection"""
    global last_detection_time
    
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
    """Draw detection boxes from cached results"""
    for (x, y, w, h), weight in detection_boxes:
        # Scale to display size
        x, y, w, h = int(x * scale_x), int(y * scale_y), int(w * scale_x), int(h * scale_y)
        
        # Simple bounding box (faster than corners)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
        
        # Label
        cv2.putText(frame, "PERSON", (x, y - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
    
    return frame

def draw_simple_overlay(frame):
    """Draw minimal overlay (crosshair only)"""
    h, w = frame.shape[:2]
    cx, cy = w // 2, h // 2
    
    color = (0, 255, 255)
    
    # Simple crosshair
    cv2.circle(frame, (cx, cy), 30, color, 1)
    cv2.circle(frame, (cx, cy), 3, color, -1)
    
    # Lines
    gap = 10
    length = 20
    cv2.line(frame, (cx - gap - length, cy), (cx - gap, cy), color, 1)
    cv2.line(frame, (cx + gap, cy), (cx + gap + length, cy), color, 1)
    cv2.line(frame, (cx, cy - gap - length), (cx, cy - gap), color, 1)
    cv2.line(frame, (cx, cy + gap), (cx, cy + gap + length), color, 1)
    
    return frame

def reconnect_camera():
    """Reconnect camera if connection lost"""
    global camera, camera_reconnect_attempts
    
    with camera_lock:
        if camera is not None:
            camera.release()
            camera = None
        
        camera_reconnect_attempts += 1
        add_log(f"Thử kết nối lại... (lần {camera_reconnect_attempts})")
        
    time.sleep(2)
    init_camera()

def generate_frames():
    """Generate video frames for streaming (ULTRA OPTIMIZED)"""
    global camera, camera_reconnect_attempts, last_detection_time
    init_camera()
    
    frame_count = 0
    failed_reads = 0
    max_failed_reads = 10
    
    # Detection scale (detect trên frame nhỏ hơn)
    detection_width = 320
    detection_height = 180
    
    while True:
        with camera_lock:
            if camera is None or not camera.isOpened():
                if camera_reconnect_attempts < 5:
                    reconnect_camera()
                time.sleep(1)
                continue
            
            # Skip buffered frames (critical for low latency)
            if USE_RTSP:
                for _ in range(2):  # Skip 2 frames
                    camera.grab()
            
            success, frame = camera.read()
        
        if not success:
            failed_reads += 1
            if failed_reads >= max_failed_reads:
                add_log("⚠ Mất kết nối. Đang kết nối lại...")
                reconnect_camera()
                failed_reads = 0
            time.sleep(0.1)
            continue
        
        failed_reads = 0
        frame_count += 1
        
        # Resize frame for streaming (critical for performance)
        frame_display = cv2.resize(frame, (STREAM_WIDTH, STREAM_HEIGHT), 
                                   interpolation=cv2.INTER_LINEAR)
        
        # Send frame to detection thread every DETECTION_INTERVAL seconds
        current_time = time.time()
        if (current_time - last_detection_time) >= DETECTION_INTERVAL:
            if detection_queue.empty():
                frame_detect = cv2.resize(frame, (detection_width, detection_height))
                try:
                    detection_queue.put_nowait(frame_detect)
                except:
                    pass
        
        # Draw cached detection boxes
        if detection_boxes:
            scale_x = STREAM_WIDTH / detection_width
            scale_y = STREAM_HEIGHT / detection_height
            frame_display = draw_detections(frame_display, scale_x, scale_y)
        
        # Draw minimal overlay
        frame_display = draw_simple_overlay(frame_display)
        
        # Encode with lower quality
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY]
        ret, buffer = cv2.imencode('.jpg', frame_display, encode_param)
        
        if not ret:
            continue
            
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        # 15 FPS
        time.sleep(0.066)

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
    # Add initial log
    add_log("Hệ thống khởi động (OPTIMIZED MODE).")
    add_log("AI VISION: PHÁT HIỆN DẤU HIỆU SỰ SỐNG")
    
    # Start detection thread
    detection_worker = threading.Thread(target=detection_thread, daemon=True)
    detection_worker.start()
    
    # Start sensor update thread
    sensor_thread = threading.Thread(target=update_sensors, daemon=True)
    sensor_thread.start()
    
    # Run Flask app
    print("=" * 60)
    print("SAR-BOT PRO - ULTRA OPTIMIZED MODE")
    print("=" * 60)
    print(f"Stream: {STREAM_WIDTH}x{STREAM_HEIGHT}")
    print(f"Detection: Every {DETECTION_INTERVAL} seconds")
    print(f"JPEG Quality: {JPEG_QUALITY}%")
    print(f"Target FPS: 15")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)

