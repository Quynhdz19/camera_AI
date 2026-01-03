"""
SAR-BOT PRO - YOLO PERSON DETECTION
Sử dụng YOLOv8 để nhận diện người CHÍNH XÁC
"""

from flask import Flask, render_template, Response, jsonify
import cv2
import numpy as np
from datetime import datetime
import threading
import time
import random
from queue import Queue
from ultralytics import YOLO

app = Flask(__name__)

# EZVIZ RTSP Configuration
RTSP_URL = "rtsp://admin:EEZSQY@192.168.1.5:554/h264/ch01/sub/av_stream"
USE_RTSP = True

# Optimization settings
STREAM_WIDTH = 640      # Tăng lên 640 vì YOLO nhanh hơn HOG
STREAM_HEIGHT = 360
DETECTION_INTERVAL = 1  # Detect mỗi 1 giây vì YOLO nhanh
JPEG_QUALITY = 60
TARGET_FPS = 15

# Global variables
camera = None
camera_lock = threading.Lock()
system_logs = []
detected_persons = 0
detection_boxes = []
last_detection_time = 0
is_recording = False
camera_reconnect_attempts = 0
detection_active = False

# Sensor data
sensor_data = {
    "gas_level": 77,
    "dust_pm25": 18,
    "temperature": 24.5,
    "co_level": 8,
    "signal_strength": 95,
    "battery_level": 84
}

# Initialize YOLO model
print("🤖 Loading YOLOv8 model...")
model = YOLO('yolov8n.pt')  # YOLOv8 nano - nhanh nhất
print("✅ YOLO model loaded successfully!")

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
                        "framedrop;1"
                    )
                    
                    camera = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
                    camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    camera.set(cv2.CAP_PROP_FPS, TARGET_FPS)
                else:
                    add_log("🔌 Đang kết nối webcam local...")
                    camera = cv2.VideoCapture(0)
                    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
                
                if camera.isOpened():
                    add_log("✅ Camera kết nối - YOLO MODE")
                    add_log(f"🎯 YOLOv8 Person Detection: ACTIVE")
                    camera_reconnect_attempts = 0
                else:
                    add_log("❌ LỖI: Không thể kết nối camera")
                    camera = None
                    
            except Exception as e:
                add_log(f"❌ LỖI: {str(e)}")
                camera = None

def detect_persons_yolo(frame):
    """Detect persons using YOLO - CỰC CHÍNH XÁC"""
    global detected_persons, detection_boxes, detection_active
    
    detection_active = True
    
    try:
        # Run YOLO inference
        results = model(frame, conf=0.25, classes=[0], verbose=False)  # class 0 = person, confidence 25%
        
        detection_boxes = []
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Get coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = box.conf[0].cpu().numpy()
                
                # Convert to (x, y, w, h) format
                x, y, w, h = int(x1), int(y1), int(x2-x1), int(y2-y1)
                detection_boxes.append(((x, y, w, h), float(conf)))
        
        detected_persons = len(detection_boxes)
        
        if detected_persons > 0:
            add_log(f"👤 YOLO: PHÁT HIỆN {detected_persons} NGƯỜI!")
            print(f"[YOLO] Detected {detected_persons} persons")
            
    except Exception as e:
        print(f"YOLO Detection error: {e}")
    finally:
        detection_active = False

def detection_thread():
    """Background thread for YOLO detection"""
    global last_detection_time
    
    add_log("🤖 YOLO Detection thread started")
    
    while True:
        try:
            if not detection_queue.empty():
                frame = detection_queue.get()
                detect_persons_yolo(frame)
                last_detection_time = time.time()
            time.sleep(0.05)
        except Exception as e:
            print(f"Detection thread error: {e}")
            time.sleep(1)

def draw_detections(frame):
    """Draw YOLO detection boxes - RÕ RÀNG"""
    for idx, ((x, y, w, h), conf) in enumerate(detection_boxes):
        # KHUNG CHÍNH - MÀU XANH LÁ NEON
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 4)
        
        # KHUNG PHỤ BÊN TRONG - MÀU VÀNG
        cv2.rectangle(frame, (x+3, y+3), (x + w-3, y + h-3), (0, 255, 255), 2)
        
        # VẼ GÓC - MÀU ĐỎ
        corner_len = 30
        corner_color = (0, 0, 255)
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
        
        # LABEL với confidence
        label = f"PERSON {int(conf*100)}%"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.9
        font_thickness = 3
        label_size = cv2.getTextSize(label, font, font_scale, font_thickness)[0]
        
        # Background VÀNG NEON
        label_x = max(x, 0)
        label_y = max(y - label_size[1] - 15, label_size[1] + 10)
        cv2.rectangle(frame, 
                     (label_x, label_y - label_size[1] - 10), 
                     (label_x + label_size[0] + 10, label_y + 5), 
                     (0, 255, 255), -1)
        
        # Text ĐEN
        cv2.putText(frame, label, (label_x + 5, label_y), 
                    font, font_scale, (0, 0, 0), font_thickness)
    
    return frame

def draw_overlay(frame):
    """Draw overlay"""
    h, w = frame.shape[:2]
    
    # Detection counter
    if detected_persons > 0:
        counter_text = f"DETECTED: {detected_persons} PERSON(S)"
        text_size = cv2.getTextSize(counter_text, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)[0]
        
        cv2.rectangle(frame, (10, 10), (20 + text_size[0], 45 + text_size[1]), (0, 255, 0), -1)
        cv2.putText(frame, counter_text, (15, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2)
    
    # YOLO indicator
    yolo_text = "YOLO"
    if detection_active:
        cv2.circle(frame, (w - 30, 30), 12, (0, 255, 0), -1)
    cv2.putText(frame, yolo_text, (w - 55, 37), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    # Crosshair
    cx, cy = w // 2, h // 2
    color = (0, 255, 255)
    cv2.circle(frame, (cx, cy), 25, color, 1)
    cv2.circle(frame, (cx, cy), 3, color, -1)
    
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
        add_log(f"🔄 Kết nối lại... (lần {camera_reconnect_attempts})")
        
    time.sleep(2)
    init_camera()

def generate_frames():
    """Generate video frames with YOLO detection"""
    global camera, camera_reconnect_attempts, last_detection_time
    init_camera()
    
    frame_count = 0
    failed_reads = 0
    max_failed_reads = 15
    
    add_log("🎬 Video stream started with YOLO")
    
    while True:
        with camera_lock:
            if camera is None or not camera.isOpened():
                if camera_reconnect_attempts < 5:
                    reconnect_camera()
                time.sleep(1)
                continue
            
            # Skip buffered frames
            if USE_RTSP:
                for _ in range(2):
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
        
        # Resize for streaming
        frame_display = cv2.resize(frame, (STREAM_WIDTH, STREAM_HEIGHT), 
                                   interpolation=cv2.INTER_LINEAR)
        
        # Send to YOLO detection thread
        current_time = time.time()
        if (current_time - last_detection_time) >= DETECTION_INTERVAL:
            if detection_queue.empty():
                try:
                    detection_queue.put_nowait(frame_display.copy())
                except:
                    pass
        
        # Draw detection boxes
        if len(detection_boxes) > 0:
            frame_display = draw_detections(frame_display)
        
        # Draw overlay
        frame_display = draw_overlay(frame_display)
        
        # Encode
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY]
        ret, buffer = cv2.imencode('.jpg', frame_display, encode_param)
        
        if not ret:
            continue
            
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
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
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/status')
def get_status():
    return jsonify({
        "sensor_data": sensor_data,
        "detected_persons": detected_persons,
        "is_recording": is_recording,
        "system_online": True
    })

@app.route('/api/logs')
def get_logs():
    return jsonify({"logs": system_logs[:20]})

if __name__ == '__main__':
    print("\n" + "="*70)
    print("  🚀 SAR-BOT PRO - YOLO PERSON DETECTION")
    print("="*70)
    print(f"  🤖 Model: YOLOv8-Nano (Ultra Fast)")
    print(f"  📹 Stream: {STREAM_WIDTH}x{STREAM_HEIGHT} @ {TARGET_FPS}fps")
    print(f"  🔍 Detection: Every {DETECTION_INTERVAL} second")
    print(f"  📊 JPEG Quality: {JPEG_QUALITY}%")
    print(f"  🎯 Accuracy: ⭐⭐⭐⭐⭐ (YOLO)")
    print("="*70 + "\n")
    
    add_log("🚀 SAR-BOT PRO - YOLO MODE")
    add_log("🤖 YOLOv8 Person Detection: ACTIVE")
    
    # Start detection thread
    detection_worker = threading.Thread(target=detection_thread, daemon=True)
    detection_worker.start()
    
    # Start sensor thread
    sensor_thread = threading.Thread(target=update_sensors, daemon=True)
    sensor_thread.start()
    
    # Run Flask
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)

