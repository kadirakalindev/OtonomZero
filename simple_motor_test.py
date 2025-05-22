#!/usr/bin/env python3
"""
Basit motor testi - pigpiod kullanmadan sadece gpiozero ve RPi.GPIO ile
"""

import time
import sys
import os

# Loglama için basit fonksiyon
def log(message):
    print(f"[TEST] {message}")

# Pin numaraları
# BOARD pin numaraları (fiziksel pin numaraları)
BOARD_LEFT_MOTOR_ENA = 12
BOARD_LEFT_MOTOR_IN1 = 16
BOARD_LEFT_MOTOR_IN2 = 18
BOARD_RIGHT_MOTOR_ENA = 32
BOARD_RIGHT_MOTOR_IN1 = 36
BOARD_RIGHT_MOTOR_IN2 = 38

# BCM pin numaraları (GPIO numaraları)
BCM_LEFT_MOTOR_ENA = 18  # GPIO18 (BOARD 12)
BCM_LEFT_MOTOR_IN1 = 23  # GPIO23 (BOARD 16)
BCM_LEFT_MOTOR_IN2 = 24  # GPIO24 (BOARD 18)
BCM_RIGHT_MOTOR_ENA = 12  # GPIO12 (BOARD 32)
BCM_RIGHT_MOTOR_IN1 = 16  # GPIO16 (BOARD 36)
BCM_RIGHT_MOTOR_IN2 = 20  # GPIO20 (BOARD 38)

def test_with_gpiozero_board():
    """
    gpiozero kütüphanesi ile BOARD pin numaralandırması kullanarak motorları test eder
    """
    try:
        from gpiozero import Motor, PWMOutputDevice, Device
        from gpiozero.pins.rpigpio import RPiGPIOFactory
        import RPi.GPIO as GPIO
        
        log("gpiozero ve RPi.GPIO kütüphaneleri başarıyla içe aktarıldı")
        
        # BOARD pin numaralandırması ayarla
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        log("BOARD pin numaralandırması ayarlandı")
        
        # RPiGPIOFactory kullan
        factory = RPiGPIOFactory()
        Device.pin_factory = factory
        
        # Pin numaralarını göster
        log(f"Sol motor pinleri (BOARD): ENA={BOARD_LEFT_MOTOR_ENA}, IN1={BOARD_LEFT_MOTOR_IN1}, IN2={BOARD_LEFT_MOTOR_IN2}")
        log(f"Sağ motor pinleri (BOARD): ENA={BOARD_RIGHT_MOTOR_ENA}, IN1={BOARD_RIGHT_MOTOR_IN1}, IN2={BOARD_RIGHT_MOTOR_IN2}")
        
        # Sol motor için PWM hız kontrolü ve motor nesnesi
        left_ena = PWMOutputDevice(BOARD_LEFT_MOTOR_ENA)
        left_motor = Motor(
            forward=BOARD_LEFT_MOTOR_IN1, 
            backward=BOARD_LEFT_MOTOR_IN2,
            pwm=False  # PWM'i kendimiz kontrol edeceğiz
        )
        
        # Sağ motor için PWM hız kontrolü ve motor nesnesi
        right_ena = PWMOutputDevice(BOARD_RIGHT_MOTOR_ENA)
        right_motor = Motor(
            forward=BOARD_RIGHT_MOTOR_IN1, 
            backward=BOARD_RIGHT_MOTOR_IN2,
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

def test_with_gpiozero_bcm():
    """
    gpiozero kütüphanesi ile BCM pin numaralandırması kullanarak motorları test eder
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

if __name__ == "__main__":
    log("Basit motor testi başlatılıyor...")
    
    # Kullanıcı root mu kontrol et
    if os.geteuid() != 0:
        log("UYARI: Bu betik root yetkileri gerektirebilir. 'sudo python3 simple_motor_test.py' komutu ile çalıştırın.")
    
    # Önce BOARD pin numaralandırması ile dene
    log("BOARD pin numaralandırması ile test deneniyor...")
    if test_with_gpiozero_board():
        log("BOARD pin numaralandırması ile motor testi başarılı")
    else:
        log("BOARD pin numaralandırması ile motor testi başarısız")
        
        # BOARD başarısız olursa BCM ile dene
        log("BCM pin numaralandırması ile test deneniyor...")
        if test_with_gpiozero_bcm():
            log("BCM pin numaralandırması ile motor testi başarılı")
        else:
            log("BCM pin numaralandırması ile motor testi başarısız")
            log("Tüm testler başarısız!")
