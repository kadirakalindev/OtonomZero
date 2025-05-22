# Raspberry Pi 5 Kurulum Kılavuzu

Bu kılavuz, şerit takip eden robot projesini Raspberry Pi 5 üzerinde çalıştırmak için gerekli adımları içerir.

## 1. Sistem Güncellemesi

İlk olarak, Raspberry Pi işletim sistemini güncelleyin:

```bash
sudo apt update
sudo apt upgrade -y
```

## 2. Gerekli Sistem Paketlerinin Kurulumu

Projenin çalışması için gerekli sistem paketlerini yükleyin:

```bash
# libcamera ve picamera2 için gerekli paketler
sudo apt install -y python3-libcamera python3-kms++ python3-picamera2

# OpenCV için gerekli paketler
sudo apt install -y python3-opencv

# GPIO kontrol paketleri
sudo apt install -y python3-gpiozero python3-rpi.gpio

# Diğer gerekli paketler
sudo apt install -y python3-pip python3-numpy
```

## 3. Python Paketlerinin Kurulumu

Gerekli Python paketlerini pip ile yükleyin:

```bash
# requirements.txt dosyasından paketleri yükle
pip3 install -r requirements.txt
```

## 4. Kamera Ayarları

Raspberry Pi kamerasının doğru çalıştığından emin olun:

```bash
# Kamera arayüzünü etkinleştir
sudo raspi-config
# Interface Options -> Camera -> Enable seçin

# Kamerayı test et
libcamera-hello
```

## 5. GPIO Pinlerinin Kontrolü

GPIO pinlerinin doğru çalıştığından emin olun:

```bash
# GPIO pinlerini test et
python3 -c "from gpiozero import LED; led = LED(17); led.on(); import time; time.sleep(1); led.off()"
```

## 6. Projeyi Çalıştırma

Projeyi çalıştırmak için:

```bash
# Normal mod
python3 main.py

# Debug modu (görüntü kaydetme ve detaylı loglama)
export DEBUG_MODE=true
python3 main.py
```

## 7. Sorun Giderme

### "No module named 'libcamera'" Hatası

Bu hata, libcamera modülünün doğru şekilde kurulmadığını gösterir:

```bash
# Çözüm
sudo apt install -y python3-libcamera
sudo apt install -y python3-picamera2
```

### "No module named 'cv2'" Hatası

OpenCV modülünün doğru şekilde kurulmadığını gösterir:

```bash
# Çözüm
sudo apt install -y python3-opencv
```

### "No module named 'gpiozero'" Hatası

GPIO kontrol modülünün doğru şekilde kurulmadığını gösterir:

```bash
# Çözüm
sudo apt install -y python3-gpiozero python3-rpi.gpio
```

### "No module named 'loguru'" Hatası

Loguru modülünün doğru şekilde kurulmadığını gösterir:

```bash
# Çözüm
pip3 install loguru
```

### Kamera Erişim Hatası

Kamera erişim hatası alırsanız:

```bash
# Çözüm
sudo usermod -a -G video $USER
# Oturumu kapatıp yeniden açın
```

### GPIO Erişim Hatası

GPIO erişim hatası alırsanız:

```bash
# Çözüm
sudo usermod -a -G gpio $USER
# Oturumu kapatıp yeniden açın
```

## 8. Otomatik Başlatma Ayarları

Robotun Raspberry Pi açıldığında otomatik olarak çalışmasını istiyorsanız:

```bash
# systemd servis dosyası oluştur
sudo nano /etc/systemd/system/line-follower.service
```

Aşağıdaki içeriği ekleyin:

```
[Unit]
Description=Line Following Robot
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/OtonomZero/main.py
WorkingDirectory=/home/pi/OtonomZero
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

Servisi etkinleştirin:

```bash
sudo systemctl enable line-follower.service
sudo systemctl start line-follower.service
```

## 9. Performans İpuçları

- Raspberry Pi'nin aşırı ısınmasını önlemek için soğutucu kullanın
- Yeterli güç kaynağı kullandığınızdan emin olun (en az 3A, 5V)
- Kamera çözünürlüğünü düşürerek performansı artırabilirsiniz
- Debug modunu sadece geliştirme sırasında kullanın, normal çalışmada kapatın
