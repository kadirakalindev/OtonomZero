#!/usr/bin/env python3
"""
GPIO pin testi - Raspberry Pi 5 için
"""

import time
import sys
import os

# Loglama için basit fonksiyon
def log(message):
    print(f"[TEST] {message}")

def test_with_rpi_gpio():
    """
    RPi.GPIO kütüphanesi ile GPIO pinlerini test eder
    """
    try:
        import RPi.GPIO as GPIO
        log("RPi.GPIO kütüphanesi başarıyla içe aktarıldı")
        
        # Pin numaraları (fiziksel pin numaraları - BOARD)
        LEFT_MOTOR_ENA = 12
        LEFT_MOTOR_IN1 = 16
        LEFT_MOTOR_IN2 = 18
        RIGHT_MOTOR_ENA = 32
        RIGHT_MOTOR_IN1 = 36
        RIGHT_MOTOR_IN2 = 38
        
        # BOARD pin numaralandırması kullan
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        log("BOARD pin numaralandırması kullanılıyor")
        
        # Pin numaralarını göster
        log(f"Sol motor pinleri: ENA={LEFT_MOTOR_ENA}, IN1={LEFT_MOTOR_IN1}, IN2={LEFT_MOTOR_IN2}")
        log(f"Sağ motor pinleri: ENA={RIGHT_MOTOR_ENA}, IN1={RIGHT_MOTOR_IN1}, IN2={RIGHT_MOTOR_IN2}")
        
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
        log("Motor testi başlıyor...")
        
        # Motorları durdur
        log("Motorlar durduruluyor...")
        left_pwm.ChangeDutyCycle(0)
        right_pwm.ChangeDutyCycle(0)
        GPIO.output(LEFT_MOTOR_IN1, GPIO.LOW)
        GPIO.output(LEFT_MOTOR_IN2, GPIO.LOW)
        GPIO.output(RIGHT_MOTOR_IN1, GPIO.LOW)
        GPIO.output(RIGHT_MOTOR_IN2, GPIO.LOW)
        time.sleep(1)
        
        # İleri hareket
        log("İleri hareket...")
        left_pwm.ChangeDutyCycle(50)  # %50 hız
        right_pwm.ChangeDutyCycle(50)  # %50 hız
        GPIO.output(LEFT_MOTOR_IN1, GPIO.HIGH)
        GPIO.output(LEFT_MOTOR_IN2, GPIO.LOW)
        GPIO.output(RIGHT_MOTOR_IN1, GPIO.HIGH)
        GPIO.output(RIGHT_MOTOR_IN2, GPIO.LOW)
        time.sleep(2)
        
        # Motorları durdur
        log("Motorlar durduruluyor...")
        left_pwm.ChangeDutyCycle(0)
        right_pwm.ChangeDutyCycle(0)
        GPIO.output(LEFT_MOTOR_IN1, GPIO.LOW)
        GPIO.output(LEFT_MOTOR_IN2, GPIO.LOW)
        GPIO.output(RIGHT_MOTOR_IN1, GPIO.LOW)
        GPIO.output(RIGHT_MOTOR_IN2, GPIO.LOW)
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

def test_with_gpiozero():
    """
    gpiozero kütüphanesi ile GPIO pinlerini test eder
    """
    try:
        from gpiozero import LED, Motor, Device
        log("gpiozero kütüphanesi başarıyla içe aktarıldı")
        
        # BCM pin numaraları
        BCM_LEFT_MOTOR_ENA = 18  # GPIO18 (BOARD 12)
        BCM_LEFT_MOTOR_IN1 = 23  # GPIO23 (BOARD 16)
        BCM_LEFT_MOTOR_IN2 = 24  # GPIO24 (BOARD 18)
        BCM_RIGHT_MOTOR_ENA = 12  # GPIO12 (BOARD 32)
        BCM_RIGHT_MOTOR_IN1 = 16  # GPIO16 (BOARD 36)
        BCM_RIGHT_MOTOR_IN2 = 20  # GPIO20 (BOARD 38)
        
        # Pin numaralarını göster
        log(f"Sol motor pinleri (BCM): ENA={BCM_LEFT_MOTOR_ENA}, IN1={BCM_LEFT_MOTOR_IN1}, IN2={BCM_LEFT_MOTOR_IN2}")
        log(f"Sağ motor pinleri (BCM): ENA={BCM_RIGHT_MOTOR_ENA}, IN1={BCM_RIGHT_MOTOR_IN1}, IN2={BCM_RIGHT_MOTOR_IN2}")
        
        # LED'leri kullanarak pinleri test et
        log("LED'ler ile pin testi...")
        
        # Sol motor pinleri
        left_ena_led = LED(BCM_LEFT_MOTOR_ENA)
        left_in1_led = LED(BCM_LEFT_MOTOR_IN1)
        left_in2_led = LED(BCM_LEFT_MOTOR_IN2)
        
        # Sağ motor pinleri
        right_ena_led = LED(BCM_RIGHT_MOTOR_ENA)
        right_in1_led = LED(BCM_RIGHT_MOTOR_IN1)
        right_in2_led = LED(BCM_RIGHT_MOTOR_IN2)
        
        # LED'leri sırayla yak ve söndür
        log("Sol motor ENA pin testi...")
        left_ena_led.on()
        time.sleep(0.5)
        left_ena_led.off()
        
        log("Sol motor IN1 pin testi...")
        left_in1_led.on()
        time.sleep(0.5)
        left_in1_led.off()
        
        log("Sol motor IN2 pin testi...")
        left_in2_led.on()
        time.sleep(0.5)
        left_in2_led.off()
        
        log("Sağ motor ENA pin testi...")
        right_ena_led.on()
        time.sleep(0.5)
        right_ena_led.off()
        
        log("Sağ motor IN1 pin testi...")
        right_in1_led.on()
        time.sleep(0.5)
        right_in1_led.off()
        
        log("Sağ motor IN2 pin testi...")
        right_in2_led.on()
        time.sleep(0.5)
        right_in2_led.off()
        
        # Temizlik
        log("Temizlik yapılıyor...")
        left_ena_led.close()
        left_in1_led.close()
        left_in2_led.close()
        right_ena_led.close()
        right_in1_led.close()
        right_in2_led.close()
        
        log("LED testi tamamlandı")
        return True
        
    except Exception as e:
        log(f"gpiozero ile LED testi başarısız: {e}")
        return False

if __name__ == "__main__":
    log("GPIO pin testi başlatılıyor...")
    
    # Kullanıcı root mu kontrol et
    if os.geteuid() != 0:
        log("UYARI: Bu betik root yetkileri gerektirebilir. 'sudo python3 test_gpio.py' komutu ile çalıştırın.")
    
    # Önce gpiozero ile dene
    log("gpiozero ile test deneniyor...")
    if test_with_gpiozero():
        log("gpiozero ile LED testi başarılı")
    else:
        log("gpiozero ile LED testi başarısız")
    
    # Sonra RPi.GPIO ile dene
    log("RPi.GPIO ile test deneniyor...")
    if test_with_rpi_gpio():
        log("RPi.GPIO ile motor testi başarılı")
    else:
        log("RPi.GPIO ile motor testi başarısız")
