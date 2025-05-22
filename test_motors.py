#!/usr/bin/env python3
"""
Motor test betiği - Fiziksel pin numaralarını (BOARD) kullanarak motorları test eder
"""

import time
import sys
from loguru import logger

# Loglama ayarları
logger.remove()
logger.add(sys.stderr, level="INFO")

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

# Pin numaraları (fiziksel pin numaraları - BOARD)
LEFT_MOTOR_ENA = 12
LEFT_MOTOR_IN1 = 16
LEFT_MOTOR_IN2 = 18
RIGHT_MOTOR_ENA = 32
RIGHT_MOTOR_IN1 = 36
RIGHT_MOTOR_IN2 = 38

def test_with_gpiozero():
    """
    gpiozero kütüphanesi ile motorları test eder
    """
    try:
        from gpiozero import Motor, PWMOutputDevice, Device
        from gpiozero.pins.rpigpio import RPiGPIOFactory
        
        logger.info("gpiozero kütüphanesi başarıyla içe aktarıldı")
        
        # BOARD pin numaralandırması için fabrika oluştur
        factory = RPiGPIOFactory(pin_mode="BOARD")
        Device.pin_factory = factory
        
        logger.info("BOARD pin numaralandırması kullanılıyor")
        logger.info(f"Sol motor pinleri: ENA={LEFT_MOTOR_ENA}, IN1={LEFT_MOTOR_IN1}, IN2={LEFT_MOTOR_IN2}")
        logger.info(f"Sağ motor pinleri: ENA={RIGHT_MOTOR_ENA}, IN1={RIGHT_MOTOR_IN1}, IN2={RIGHT_MOTOR_IN2}")
        
        # Sol motor için PWM hız kontrolü ve motor nesnesi
        left_ena = PWMOutputDevice(LEFT_MOTOR_ENA)
        left_motor = Motor(
            forward=LEFT_MOTOR_IN1, 
            backward=LEFT_MOTOR_IN2,
            pwm=False  # PWM'i kendimiz kontrol edeceğiz
        )
        
        # Sağ motor için PWM hız kontrolü ve motor nesnesi
        right_ena = PWMOutputDevice(RIGHT_MOTOR_ENA)
        right_motor = Motor(
            forward=RIGHT_MOTOR_IN1, 
            backward=RIGHT_MOTOR_IN2,
            pwm=False  # PWM'i kendimiz kontrol edeceğiz
        )
        
        # Test sırası
        logger.info("Motor testi başlıyor...")
        
        # Motorları durdur
        logger.info("Motorlar durduruluyor...")
        left_ena.value = 0
        right_ena.value = 0
        left_motor.stop()
        right_motor.stop()
        time.sleep(1)
        
        # İleri hareket
        logger.info("İleri hareket...")
        left_ena.value = 0.5
        right_ena.value = 0.5
        left_motor.forward()
        right_motor.forward()
        time.sleep(2)
        
        # Motorları durdur
        logger.info("Motorlar durduruluyor...")
        left_ena.value = 0
        right_ena.value = 0
        left_motor.stop()
        right_motor.stop()
        time.sleep(1)
        
        # Geri hareket
        logger.info("Geri hareket...")
        left_ena.value = 0.5
        right_ena.value = 0.5
        left_motor.backward()
        right_motor.backward()
        time.sleep(2)
        
        # Motorları durdur
        logger.info("Motorlar durduruluyor...")
        left_ena.value = 0
        right_ena.value = 0
        left_motor.stop()
        right_motor.stop()
        time.sleep(1)
        
        # Sola dönüş
        logger.info("Sola dönüş...")
        left_ena.value = 0
        right_ena.value = 0.5
        left_motor.backward()
        right_motor.forward()
        time.sleep(2)
        
        # Motorları durdur
        logger.info("Motorlar durduruluyor...")
        left_ena.value = 0
        right_ena.value = 0
        left_motor.stop()
        right_motor.stop()
        time.sleep(1)
        
        # Sağa dönüş
        logger.info("Sağa dönüş...")
        left_ena.value = 0.5
        right_ena.value = 0
        left_motor.forward()
        right_motor.backward()
        time.sleep(2)
        
        # Motorları durdur
        logger.info("Motorlar durduruluyor...")
        left_ena.value = 0
        right_ena.value = 0
        left_motor.stop()
        right_motor.stop()
        
        # Temizlik
        logger.info("Temizlik yapılıyor...")
        left_ena.close()
        right_ena.close()
        left_motor.close()
        right_motor.close()
        
        logger.info("Motor testi tamamlandı")
        return True
        
    except Exception as e:
        logger.error(f"gpiozero ile motor testi başarısız: {e}")
        return False

def test_with_rpi_gpio():
    """
    RPi.GPIO kütüphanesi ile motorları test eder
    """
    try:
        import RPi.GPIO as GPIO
        
        logger.info("RPi.GPIO kütüphanesi başarıyla içe aktarıldı")
        
        # BOARD pin numaralandırması kullan
        GPIO.setmode(GPIO.BOARD)
        logger.info("BOARD pin numaralandırması kullanılıyor")
        
        # Pin numaralarını ayarla
        logger.info(f"Sol motor pinleri: ENA={LEFT_MOTOR_ENA}, IN1={LEFT_MOTOR_IN1}, IN2={LEFT_MOTOR_IN2}")
        logger.info(f"Sağ motor pinleri: ENA={RIGHT_MOTOR_ENA}, IN1={RIGHT_MOTOR_IN1}, IN2={RIGHT_MOTOR_IN2}")
        
        # Pinleri çıkış olarak ayarla
        GPIO.setup(LEFT_MOTOR_ENA, GPIO.OUT)
        GPIO.setup(LEFT_MOTOR_IN1, GPIO.OUT)
        GPIO.setup(LEFT_MOTOR_IN2, GPIO.OUT)
        GPIO.setup(RIGHT_MOTOR_ENA, GPIO.OUT)
        GPIO.setup(RIGHT_MOTOR_IN1, GPIO.OUT)
        GPIO.setup(RIGHT_MOTOR_IN2, GPIO.OUT)
        
        # PWM nesneleri oluştur
        left_pwm = GPIO.PWM(LEFT_MOTOR_ENA, 100)  # 100 Hz
        right_pwm = GPIO.PWM(RIGHT_MOTOR_ENA, 100)  # 100 Hz
        
        # PWM başlat
        left_pwm.start(0)  # %0 duty cycle
        right_pwm.start(0)  # %0 duty cycle
        
        # Test sırası
        logger.info("Motor testi başlıyor...")
        
        # Motorları durdur
        logger.info("Motorlar durduruluyor...")
        left_pwm.ChangeDutyCycle(0)
        right_pwm.ChangeDutyCycle(0)
        GPIO.output(LEFT_MOTOR_IN1, GPIO.LOW)
        GPIO.output(LEFT_MOTOR_IN2, GPIO.LOW)
        GPIO.output(RIGHT_MOTOR_IN1, GPIO.LOW)
        GPIO.output(RIGHT_MOTOR_IN2, GPIO.LOW)
        time.sleep(1)
        
        # İleri hareket
        logger.info("İleri hareket...")
        left_pwm.ChangeDutyCycle(50)  # %50 hız
        right_pwm.ChangeDutyCycle(50)  # %50 hız
        GPIO.output(LEFT_MOTOR_IN1, GPIO.HIGH)
        GPIO.output(LEFT_MOTOR_IN2, GPIO.LOW)
        GPIO.output(RIGHT_MOTOR_IN1, GPIO.HIGH)
        GPIO.output(RIGHT_MOTOR_IN2, GPIO.LOW)
        time.sleep(2)
        
        # Motorları durdur
        logger.info("Motorlar durduruluyor...")
        left_pwm.ChangeDutyCycle(0)
        right_pwm.ChangeDutyCycle(0)
        GPIO.output(LEFT_MOTOR_IN1, GPIO.LOW)
        GPIO.output(LEFT_MOTOR_IN2, GPIO.LOW)
        GPIO.output(RIGHT_MOTOR_IN1, GPIO.LOW)
        GPIO.output(RIGHT_MOTOR_IN2, GPIO.LOW)
        time.sleep(1)
        
        # Geri hareket
        logger.info("Geri hareket...")
        left_pwm.ChangeDutyCycle(50)  # %50 hız
        right_pwm.ChangeDutyCycle(50)  # %50 hız
        GPIO.output(LEFT_MOTOR_IN1, GPIO.LOW)
        GPIO.output(LEFT_MOTOR_IN2, GPIO.HIGH)
        GPIO.output(RIGHT_MOTOR_IN1, GPIO.LOW)
        GPIO.output(RIGHT_MOTOR_IN2, GPIO.HIGH)
        time.sleep(2)
        
        # Temizlik
        logger.info("Temizlik yapılıyor...")
        left_pwm.stop()
        right_pwm.stop()
        GPIO.cleanup()
        
        logger.info("Motor testi tamamlandı")
        return True
        
    except Exception as e:
        logger.error(f"RPi.GPIO ile motor testi başarısız: {e}")
        return False

if __name__ == "__main__":
    logger.info("Motor test betiği başlatılıyor...")
    
    # Önce gpiozero ile dene
    if test_with_gpiozero():
        logger.info("gpiozero ile motor testi başarılı")
    else:
        # gpiozero başarısız olursa RPi.GPIO ile dene
        logger.info("RPi.GPIO ile test deneniyor...")
        if test_with_rpi_gpio():
            logger.info("RPi.GPIO ile motor testi başarılı")
        else:
            logger.error("Tüm motor testleri başarısız!")
