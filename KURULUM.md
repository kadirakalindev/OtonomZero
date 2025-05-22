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
sudo apt install -y python3-libcamera python3-kms++ python3-picamera2 libcamera-apps

# OpenCV için gerekli paketler
sudo apt install -y python3-opencv

# GPIO kontrol paketleri
sudo apt install -y python3-gpiozero python3-pigpio python3-rpi.gpio

# Diğer gerekli paketler
sudo apt install -y python3-pip python3-numpy

# pigpio daemon'ı başlat (daha iyi motor kontrolü için)
sudo pigpiod
# Sistem başlangıcında otomatik başlatma
sudo systemctl enable pigpiod
```

> **Not:** Raspberry Pi 5'te picamera2 modülünün düzgün çalışması için libcamera-apps paketi gereklidir.

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
# veya
libcamera-jpeg -o test.jpg
```

Eğer kamera ile ilgili sorunlar yaşıyorsanız:

```bash
# Kamera kullanıcı izinlerini kontrol et
sudo usermod -a -G video $USER

# Kamera modülünü yeniden yükle
sudo modprobe -r bcm2835-v4l2
sudo modprobe bcm2835-v4l2

# Raspberry Pi'yi yeniden başlat
sudo reboot
```

Raspberry Pi 5 ve Pi Camera 3 için özel notlar:

1. Pi Camera 3 için doğru kablo kullandığınızdan emin olun
2. Kamera bağlantısını Raspberry Pi kapalıyken yapın
3. Kamera modülünün doğru takıldığından emin olun
4. libcamera-apps paketinin kurulu olduğundan emin olun

## 5. GPIO Pinlerinin Kontrolü

GPIO pinlerinin doğru çalıştığından emin olun:

```bash
# pigpio daemon'ın çalıştığını kontrol et
pgrep pigpiod
# Eğer çalışmıyorsa başlat
sudo pigpiod

# GPIO pinlerini test et (LED örneği)
python3 -c "from gpiozero import LED; led = LED(17); led.on(); import time; time.sleep(1); led.off()"

# Motor pinlerini test et (projedeki pinleri kullanarak)
python3 -c "from gpiozero import Motor; import time; motor = Motor(16, 18); motor.forward(); time.sleep(1); motor.stop()"
```

Eğer GPIO ile ilgili sorunlar yaşıyorsanız:

```bash
# GPIO kullanıcı izinlerini kontrol et
sudo usermod -a -G gpio $USER

# pigpio daemon'ı yeniden başlat
sudo systemctl restart pigpiod

# GPIO durumunu kontrol et
gpio readall  # WiringPi kurulu ise
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

### "No module named 'libcamera'" veya "No module named 'picamera2'" Hatası

Bu hatalar, libcamera veya picamera2 modüllerinin doğru şekilde kurulmadığını gösterir:

```bash
# Çözüm 1: Paketleri yeniden yükle
sudo apt update
sudo apt install -y --reinstall python3-libcamera python3-picamera2 libcamera-apps

# Kamera modülünü test et
libcamera-hello

# Python'da test et
python3 -c "from picamera2 import Picamera2; print('Picamera2 modülü başarıyla içe aktarıldı')"
```

Eğer hata devam ederse:

```bash
# Çözüm 2: Python modül yollarını kontrol et
python3 -c "import sys; print(sys.path)"

# Modüllerin konumunu bul
sudo find / -name "picamera2" -type d 2>/dev/null
sudo find / -name "libcamera" -type d 2>/dev/null

# Çözüm 3: Sembolik bağlantı oluştur
# Örnek: Modül /usr/lib/python3/dist-packages'da ise ve Python yolunda değilse
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
sudo ln -s /usr/lib/python3/dist-packages/picamera2 /usr/local/lib/python$PYTHON_VERSION/dist-packages/
sudo ln -s /usr/lib/python3/dist-packages/libcamera /usr/local/lib/python$PYTHON_VERSION/dist-packages/

# Çözüm 4: Sistem paketlerini güncelle
sudo apt update
sudo apt full-upgrade

# Raspberry Pi'yi yeniden başlat
sudo reboot
```

Eğer yukarıdaki çözümler işe yaramazsa, alternatif bir yaklaşım deneyin:

```bash
# Çözüm 5: Python sanal ortamı kullanmadan doğrudan sistem Python'ını kullan
sudo python3 main.py
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
sudo apt install -y python3-gpiozero python3-pigpio python3-rpi.gpio

# pigpio daemon'ı başlat
sudo pigpiod
sudo systemctl enable pigpiod

# Python'da test et
python3 -c "from gpiozero import LED, Motor; from gpiozero.pins.pigpio import PiGPIOFactory; print('GPIO modülleri başarıyla içe aktarıldı')"
```

### "ImportError: cannot import name 'Transform' from 'libcamera'" Hatası

Bu hata, libcamera modülünün eski bir sürümünün kurulu olduğunu gösterir:

```bash
# Çözüm
sudo apt update
sudo apt install -y --reinstall python3-libcamera libcamera-apps
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
