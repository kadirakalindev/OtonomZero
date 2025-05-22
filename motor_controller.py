"""
Motor kontrol sınıfı - Şerit takip eden robot için optimize edilmiş
Raspberry Pi 5 için uyumlu hale getirilmiştir
gpiozero kütüphanesi kullanılarak motor kontrolü sağlanır
Fiziksel pin numaraları (BOARD) kullanılarak yapılandırılmıştır
"""

import time
import config
from loguru import logger

# BOARD-BCM pin dönüşüm tablosu
BOARD_TO_BCM = {
    # Sol Motor
    12: 18,  # ENA -> GPIO18
    16: 23,  # IN1 -> GPIO23
    18: 24,  # IN2 -> GPIO24
    # Sağ Motor
    32: 12,  # ENA -> GPIO12
    36: 16,  # IN1 -> GPIO16
    38: 20,  # IN2 -> GPIO20
}

# GPIO modüllerini kontrol et ve içe aktar
try:
    # gpiozero kütüphanesinden gerekli sınıfları içe aktar
    from gpiozero import Motor, PWMOutputDevice, Device

    # Pin fabrikalarını içe aktar
    from gpiozero.pins.rpigpio import RPiGPIOFactory
    from gpiozero.pins.native import NativeFactory

    try:
        # pigpio daemon'ın çalıştığından emin ol
        import subprocess
        subprocess.run(["pgrep", "pigpiod"], check=True)
        from gpiozero.pins.pigpio import PiGPIOFactory

        # BOARD pin numaralandırması için özel fabrika oluştur
        # Not: PiGPIOFactory BOARD modunu doğrudan desteklemez, bu yüzden BCM pinlerini kullanacağız
        factory = PiGPIOFactory()
        logger.info("PiGPIO pin fabrikası BCM pin numaralandırması ile kullanılıyor")
    except (ImportError, subprocess.CalledProcessError):
        # RPi.GPIO kullanarak BOARD pin numaralandırması
        factory = RPiGPIOFactory(pin_mode="BOARD")
        logger.info("RPiGPIO pin fabrikası BOARD pin numaralandırması ile kullanılıyor")

    # Varsayılan pin fabrikasını ayarla
    Device.pin_factory = factory

    # Pin numaralandırma modunu kontrol et ve log'a yaz
    pin_mode = "BOARD" if hasattr(factory, "_mode") and factory._mode == "BOARD" else "BCM"
    logger.info(f"Pin numaralandırma modu: {pin_mode}")

    # Pin numaralandırma modu BCM ise, BOARD pinlerini BCM'ye çevireceğiz
    USE_BCM_CONVERSION = (pin_mode == "BCM")

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
            # Pin numaralandırma moduna göre pin numaralarını ayarla
            if 'USE_BCM_CONVERSION' in globals() and USE_BCM_CONVERSION:
                # BCM pin numaralandırması kullanılıyorsa, BOARD pinlerini BCM'ye çevir
                logger.info("BOARD pinleri BCM'ye çevriliyor...")
                left_ena_pin = BOARD_TO_BCM.get(config.LEFT_MOTOR_ENA, config.LEFT_MOTOR_ENA)
                left_in1_pin = BOARD_TO_BCM.get(config.LEFT_MOTOR_IN1, config.LEFT_MOTOR_IN1)
                left_in2_pin = BOARD_TO_BCM.get(config.LEFT_MOTOR_IN2, config.LEFT_MOTOR_IN2)
                right_ena_pin = BOARD_TO_BCM.get(config.RIGHT_MOTOR_ENA, config.RIGHT_MOTOR_ENA)
                right_in1_pin = BOARD_TO_BCM.get(config.RIGHT_MOTOR_IN1, config.RIGHT_MOTOR_IN1)
                right_in2_pin = BOARD_TO_BCM.get(config.RIGHT_MOTOR_IN2, config.RIGHT_MOTOR_IN2)

                logger.info(f"Sol motor pinleri: ENA={left_ena_pin}(BCM), IN1={left_in1_pin}(BCM), IN2={left_in2_pin}(BCM)")
                logger.info(f"Sağ motor pinleri: ENA={right_ena_pin}(BCM), IN1={right_in1_pin}(BCM), IN2={right_in2_pin}(BCM)")
            else:
                # BOARD pin numaralandırması kullanılıyorsa, doğrudan fiziksel pinleri kullan
                left_ena_pin = config.LEFT_MOTOR_ENA
                left_in1_pin = config.LEFT_MOTOR_IN1
                left_in2_pin = config.LEFT_MOTOR_IN2
                right_ena_pin = config.RIGHT_MOTOR_ENA
                right_in1_pin = config.RIGHT_MOTOR_IN1
                right_in2_pin = config.RIGHT_MOTOR_IN2

                logger.info(f"Sol motor pinleri: ENA={left_ena_pin}(BOARD), IN1={left_in1_pin}(BOARD), IN2={left_in2_pin}(BOARD)")
                logger.info(f"Sağ motor pinleri: ENA={right_ena_pin}(BOARD), IN1={right_in1_pin}(BOARD), IN2={right_in2_pin}(BOARD)")

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
