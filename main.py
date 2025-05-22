"""
Şerit takip eden ve engel algılayan robot ana programı
Siyah zemin üzerinde beyaz şerit takibi ve renk tabanlı engel tespiti için optimize edilmiş
"""

import time
import cv2
import numpy as np
from picamera2 import Picamera2
import config
from motor_controller import MotorController
from line_detector import LineDetector
from obstacle_detector import ObstacleDetector
import os
import logging

# Loglama ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("robot_log.txt"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("OtonomZero")

def main():
    logger.info("Şerit Takip Eden Robot Başlatılıyor...")

    # Debug modu kontrolü
    debug_mode = os.environ.get('DEBUG_MODE', 'False').lower() == 'true'
    if debug_mode:
        logger.info("Debug modu aktif")
        # Debug klasörü oluştur
        os.makedirs("debug_images", exist_ok=True)

    # Kamera başlatma
    logger.info("Kamera başlatılıyor...")
    picam2 = Picamera2()
    camera_config = picam2.create_preview_configuration(
        main={"size": config.CAMERA_RESOLUTION, "format": "RGB888"},
        lores={"size": (320, 240), "format": "YUV420"},
        display="lores"
    )
    picam2.configure(camera_config)
    picam2.start()
    time.sleep(2)  # Kameranın başlaması için bekle
    logger.info("Kamera hazır.")

    # Motor kontrolcüsü başlatma
    logger.info("Motor kontrolcüsü başlatılıyor...")
    motors = MotorController()
    logger.info("Motor kontrolcüsü hazır.")

    # Şerit algılayıcı başlatma
    logger.info("Şerit algılayıcı başlatılıyor...")
    line_detector = LineDetector()
    logger.info("Şerit algılayıcı hazır.")

    # Engel algılayıcı başlatma
    logger.info("Engel algılayıcı başlatılıyor...")
    obstacle_detector = ObstacleDetector()
    logger.info("Engel algılayıcı hazır.")

    # Durum değişkenleri
    is_at_crosswalk = False
    crosswalk_start_time = 0
    avoiding_obstacle = False
    obstacle_start_time = 0
    avoidance_direction = None
    frame_count = 0

    logger.info("Robot hazır! Başlatılıyor...")

    try:
        while True:
            # Kameradan görüntü al
            frame = picam2.capture_array("main")

            # Kare sayacını artır
            frame_count += 1

            # Durum kontrolü
            current_time = time.time()

            # 1. Zemin geçidinde durma durumu
            if is_at_crosswalk:
                if current_time - crosswalk_start_time >= config.CROSSWALK_STOP_TIME:
                    logger.info("Zemin geçidi geçiliyor...")
                    is_at_crosswalk = False
                    motors.forward(config.DEFAULT_SPEED)
                else:
                    # Zemin geçidinde bekle
                    motors.stop()
                    continue

            # 2. Engelden kaçınma durumu
            if avoiding_obstacle:
                if current_time - obstacle_start_time >= config.OBSTACLE_AVOIDANCE_TIME:
                    logger.info("Engelden kaçınma tamamlandı.")
                    avoiding_obstacle = False
                    motors.forward(config.DEFAULT_SPEED)
                else:
                    # Engelden kaçınma manevrası devam ediyor
                    continue

            # 3. Normal çalışma durumu - Engel kontrolü
            has_obstacle, obstacle_position, obstacle_processed_frame = obstacle_detector.detect_obstacles(frame)

            # Engel renk tespiti
            if has_obstacle:
                obstacle_color, color_confidence = obstacle_detector.detect_obstacle_color(frame)
                logger.info(f"Engel tespit edildi: {obstacle_position}, Renk: {obstacle_color}, Güven: {color_confidence:.2f}")
                avoidance_direction = obstacle_detector.get_avoidance_direction(obstacle_position)

                # Engelden kaçınma manevrası başlat
                logger.info(f"Engelden kaçınma yönü: {avoidance_direction}")
                avoiding_obstacle = True
                obstacle_start_time = current_time

                if avoidance_direction == "left":
                    motors.turn_left(config.TURN_SPEED)
                elif avoidance_direction == "right":
                    motors.turn_right(config.TURN_SPEED)
                elif avoidance_direction == "backward_right":
                    motors.backward(config.SLOW_SPEED)
                    time.sleep(1)
                    motors.turn_right(config.TURN_SPEED)
                elif avoidance_direction == "backward_left":
                    motors.backward(config.SLOW_SPEED)
                    time.sleep(1)
                    motors.turn_left(config.TURN_SPEED)

                # Debug modunda görüntüyü kaydet
                if debug_mode and frame_count % 10 == 0:
                    cv2.imwrite(f"debug_images/obstacle_{frame_count}.jpg", obstacle_processed_frame)

                continue

            # 4. Normal çalışma durumu - Zemin geçidi kontrolü
            is_crosswalk, crosswalk_confidence, crosswalk_processed_frame = line_detector.is_crosswalk(frame)

            if is_crosswalk:
                logger.info(f"Zemin geçidi tespit edildi! Güven: {crosswalk_confidence:.2f}")
                is_at_crosswalk = True
                crosswalk_start_time = current_time
                motors.stop()

                # Debug modunda görüntüyü kaydet
                if debug_mode:
                    cv2.imwrite(f"debug_images/crosswalk_{frame_count}.jpg", crosswalk_processed_frame)

                continue

            # 5. Normal çalışma durumu - Şerit takibi
            line_position, line_processed_frame = line_detector.detect_line(frame)

            # Şerit kontrolü
            if line_position is not None:

                # Şerit pozisyonuna göre hareket et
                if abs(line_position) < config.LINE_POSITION_THRESHOLD:
                    # Düz git
                    motors.forward(config.DEFAULT_SPEED)
                    if frame_count % 50 == 0:
                        logger.debug(f"Düz gidiyor. Şerit pozisyonu: {line_position}")
                elif line_position < 0:
                    # Sola dön
                    motors.curve_left(config.CURVE_SPEED)
                    if frame_count % 20 == 0:
                        logger.debug(f"Sola dönüyor. Şerit pozisyonu: {line_position}")
                else:
                    # Sağa dön
                    motors.curve_right(config.CURVE_SPEED)
                    if frame_count % 20 == 0:
                        logger.debug(f"Sağa dönüyor. Şerit pozisyonu: {line_position}")
            else:
                # Şerit bulunamadı, son bilinen yöne devam et veya dur
                logger.warning("Şerit bulunamadı!")
                motors.stop()

            # Debug modunda görüntüleri kaydet
            if debug_mode and frame_count % 30 == 0:
                cv2.imwrite(f"debug_images/line_{frame_count}.jpg", line_processed_frame)

            # Döngü hızını kontrol et
            time.sleep(0.05)

    except KeyboardInterrupt:
        logger.info("Program kullanıcı tarafından durduruldu.")
    except Exception as e:
        logger.error(f"Hata oluştu: {e}")
    finally:
        # Temizlik işlemleri
        logger.info("Temizlik yapılıyor...")
        motors.cleanup()
        picam2.stop()
        cv2.destroyAllWindows()
        logger.info("Program sonlandırıldı.")

if __name__ == "__main__":
    main()
