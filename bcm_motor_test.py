#!/usr/bin/env python3
"""
BCM Motor Testi - BOARD pin numaralarının BCM karşılıklarını kullanarak motorları test eder
"""

import time
import sys
import os

# Loglama için basit fonksiyon
def log(message):
    print(f"[TEST] {message}")

# BOARD-BCM Pin Dönüşüm Tablosu
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

# BOARD Pin Numaraları (Fiziksel pin numaraları - bize verilen)
BOARD_LEFT_MOTOR_ENA = 12
BOARD_LEFT_MOTOR_IN1 = 16
BOARD_LEFT_MOTOR_IN2 = 18
BOARD_RIGHT_MOTOR_ENA = 32
BOARD_RIGHT_MOTOR_IN1 = 36
BOARD_RIGHT_MOTOR_IN2 = 38

# BCM Pin Numaraları (GPIO numaraları - kullanacağımız)
BCM_LEFT_MOTOR_ENA = BOARD_TO_BCM[BOARD_LEFT_MOTOR_ENA]   # GPIO18
BCM_LEFT_MOTOR_IN1 = BOARD_TO_BCM[BOARD_LEFT_MOTOR_IN1]   # GPIO23
BCM_LEFT_MOTOR_IN2 = BOARD_TO_BCM[BOARD_LEFT_MOTOR_IN2]   # GPIO24
BCM_RIGHT_MOTOR_ENA = BOARD_TO_BCM[BOARD_RIGHT_MOTOR_ENA] # GPIO12
BCM_RIGHT_MOTOR_IN1 = BOARD_TO_BCM[BOARD_RIGHT_MOTOR_IN1] # GPIO16
BCM_RIGHT_MOTOR_IN2 = BOARD_TO_BCM[BOARD_RIGHT_MOTOR_IN2] # GPIO20

def test_with_gpiozero():
    """
    gpiozero kütüphanesi ile BCM pin numaralarını kullanarak motorları test eder
    """
    try:
        from gpiozero import Motor, PWMOutputDevice, Device
        from gpiozero.pins.rpigpio import RPiGPIOFactory
        import RPi.GPIO as GPIO
        
        log("gpiozero ve RPi.GPIO kütüphaneleri başarıyla içe aktarıldı")
        
        # BCM pin numaralandırması ayarla
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        log("BCM pin numaralandırması ayarlandı")
        
        # RPiGPIOFactory kullan
        factory = RPiGPIOFactory()
        Device.pin_factory = factory
        
        # BOARD-BCM dönüşüm bilgisini göster
        log("BOARD-BCM pin dönüşümü:")
        for board_pin, bcm_pin in BOARD_TO_BCM.items():
            log(f"BOARD {board_pin} -> BCM {bcm_pin}")
        
        # Pin numaralarını göster
        log(f"Sol motor pinleri (BCM): ENA={BCM_LEFT_MOTOR_ENA}, IN1={BCM_LEFT_MOTOR_IN1}, IN2={BCM_LEFT_MOTOR_IN2}")
        log(f"Sağ motor pinleri (BCM): ENA={BCM_RIGHT_MOTOR_ENA}, IN1={BCM_RIGHT_MOTOR_IN1}, IN2={BCM_RIGHT_MOTOR_IN2}")
        
        # Sol motor için PWM hız kontrolü ve motor nesnesi
        left_ena = PWMOutputDevice(BCM_LEFT_MOTOR_ENA)
        left_motor = Motor(
            forward=BCM_LEFT_MOTOR_IN1, 
            backward=BCM_LEFT_MOTOR_IN2,
            pwm=False  # PWM'i kendimiz kontrol edeceğiz
        )
        
        # Sağ motor için PWM hız kontrolü ve motor nesnesi
        right_ena = PWMOutputDevice(BCM_RIGHT_MOTOR_ENA)
        right_motor = Motor(
            forward=BCM_RIGHT_MOTOR_IN1, 
            backward=BCM_RIGHT_MOTOR_IN2,
            pwm=False  # PWM'i kendimiz kontrol edeceğiz
        )
        
        # Test sırası
        log("Motor testi başlıyor...")
        
        # Motorları durdur
        log("Motorlar durduruluyor...")
        left_ena.value = 0
        right_ena.value = 0
        left_motor.stop()
        right_motor.stop()
        time.sleep(1)
        
        # İleri hareket
        log("İleri hareket...")
        left_ena.value = 0.5  # %50 hız
        right_ena.value = 0.5  # %50 hız
        left_motor.forward()
        right_motor.forward()
        time.sleep(2)
        
        # Motorları durdur
        log("Motorlar durduruluyor...")
        left_ena.value = 0
        right_ena.value = 0
        left_motor.stop()
        right_motor.stop()
        time.sleep(1)
        
        # Geri hareket
        log("Geri hareket...")
        left_ena.value = 0.5  # %50 hız
        right_ena.value = 0.5  # %50 hız
        left_motor.backward()
        right_motor.backward()
        time.sleep(2)
        
        # Motorları durdur
        log("Motorlar durduruluyor...")
        left_ena.value = 0
        right_ena.value = 0
        left_motor.stop()
        right_motor.stop()
        time.sleep(1)
        
        # Sola dönüş
        log("Sola dönüş...")
        left_ena.value = 0
        right_ena.value = 0.5
        left_motor.backward()
        right_motor.forward()
        time.sleep(2)
        
        # Motorları durdur
        log("Motorlar durduruluyor...")
        left_ena.value = 0
        right_ena.value = 0
        left_motor.stop()
        right_motor.stop()
        time.sleep(1)
        
        # Sağa dönüş
        log("Sağa dönüş...")
        left_ena.value = 0.5
        right_ena.value = 0
        left_motor.forward()
        right_motor.backward()
        time.sleep(2)
        
        # Motorları durdur
        log("Motorlar durduruluyor...")
        left_ena.value = 0
        right_ena.value = 0
        left_motor.stop()
        right_motor.stop()
        
        # Temizlik
        log("Temizlik yapılıyor...")
        left_ena.close()
        right_ena.close()
        left_motor.close()
        right_motor.close()
        GPIO.cleanup()
        
        log("Motor testi tamamlandı")
        return True
        
    except Exception as e:
        log(f"gpiozero ile motor testi başarısız: {e}")
        return False

def test_with_rpi_gpio():
    """
    RPi.GPIO kütüphanesi ile BCM pin numaralarını kullanarak motorları test eder
    """
    try:
        import RPi.GPIO as GPIO
        
        log("RPi.GPIO kütüphanesi başarıyla içe aktarıldı")
        
        # BCM pin numaralandırması kullan
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        log("BCM pin numaralandırması kullanılıyor")
        
        # Pin numaralarını göster
        log(f"Sol motor pinleri (BCM): ENA={BCM_LEFT_MOTOR_ENA}, IN1={BCM_LEFT_MOTOR_IN1}, IN2={BCM_LEFT_MOTOR_IN2}")
        log(f"Sağ motor pinleri (BCM): ENA={BCM_RIGHT_MOTOR_ENA}, IN1={BCM_RIGHT_MOTOR_IN1}, IN2={BCM_RIGHT_MOTOR_IN2}")
        
        # Pinleri çıkış olarak ayarla
        GPIO.setup(BCM_LEFT_MOTOR_ENA, GPIO.OUT)
        GPIO.setup(BCM_LEFT_MOTOR_IN1, GPIO.OUT)
        GPIO.setup(BCM_LEFT_MOTOR_IN2, GPIO.OUT)
        GPIO.setup(BCM_RIGHT_MOTOR_ENA, GPIO.OUT)
        GPIO.setup(BCM_RIGHT_MOTOR_IN1, GPIO.OUT)
        GPIO.setup(BCM_RIGHT_MOTOR_IN2, GPIO.OUT)
        
        # PWM nesneleri oluştur
        left_pwm = GPIO.PWM(BCM_LEFT_MOTOR_ENA, 100)  # 100 Hz
        right_pwm = GPIO.PWM(BCM_RIGHT_MOTOR_ENA, 100)  # 100 Hz
        
        # PWM başlat
        left_pwm.start(0)  # %0 duty cycle
        right_pwm.start(0)  # %0 duty cycle
        
        # Test sırası
        log("Motor testi başlıyor...")
        
        # Motorları durdur
        log("Motorlar durduruluyor...")
        left_pwm.ChangeDutyCycle(0)
        right_pwm.ChangeDutyCycle(0)
        GPIO.output(BCM_LEFT_MOTOR_IN1, GPIO.LOW)
        GPIO.output(BCM_LEFT_MOTOR_IN2, GPIO.LOW)
        GPIO.output(BCM_RIGHT_MOTOR_IN1, GPIO.LOW)
        GPIO.output(BCM_RIGHT_MOTOR_IN2, GPIO.LOW)
        time.sleep(1)
        
        # İleri hareket
        log("İleri hareket...")
        left_pwm.ChangeDutyCycle(50)  # %50 hız
        right_pwm.ChangeDutyCycle(50)  # %50 hız
        GPIO.output(BCM_LEFT_MOTOR_IN1, GPIO.HIGH)
        GPIO.output(BCM_LEFT_MOTOR_IN2, GPIO.LOW)
        GPIO.output(BCM_RIGHT_MOTOR_IN1, GPIO.HIGH)
        GPIO.output(BCM_RIGHT_MOTOR_IN2, GPIO.LOW)
        time.sleep(2)
        
        # Motorları durdur
        log("Motorlar durduruluyor...")
        left_pwm.ChangeDutyCycle(0)
        right_pwm.ChangeDutyCycle(0)
        GPIO.output(BCM_LEFT_MOTOR_IN1, GPIO.LOW)
        GPIO.output(BCM_LEFT_MOTOR_IN2, GPIO.LOW)
        GPIO.output(BCM_RIGHT_MOTOR_IN1, GPIO.LOW)
        GPIO.output(BCM_RIGHT_MOTOR_IN2, GPIO.LOW)
        time.sleep(1)
        
        # Temizlik
        log("Temizlik yapılıyor...")
        left_pwm.stop()
        right_pwm.stop()
        GPIO.cleanup()
        
        log("Motor testi tamamlandı")
        return True
        
    except Exception as e:
        log(f"RPi.GPIO ile motor testi başarısız: {e}")
        return False

if __name__ == "__main__":
    log("BCM Motor Testi başlatılıyor...")
    
    # Kullanıcı root mu kontrol et
    if os.geteuid() != 0:
        log("UYARI: Bu betik root yetkileri gerektirebilir. 'sudo python3 bcm_motor_test.py' komutu ile çalıştırın.")
    
    # Önce gpiozero ile dene
    log("gpiozero ile test deneniyor...")
    if test_with_gpiozero():
        log("gpiozero ile motor testi başarılı")
    else:
        # gpiozero başarısız olursa RPi.GPIO ile dene
        log("RPi.GPIO ile test deneniyor...")
        if test_with_rpi_gpio():
            log("RPi.GPIO ile motor testi başarılı")
        else:
            log("Tüm motor testleri başarısız!")
