"""
Şerit takip eden ve engel algılayan robot ana programı
Siyah zemin üzerinde beyaz şerit takibi ve renk tabanlı engel tespiti için optimize edilmiş
Raspberry Pi 5 ve Pi Camera 3 için uyumlu hale getirilmiştir
"""

import time
import cv2
import numpy as np
import config
from motor_controller import MotorController
from line_detector import LineDetector
from obstacle_detector import ObstacleDetector
import os
import sys
import logging
from loguru import logger

# Picamera2 modülünü kontrol et ve içe aktar
try:
    # Doğrudan modül yolunu belirterek içe aktarma deneyin
    import sys
    import os

    # Olası picamera2 modül yollarını ekle
    possible_paths = [
        "/usr/lib/python3/dist-packages",
        "/usr/local/lib/python3.9/dist-packages",  # Python sürümünüze göre değişebilir
        "/usr/local/lib/python3.10/dist-packages", # Python sürümünüze göre değişebilir
        "/usr/local/lib/python3.11/dist-packages"  # Python sürümünüze göre değişebilir
    ]

    for path in possible_paths:
        if os.path.exists(path) and path not in sys.path:
            sys.path.append(path)
            logger.info(f"Python modül yoluna eklendi: {path}")

    # Python modül yollarını göster (debug için)
    logger.debug(f"Python modül yolları: {sys.path}")

    # Şimdi içe aktarmayı dene
    from picamera2 import Picamera2
    logger.info("Picamera2 modülü başarıyla içe aktarıldı")

    # libcamera modülünü içe aktarmayı dene
    try:
        from libcamera import Transform
        logger.info("libcamera.Transform modülü başarıyla içe aktarıldı")
    except ImportError as e:
        logger.warning(f"libcamera.Transform içe aktarılamadı: {e}")
        logger.warning("Transform sınıfı olmadan devam edilecek")
        # Transform sınıfı olmadan devam etmek için boş bir sınıf tanımla
        class Transform:
            def __init__(self, hflip=False, vflip=False):
                self.hflip = hflip
                self.vflip = vflip

    PICAMERA_AVAILABLE = True
except ImportError as e:
    logger.error(f"Picamera2 modülü içe aktarılamadı: {e}")
    logger.error("Hata detayları:")
    import traceback
    logger.error(traceback.format_exc())
    logger.error("\nÇözüm önerileri:")
    logger.error("1. Modül yollarını kontrol edin: python3 -c \"import sys; print(sys.path)\"")
    logger.error("2. Modülün kurulu olduğunu doğrulayın: dpkg -l | grep picamera")
    logger.error("3. Modülü yeniden yükleyin: sudo apt install -y --reinstall python3-picamera2 python3-libcamera")
    logger.error("4. Raspberry Pi'yi yeniden başlatın: sudo reboot")
    PICAMERA_AVAILABLE = False

# Loglama ayarları
logger.remove()  # Varsayılan logger'ı kaldır
logger.add(sys.stderr, level="INFO")  # Konsola log
logger.add("robot_log.txt", rotation="10 MB", level="DEBUG")  # Dosyaya log

def main():
    logger.info("Şerit Takip Eden Robot Başlatılıyor...")

    # Debug modu kontrolü
    debug_mode = os.environ.get('DEBUG_MODE', 'False').lower() == 'true'
    if debug_mode:
        logger.info("Debug modu aktif")
        # Debug klasörü oluştur
        os.makedirs("debug_images", exist_ok=True)

    # Kamera kontrolü
    if not PICAMERA_AVAILABLE:
        logger.error("Picamera2 modülü yüklenemedi. Program sonlandırılıyor.")
        sys.exit(1)

    # Kamera başlatma
    logger.info("Kamera başlatılıyor...")
    try:
        picam2 = Picamera2()

        # Raspberry Pi 5 ve Pi Camera 3 için özel yapılandırma
        # Transform sınıfı kullanılabilir mi kontrol et
        if 'Transform' in globals():
            # Transform sınıfı varsa kullan
            camera_config = picam2.create_still_configuration(
                main={"size": config.CAMERA_RESOLUTION, "format": "RGB888"},
                transform=Transform(hflip=config.CAMERA_HFLIP, vflip=config.CAMERA_VFLIP)
            )
            logger.info("Transform sınıfı ile kamera yapılandırıldı")
        else:
            # Transform sınıfı yoksa daha basit yapılandırma kullan
            camera_config = picam2.create_still_configuration(
                main={"size": config.CAMERA_RESOLUTION, "format": "RGB888"}
            )
            logger.info("Basit yapılandırma ile kamera yapılandırıldı")

        # Yapılandırmayı uygula - hata olursa alternatif yöntemleri dene
        try:
            # İlk yöntem: still_configuration
            picam2.configure(camera_config)
            logger.info("Kamera still_configuration ile yapılandırıldı")
        except Exception as e:
            logger.warning(f"still_configuration hatası: {e}")
            try:
                # İkinci yöntem: preview_configuration
                logger.info("Alternatif yapılandırma deneniyor (preview_configuration)...")
                preview_config = picam2.create_preview_configuration(
                    main={"size": config.CAMERA_RESOLUTION, "format": "RGB888"}
                )
                picam2.configure(preview_config)
                logger.info("Kamera preview_configuration ile yapılandırıldı")
            except Exception as e2:
                logger.warning(f"preview_configuration hatası: {e2}")
                try:
                    # Üçüncü yöntem: video_configuration
                    logger.info("Alternatif yapılandırma deneniyor (video_configuration)...")
                    video_config = picam2.create_video_configuration(
                        main={"size": config.CAMERA_RESOLUTION, "format": "RGB888"}
                    )
                    picam2.configure(video_config)
                    logger.info("Kamera video_configuration ile yapılandırıldı")
                except Exception as e3:
                    # Son çare: varsayılan yapılandırma
                    logger.warning(f"video_configuration hatası: {e3}")
                    logger.info("Varsayılan yapılandırma deneniyor...")
                    picam2.configure(picam2.create_preview_configuration())
                    logger.info("Kamera varsayılan yapılandırma ile yapılandırıldı")

        # Kamerayı başlat
        logger.info("Kamera başlatılıyor...")
        picam2.start()

        # Kameranın başlaması için bekle
        logger.info("Kameranın başlaması bekleniyor...")
        time.sleep(3)  # Daha uzun bekleme süresi

        # Test görüntüsü al - birkaç kez dene
        logger.info("Test görüntüsü alınıyor...")
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                test_frame = picam2.capture_array()
                if test_frame is not None and test_frame.size > 0:
                    logger.info(f"Kamera hazır. Görüntü boyutu: {test_frame.shape}")
                    break
                else:
                    logger.warning(f"Boş görüntü alındı (deneme {attempt+1}/{max_attempts})")
                    time.sleep(1)
            except Exception as e:
                logger.warning(f"Görüntü alma hatası (deneme {attempt+1}/{max_attempts}): {e}")
                time.sleep(1)

            # Son deneme başarısız olduysa
            if attempt == max_attempts - 1:
                logger.warning("Test görüntüsü alınamadı, ancak devam edilecek")
                # Hata fırlatma yerine uyarı ver ve devam et
                # raise Exception("Kamera görüntü alamıyor")
    except Exception as e:
        logger.error(f"Kamera başlatılamadı: {e}")
        logger.error("Hata detayları:")
        import traceback
        logger.error(traceback.format_exc())
        logger.error("\nÇözüm önerileri:")
        logger.error("1. Kamera bağlantısını kontrol edin")
        logger.error("2. 'sudo raspi-config' ile kamera arayüzünün etkin olduğundan emin olun")
        logger.error("3. 'libcamera-hello' komutu ile kameranın çalıştığını doğrulayın")
        logger.error("4. 'sudo apt install -y python3-picamera2 python3-libcamera libcamera-apps' komutunu çalıştırın")
        logger.error("5. Raspberry Pi'yi yeniden başlatın")
        sys.exit(1)

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
            try:
                # Farklı görüntü alma yöntemlerini dene
                try:
                    # Birincil yöntem: capture_array()
                    frame = picam2.capture_array()
                except Exception as e1:
                    logger.warning(f"capture_array() hatası: {e1}")
                    try:
                        # İkincil yöntem: capture_array("main")
                        logger.info("Alternatif görüntü alma yöntemi deneniyor (capture_array('main'))...")
                        frame = picam2.capture_array("main")
                    except Exception as e2:
                        logger.warning(f"capture_array('main') hatası: {e2}")
                        try:
                            # Üçüncü yöntem: capture_image ve numpy dönüşümü
                            logger.info("Alternatif görüntü alma yöntemi deneniyor (capture_image)...")
                            import numpy as np
                            from PIL import Image
                            img = picam2.capture_image()
                            frame = np.array(img)
                        except Exception as e3:
                            logger.error(f"Tüm görüntü alma yöntemleri başarısız: {e3}")
                            time.sleep(1)
                            continue

                # Görüntü kontrolü
                if frame is None or frame.size == 0:
                    logger.warning("Boş kamera görüntüsü alındı, yeniden deneniyor...")
                    time.sleep(0.5)
                    continue

                # Görüntü boyutunu kontrol et (debug için)
                if frame_count % 100 == 0:
                    logger.debug(f"Görüntü boyutu: {frame.shape}")

            except Exception as e:
                logger.error(f"Görüntü alma hatası: {e}")
                time.sleep(1)
                continue

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
        import traceback
        logger.error(traceback.format_exc())
    finally:
        # Temizlik işlemleri
        logger.info("Temizlik yapılıyor...")
        try:
            motors.cleanup()
            logger.info("Motor GPIO pinleri temizlendi.")
        except Exception as e:
            logger.error(f"Motor temizleme hatası: {e}")

        try:
            picam2.stop()
            logger.info("Kamera durduruldu.")
        except Exception as e:
            logger.error(f"Kamera durdurma hatası: {e}")

        try:
            cv2.destroyAllWindows()
        except Exception as e:
            logger.error(f"OpenCV pencere kapatma hatası: {e}")

        logger.info("Program sonlandırıldı.")

if __name__ == "__main__":
    main()
