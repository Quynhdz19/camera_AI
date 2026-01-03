"""
SAR-BOT PRO - Configuration File
Cấu hình cho hệ thống camera AI
"""

# ==================== CAMERA CONFIGURATION ====================

# Chế độ camera: True = RTSP Stream, False = Webcam Local
USE_RTSP = True  # Đã bật RTSP cho camera EZVIZ

# RTSP URL cho camera EZVIZ
# Format: rtsp://username:password@ip_address:port/path
RTSP_CONFIG = {
    # Thông tin đăng nhập
    "username": "admin",
    "password": "EEZSQY",  # Verification code của camera EZVIZ
    
    # Network
    "ip_address": "192.168.1.5",  # IP của camera EZVIZ
    "port": 554,  # Port mặc định cho RTSP
    
    # Stream path
    # Main stream (HD): /h264/ch01/main/av_stream
    # Sub stream (SD): /h264/ch01/sub/av_stream (khuyến nghị cho AI)
    "stream_path": "/h264/ch01/main/av_stream",
}

# Tự động tạo RTSP URL từ config trên
RTSP_URL = f"rtsp://{RTSP_CONFIG['username']}:{RTSP_CONFIG['password']}@{RTSP_CONFIG['ip_address']}:{RTSP_CONFIG['port']}{RTSP_CONFIG['stream_path']}"

# Hoặc bạn có thể nhập trực tiếp RTSP URL ở đây:
# RTSP_URL = "rtsp://admin:ABCDEF@192.168.1.100:554/h264/ch01/sub/av_stream"

# ==================== CAMERA SETTINGS ====================

# Webcam settings (khi USE_RTSP = False)
WEBCAM_INDEX = 0  # 0 = webcam mặc định
WEBCAM_WIDTH = 1280
WEBCAM_HEIGHT = 720

# RTSP connection settings
RTSP_BUFFER_SIZE = 1  # Giảm buffer để giảm độ trễ
RTSP_OPEN_TIMEOUT = 10000  # milliseconds
RTSP_READ_TIMEOUT = 10000  # milliseconds
MAX_RECONNECT_ATTEMPTS = 5  # Số lần thử kết nối lại tối đa

# ==================== DETECTION SETTINGS ====================

# Person detection
DETECTION_FREQUENCY = 5  # Chạy detection mỗi N frames (tăng để tối ưu performance)
DETECTION_SCALE = 0.5  # Scale frame trước khi detect (giảm để tăng tốc độ)

# ==================== SYSTEM SETTINGS ====================

# Flask server
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5001
FLASK_DEBUG = True

# Video streaming
VIDEO_FPS = 30  # Frames per second
VIDEO_JPEG_QUALITY = 85  # 0-100, cao hơn = chất lượng tốt hơn

# Sensor update interval
SENSOR_UPDATE_INTERVAL = 2  # seconds

# System logs
MAX_LOGS = 50  # Số lượng logs tối đa lưu trong bộ nhớ

