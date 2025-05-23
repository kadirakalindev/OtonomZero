"""
Motor kontrol sınıfı - Şerit takip eden robot için optimize edilmiş
Raspberry Pi 5 için uyumlu hale getirilmiştir
gpiozero kütüphanesi kullanılarak motor kontrolü sağlanır
BOARD pin numaralarının BCM karşılıklarını kullanır
pigpiod kullanılmadan sadece RPi.GPIO ile çalışır
"""

import time
import config
from loguru import logger

# GPIO modüllerini kontrol et ve içe aktar
try:
    # gpiozero kütüphanesinden gerekli sınıfları içe aktar
    from gpiozero import Motor, PWMOutputDevice, Device

    # RPi.GPIO pin fabrikasını içe aktar
    from gpiozero.pins.rpigpio import RPiGPIOFactory

    # RPi.GPIO kütüphanesini içe aktar
    try:
        import RPi.GPIO as GPIO
        GPIO.setwarnings(False)

        # BCM pin numaralandırma modunu ayarla
        GPIO.setmode(GPIO.BCM)
        logger.info("RPi.GPIO BCM pin numaralandırması ayarlandı")

        # RPiGPIOFactory kullan
        factory = RPiGPIOFactory()
        logger.info("RPiGPIO pin fabrikası BCM pin numaralandırması ile kullanılıyor")

        # Varsayılan pin fabrikasını ayarla
        Device.pin_factory = factory

        # BOARD-BCM dönüşüm bilgisini göster
        logger.info("BOARD-BCM pin dönüşümü:")
        for board_pin, bcm_pin in config.BOARD_TO_BCM.items():
            logger.info(f"BOARD {board_pin} -> BCM {bcm_pin}")
    except Exception as e:
        logger.warning(f"RPi.GPIO ayarlanamadı: {e}")
        logger.info("Varsayılan pin fabrikası kullanılıyor")
        factory = None

    logger.info("BCM pin numaralandırma modu kullanılıyor")

    GPIO_AVAILABLE = True
    logger.info("gpiozero kütüphanesi başarıyla yüklendi")
except ImportError as e:
    logger.error(f"gpiozero modülü yüklenemedi: {e}")
    logger.error("Lütfen şu komutları çalıştırın:")
    logger.error("sudo apt install -y python3-gpiozero python3-pigpio")
    logger.error("sudo pigpiod")  # pigpio daemon'ı başlat
    GPIO_AVAILABLE = False
    USE_BCM_CONVERSION = False

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
            # Hata durumunda bile temel özellikleri tanımla
            self.last_movement = "stop"
            self.last_left_speed = 0
            self.last_right_speed = 0
            return

        try:
            # BCM pin numaralarını kullan
            left_ena_pin = config.BCM_LEFT_MOTOR_ENA
            left_in1_pin = config.BCM_LEFT_MOTOR_IN1
            left_in2_pin = config.BCM_LEFT_MOTOR_IN2
            right_ena_pin = config.BCM_RIGHT_MOTOR_ENA
            right_in1_pin = config.BCM_RIGHT_MOTOR_IN1
            right_in2_pin = config.BCM_RIGHT_MOTOR_IN2

            # Kullanılan pin numaralarını logla
            logger.info(f"Sol motor pinleri (BCM): ENA={left_ena_pin}, IN1={left_in1_pin}, IN2={left_in2_pin}")
            logger.info(f"Sağ motor pinleri (BCM): ENA={right_ena_pin}, IN1={right_in1_pin}, IN2={right_in2_pin}")

            # Orijinal BOARD pin numaralarını da logla
            logger.info(f"Orijinal sol motor pinleri (BOARD): ENA={config.BOARD_LEFT_MOTOR_ENA}, IN1={config.BOARD_LEFT_MOTOR_IN1}, IN2={config.BOARD_LEFT_MOTOR_IN2}")
            logger.info(f"Orijinal sağ motor pinleri (BOARD): ENA={config.BOARD_RIGHT_MOTOR_ENA}, IN1={config.BOARD_RIGHT_MOTOR_IN1}, IN2={config.BOARD_RIGHT_MOTOR_IN2}")

            # Sol motor için PWM hız kontrolü ve motor nesnesi
            self.left_ena = PWMOutputDevice(left_ena_pin)
            self.left_motor = Motor(
                forward=left_in1_pin,
                backward=left_in2_pin,
                pwm=False  # PWM'i kendimiz kontrol edeceğiz
            )

            # Sağ motor için PWM hız kontrolü ve motor nesnesi
            self.right_ena = PWMOutputDevice(right_ena_pin)
            self.right_motor = Motor(
                forward=right_in1_pin,
                backward=right_in2_pin,
                pwm=False  # PWM'i kendimiz kontrol edeceğiz
            )

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

        # last_speed özelliklerinin tanımlı olduğundan emin ol
        if not hasattr(self, 'last_left_speed'):
            self.last_left_speed = 0

        if not hasattr(self, 'last_right_speed'):
            self.last_right_speed = 0

        # Hız değerlerini sınırla (0.0 - 1.0)
        left_speed = max(0.0, min(1.0, left_speed))
        right_speed = max(0.0, min(1.0, right_speed))

        # Değişim çok küçükse görmezden gel (titreşimi azaltmak için)
        if (abs(left_speed - self.last_left_speed) < 0.05 and
            abs(right_speed - self.last_right_speed) < 0.05):
            return

        try:
            # PWM değerlerini ayarla
            if hasattr(self, 'left_ena') and hasattr(self, 'right_ena'):
                self.left_ena.value = left_speed
                self.right_ena.value = right_speed

                # Son hızları güncelle
                self.last_left_speed = left_speed
                self.last_right_speed = right_speed

                # Debug log
                if left_speed > 0 or right_speed > 0:
                    logger.debug(f"Motor hızları: Sol: {left_speed:.2f}, Sağ: {right_speed:.2f}")
            else:
                logger.warning("Motor PWM nesneleri tanımlı değil")
        except Exception as e:
            logger.error(f"Motor hızları ayarlanırken hata: {e}")

    def forward(self, speed=config.DEFAULT_SPEED):
        """
        İleri hareket

        Args:
            speed (float): Motor hızı (0.0 - 1.0)
        """
        # GPIO kullanılabilirliğini kontrol et
        if not hasattr(self, 'gpio_ok') or not self.gpio_ok:
            logger.warning("GPIO kullanılamıyor. İleri hareket yapılamadı.")
            return

        # last_movement özelliğinin tanımlı olduğundan emin ol
        if not hasattr(self, 'last_movement'):
            self.last_movement = "stop"

        if self.last_movement != "forward":
            logger.debug(f"İleri hareket başlatılıyor. Hız: {speed}")
            self.last_movement = "forward"

        try:
            self.set_speeds(speed, speed)
            self.left_motor.forward()
            self.right_motor.forward()
        except Exception as e:
            logger.error(f"İleri hareket hatası: {e}")

    def backward(self, speed=config.DEFAULT_SPEED):
        """
        Geri hareket

        Args:
            speed (float): Motor hızı (0.0 - 1.0)
        """
        # GPIO kullanılabilirliğini kontrol et
        if not hasattr(self, 'gpio_ok') or not self.gpio_ok:
            logger.warning("GPIO kullanılamıyor. Geri hareket yapılamadı.")
            return

        # last_movement özelliğinin tanımlı olduğundan emin ol
        if not hasattr(self, 'last_movement'):
            self.last_movement = "stop"

        if self.last_movement != "backward":
            logger.debug(f"Geri hareket başlatılıyor. Hız: {speed}")
            self.last_movement = "backward"

        try:
            self.set_speeds(speed, speed)
            self.left_motor.backward()
            self.right_motor.backward()
        except Exception as e:
            logger.error(f"Geri hareket hatası: {e}")

    def turn_left(self, speed=config.TURN_SPEED):
        """
        Sola dönüş

        Args:
            speed (float): Motor hızı (0.0 - 1.0)
        """
        # GPIO kullanılabilirliğini kontrol et
        if not hasattr(self, 'gpio_ok') or not self.gpio_ok:
            logger.warning("GPIO kullanılamıyor. Sola dönüş yapılamadı.")
            return

        # last_movement özelliğinin tanımlı olduğundan emin ol
        if not hasattr(self, 'last_movement'):
            self.last_movement = "stop"

        if self.last_movement != "turn_left":
            logger.debug(f"Sola dönüş başlatılıyor. Hız: {speed}")
            self.last_movement = "turn_left"

        try:
            self.set_speeds(0, speed)
            self.left_motor.backward()
            self.right_motor.forward()
        except Exception as e:
            logger.error(f"Sola dönüş hatası: {e}")

    def turn_right(self, speed=config.TURN_SPEED):
        """
        Sağa dönüş

        Args:
            speed (float): Motor hızı (0.0 - 1.0)
        """
        # GPIO kullanılabilirliğini kontrol et
        if not hasattr(self, 'gpio_ok') or not self.gpio_ok:
            logger.warning("GPIO kullanılamıyor. Sağa dönüş yapılamadı.")
            return

        # last_movement özelliğinin tanımlı olduğundan emin ol
        if not hasattr(self, 'last_movement'):
            self.last_movement = "stop"

        if self.last_movement != "turn_right":
            logger.debug(f"Sağa dönüş başlatılıyor. Hız: {speed}")
            self.last_movement = "turn_right"

        try:
            self.set_speeds(speed, 0)
            self.left_motor.forward()
            self.right_motor.backward()
        except Exception as e:
            logger.error(f"Sağa dönüş hatası: {e}")

    def curve_left(self, speed=config.CURVE_SPEED):
        """
        Sola kavis

        Args:
            speed (float): Motor hızı (0.0 - 1.0)
        """
        # GPIO kullanılabilirliğini kontrol et
        if not hasattr(self, 'gpio_ok') or not self.gpio_ok:
            logger.warning("GPIO kullanılamıyor. Sola kavis yapılamadı.")
            return

        # last_movement özelliğinin tanımlı olduğundan emin ol
        if not hasattr(self, 'last_movement'):
            self.last_movement = "stop"

        if self.last_movement != "curve_left":
            logger.debug(f"Sola kavis başlatılıyor. Hız: {speed}")
            self.last_movement = "curve_left"

        try:
            # Sola kavis için sol motor hızını azalt
            left_speed = speed * 0.4  # Daha yumuşak dönüş için 0.3 yerine 0.4
            self.set_speeds(left_speed, speed)
            self.left_motor.forward()
            self.right_motor.forward()
        except Exception as e:
            logger.error(f"Sola kavis hatası: {e}")

    def curve_right(self, speed=config.CURVE_SPEED):
        """
        Sağa kavis

        Args:
            speed (float): Motor hızı (0.0 - 1.0)
        """
        # GPIO kullanılabilirliğini kontrol et
        if not hasattr(self, 'gpio_ok') or not self.gpio_ok:
            logger.warning("GPIO kullanılamıyor. Sağa kavis yapılamadı.")
            return

        # last_movement özelliğinin tanımlı olduğundan emin ol
        if not hasattr(self, 'last_movement'):
            self.last_movement = "stop"

        if self.last_movement != "curve_right":
            logger.debug(f"Sağa kavis başlatılıyor. Hız: {speed}")
            self.last_movement = "curve_right"

        try:
            # Sağa kavis için sağ motor hızını azalt
            right_speed = speed * 0.4  # Daha yumuşak dönüş için 0.3 yerine 0.4
            self.set_speeds(speed, right_speed)
            self.left_motor.forward()
            self.right_motor.forward()
        except Exception as e:
            logger.error(f"Sağa kavis hatası: {e}")

    def stop(self):
        """
        Motorları durdur
        """
        # GPIO kullanılabilirliğini kontrol et
        if not hasattr(self, 'gpio_ok') or not self.gpio_ok:
            logger.warning("GPIO kullanılamıyor. Motorlar durdurulamadı.")
            return

        # last_movement özelliğinin tanımlı olduğundan emin ol
        if not hasattr(self, 'last_movement'):
            self.last_movement = "stop"
            return

        if self.last_movement != "stop":
            logger.debug("Motorlar durduruluyor")
            self.last_movement = "stop"

        try:
            self.set_speeds(0, 0)
            self.left_motor.stop()
            self.right_motor.stop()
        except Exception as e:
            logger.error(f"Motor durdurma hatası: {e}")

    def smooth_stop(self, duration=1.0):
        """
        Motorları kademeli olarak durdur

        Args:
            duration (float): Durma süresi (saniye)
        """
        # GPIO kullanılabilirliğini kontrol et
        if not hasattr(self, 'gpio_ok') or not self.gpio_ok:
            logger.warning("GPIO kullanılamıyor. Kademeli durma yapılamadı.")
            return

        # last_movement ve last_speed özelliklerinin tanımlı olduğundan emin ol
        if not hasattr(self, 'last_movement'):
            self.last_movement = "stop"

        if not hasattr(self, 'last_left_speed'):
            self.last_left_speed = 0

        if not hasattr(self, 'last_right_speed'):
            self.last_right_speed = 0

        logger.debug(f"Kademeli durma başlatılıyor. Süre: {duration} saniye")

        try:
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
        except Exception as e:
            logger.error(f"Kademeli durma hatası: {e}")
            # Hata durumunda normal durdurma dene
            try:
                self.stop()
            except:
                pass

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
            # Önce motorları durdur
            self.stop()

            # Motor ve PWM nesnelerinin tanımlı olduğundan emin ol
            if hasattr(self, 'left_ena'):
                self.left_ena.close()

            if hasattr(self, 'right_ena'):
                self.right_ena.close()

            if hasattr(self, 'left_motor'):
                self.left_motor.close()

            if hasattr(self, 'right_motor'):
                self.right_motor.close()

            logger.info("Motor GPIO pinleri temizlendi")
        except Exception as e:
            logger.error(f"GPIO temizleme hatası: {e}")
