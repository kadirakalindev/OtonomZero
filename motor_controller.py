"""
Motor kontrol sınıfı - Şerit takip eden robot için optimize edilmiş
Raspberry Pi 5 için uyumlu hale getirilmiştir
"""

import time
import config
from loguru import logger

# GPIO modüllerini kontrol et ve içe aktar
try:
    from gpiozero import Motor, PWMOutputDevice
    GPIO_AVAILABLE = True
except ImportError:
    logger.error("gpiozero modülü bulunamadı! Lütfen şu komutu çalıştırın:")
    logger.error("sudo apt install -y python3-gpiozero")
    GPIO_AVAILABLE = False

class MotorController:
    def __init__(self):
        """
        Motor kontrol sınıfı başlatıcı
        Sol ve sağ motorları GPIO pinlerine göre yapılandırır
        """
        logger.info("Motor kontrolcüsü başlatılıyor...")

        # GPIO kullanılabilirliğini kontrol et
        if not GPIO_AVAILABLE:
            logger.error("GPIO modülleri yüklenemedi. Motor kontrolü devre dışı.")
            self.gpio_ok = False
            return

        try:
            # Sol motor için PWM hız kontrolü
            self.left_ena = PWMOutputDevice(config.LEFT_MOTOR_ENA)
            # Sol motor
            self.left_motor = Motor(config.LEFT_MOTOR_IN1, config.LEFT_MOTOR_IN2)

            # Sağ motor için PWM hız kontrolü
            self.right_ena = PWMOutputDevice(config.RIGHT_MOTOR_ENA)
            # Sağ motor
            self.right_motor = Motor(config.RIGHT_MOTOR_IN1, config.RIGHT_MOTOR_IN2)

            # Son hareket bilgisi
            self.last_movement = "stop"
            self.last_left_speed = 0
            self.last_right_speed = 0

            # Başlangıçta motorları durdur
            self.stop()

            self.gpio_ok = True
            logger.info(f"Motor kontrolcüsü hazır. GPIO pinleri: Sol: {config.LEFT_MOTOR_ENA}, {config.LEFT_MOTOR_IN1}, {config.LEFT_MOTOR_IN2} - Sağ: {config.RIGHT_MOTOR_ENA}, {config.RIGHT_MOTOR_IN1}, {config.RIGHT_MOTOR_IN2}")
        except Exception as e:
            logger.error(f"Motor kontrolcüsü başlatılamadı: {e}")
            self.gpio_ok = False

    def set_speeds(self, left_speed, right_speed):
        """
        Sol ve sağ motor hızlarını ayarlar

        Args:
            left_speed (float): Sol motor hızı (0.0 - 1.0)
            right_speed (float): Sağ motor hızı (0.0 - 1.0)
        """
        # GPIO kullanılabilirliğini kontrol et
        if not hasattr(self, 'gpio_ok') or not self.gpio_ok:
            logger.warning("GPIO kullanılamıyor. Motor hızları ayarlanamadı.")
            return

        # Hız değerlerini sınırla (0.0 - 1.0)
        left_speed = max(0.0, min(1.0, left_speed))
        right_speed = max(0.0, min(1.0, right_speed))

        # Değişim çok küçükse görmezden gel (titreşimi azaltmak için)
        if (abs(left_speed - self.last_left_speed) < 0.05 and
            abs(right_speed - self.last_right_speed) < 0.05):
            return

        try:
            # PWM değerlerini ayarla
            self.left_ena.value = left_speed
            self.right_ena.value = right_speed

            # Son hızları güncelle
            self.last_left_speed = left_speed
            self.last_right_speed = right_speed

            # Debug log
            if left_speed > 0 or right_speed > 0:
                logger.debug(f"Motor hızları: Sol: {left_speed:.2f}, Sağ: {right_speed:.2f}")
        except Exception as e:
            logger.error(f"Motor hızları ayarlanırken hata: {e}")

    def forward(self, speed=config.DEFAULT_SPEED):
        """
        İleri hareket

        Args:
            speed (float): Motor hızı (0.0 - 1.0)
        """
        if self.last_movement != "forward":
            logger.debug(f"İleri hareket başlatılıyor. Hız: {speed}")
            self.last_movement = "forward"

        self.set_speeds(speed, speed)
        self.left_motor.forward()
        self.right_motor.forward()

    def backward(self, speed=config.DEFAULT_SPEED):
        """
        Geri hareket

        Args:
            speed (float): Motor hızı (0.0 - 1.0)
        """
        if self.last_movement != "backward":
            logger.debug(f"Geri hareket başlatılıyor. Hız: {speed}")
            self.last_movement = "backward"

        self.set_speeds(speed, speed)
        self.left_motor.backward()
        self.right_motor.backward()

    def turn_left(self, speed=config.TURN_SPEED):
        """
        Sola dönüş

        Args:
            speed (float): Motor hızı (0.0 - 1.0)
        """
        if self.last_movement != "turn_left":
            logger.debug(f"Sola dönüş başlatılıyor. Hız: {speed}")
            self.last_movement = "turn_left"

        self.set_speeds(0, speed)
        self.left_motor.backward()
        self.right_motor.forward()

    def turn_right(self, speed=config.TURN_SPEED):
        """
        Sağa dönüş

        Args:
            speed (float): Motor hızı (0.0 - 1.0)
        """
        if self.last_movement != "turn_right":
            logger.debug(f"Sağa dönüş başlatılıyor. Hız: {speed}")
            self.last_movement = "turn_right"

        self.set_speeds(speed, 0)
        self.left_motor.forward()
        self.right_motor.backward()

    def curve_left(self, speed=config.CURVE_SPEED):
        """
        Sola kavis

        Args:
            speed (float): Motor hızı (0.0 - 1.0)
        """
        if self.last_movement != "curve_left":
            logger.debug(f"Sola kavis başlatılıyor. Hız: {speed}")
            self.last_movement = "curve_left"

        # Sola kavis için sol motor hızını azalt
        left_speed = speed * 0.4  # Daha yumuşak dönüş için 0.3 yerine 0.4
        self.set_speeds(left_speed, speed)
        self.left_motor.forward()
        self.right_motor.forward()

    def curve_right(self, speed=config.CURVE_SPEED):
        """
        Sağa kavis

        Args:
            speed (float): Motor hızı (0.0 - 1.0)
        """
        if self.last_movement != "curve_right":
            logger.debug(f"Sağa kavis başlatılıyor. Hız: {speed}")
            self.last_movement = "curve_right"

        # Sağa kavis için sağ motor hızını azalt
        right_speed = speed * 0.4  # Daha yumuşak dönüş için 0.3 yerine 0.4
        self.set_speeds(speed, right_speed)
        self.left_motor.forward()
        self.right_motor.forward()

    def stop(self):
        """
        Motorları durdur
        """
        if self.last_movement != "stop":
            logger.debug("Motorlar durduruluyor")
            self.last_movement = "stop"

        self.set_speeds(0, 0)
        self.left_motor.stop()
        self.right_motor.stop()

    def smooth_stop(self, duration=1.0):
        """
        Motorları kademeli olarak durdur

        Args:
            duration (float): Durma süresi (saniye)
        """
        logger.debug(f"Kademeli durma başlatılıyor. Süre: {duration} saniye")

        # Mevcut hızları al
        left_speed = self.last_left_speed
        right_speed = self.last_right_speed

        # Hızlar zaten sıfırsa bir şey yapma
        if left_speed == 0 and right_speed == 0:
            return

        # Kademeli olarak hızı azalt
        steps = 10
        step_time = duration / steps

        for i in range(steps):
            factor = 1.0 - ((i + 1) / steps)
            self.set_speeds(left_speed * factor, right_speed * factor)
            time.sleep(step_time)

        # Tamamen durdur
        self.stop()

    def cleanup(self):
        """
        GPIO pinlerini temizle
        """
        # GPIO kullanılabilirliğini kontrol et
        if not hasattr(self, 'gpio_ok') or not self.gpio_ok:
            logger.warning("GPIO kullanılamıyor. Temizleme işlemi yapılmadı.")
            return

        logger.info("Motor GPIO pinleri temizleniyor")
        try:
            self.stop()
            self.left_ena.close()
            self.right_ena.close()
            self.left_motor.close()
            self.right_motor.close()
            logger.info("Motor GPIO pinleri temizlendi")
        except Exception as e:
            logger.error(f"GPIO temizleme hatası: {e}")
