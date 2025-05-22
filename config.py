"""
Yapılandırma ayarları - Fiziksel pist ve araç özelliklerine göre optimize edilmiş
"""

# Fiziksel Pist Özellikleri
TRACK_WIDTH = 100  # Pist genişliği (cm)
LANE_WIDTH = 40    # Şerit genişliği (cm)
DASH_LENGTH = 20   # Kesik şerit uzunluğu (cm)
DASH_GAP = 20      # Kesikler arası mesafe (cm)

# Araç Özellikleri
ROBOT_WIDTH = 16   # Robot genişliği (cm)
ROBOT_LENGTH = 25  # Robot uzunluğu (cm)
ROBOT_HEIGHT = 23  # Robot yüksekliği (cm)
CAMERA_HEIGHT = 23 # Kameranın yerden yüksekliği (cm)

# GPIO Pin Tanımlamaları
# Pin numaralandırma sistemi (BOARD veya BCM)
PIN_NUMBERING = "BOARD"  # "BOARD" veya "BCM"

# BOARD Pin Numaraları (Fiziksel pin numaraları)
BOARD_LEFT_MOTOR_ENA = 12
BOARD_LEFT_MOTOR_IN1 = 16
BOARD_LEFT_MOTOR_IN2 = 18
BOARD_RIGHT_MOTOR_ENA = 32
BOARD_RIGHT_MOTOR_IN1 = 36
BOARD_RIGHT_MOTOR_IN2 = 38

# BCM Pin Numaraları (GPIO numaraları)
BCM_LEFT_MOTOR_ENA = 18  # GPIO18
BCM_LEFT_MOTOR_IN1 = 23  # GPIO23
BCM_LEFT_MOTOR_IN2 = 24  # GPIO24
BCM_RIGHT_MOTOR_ENA = 12  # GPIO12
BCM_RIGHT_MOTOR_IN1 = 16  # GPIO16
BCM_RIGHT_MOTOR_IN2 = 20  # GPIO20

# Aktif pin numaraları (PIN_NUMBERING'e göre otomatik seçilir)
if PIN_NUMBERING == "BOARD":
    # Fiziksel pin numaralarını kullan
    LEFT_MOTOR_ENA = BOARD_LEFT_MOTOR_ENA
    LEFT_MOTOR_IN1 = BOARD_LEFT_MOTOR_IN1
    LEFT_MOTOR_IN2 = BOARD_LEFT_MOTOR_IN2
    RIGHT_MOTOR_ENA = BOARD_RIGHT_MOTOR_ENA
    RIGHT_MOTOR_IN1 = BOARD_RIGHT_MOTOR_IN1
    RIGHT_MOTOR_IN2 = BOARD_RIGHT_MOTOR_IN2
else:
    # BCM pin numaralarını kullan
    LEFT_MOTOR_ENA = BCM_LEFT_MOTOR_ENA
    LEFT_MOTOR_IN1 = BCM_LEFT_MOTOR_IN1
    LEFT_MOTOR_IN2 = BCM_LEFT_MOTOR_IN2
    RIGHT_MOTOR_ENA = BCM_RIGHT_MOTOR_ENA
    RIGHT_MOTOR_IN1 = BCM_RIGHT_MOTOR_IN1
    RIGHT_MOTOR_IN2 = BCM_RIGHT_MOTOR_IN2

# Motor Hız Ayarları
DEFAULT_SPEED = 0.5  # %50 hız - daha kontrollü hareket için
TURN_SPEED = 0.4     # %40 hız
SLOW_SPEED = 0.3     # %30 hız
CURVE_SPEED = 0.45   # %45 hız - virajlar için

# Kamera Ayarları
CAMERA_RESOLUTION = (640, 480)  # Çözünürlük (genişlik, yükseklik)
CAMERA_FRAMERATE = 30           # FPS
CAMERA_ROTATION = 0             # Kamera açısı (derece)
CAMERA_HFLIP = False            # Yatay çevirme
CAMERA_VFLIP = False            # Dikey çevirme

# Görüntü İşleme Ayarları
ROI_HEIGHT = 150     # İlgi alanı yüksekliği (alt kısımdan) - arttırıldı
ROI_TOP_OFFSET = 100 # Üst ROI başlangıç noktası (üstten)
BINARY_THRESHOLD = 150  # İkili görüntü eşik değeri (0-255) - beyaz şerit için ayarlandı

# Şerit Takip Ayarları
LINE_POSITION_THRESHOLD = 25  # Merkez pozisyondan sapma eşiği (piksel)
LINE_DETECTION_MIN_PIXELS = 50  # Minimum şerit piksel sayısı

# Zemin Geçit Ayarları
CROSSWALK_STOP_TIME = 5  # Durma süresi (saniye)
CROSSWALK_DETECTION_THRESHOLD = 0.5  # Zemin geçit algılama eşiği (0-1)
CROSSWALK_APPROACH_DISTANCE = 30  # Zemin geçidine yaklaşma mesafesi (cm)
CROSSWALK_ROI_HEIGHT = 100  # Zemin geçidi ROI yüksekliği

# Engel Algılama Ayarları
OBSTACLE_DETECTION_THRESHOLD = 0.4  # Engel algılama eşiği (0-1) - daha hassas
OBSTACLE_AVOIDANCE_TIME = 2.5  # Engelden kaçınma manevra süresi (saniye)
OBSTACLE_COLOR_RANGES = {
    'orange': ([5, 100, 150], [15, 255, 255]),  # Turuncu engel için HSV aralığı
    'yellow': ([20, 100, 150], [30, 255, 255])  # Sarı engel için HSV aralığı
}
OBSTACLE_MIN_AREA = 500  # Minimum engel alanı (piksel kare)
