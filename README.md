# Şerit Takip Eden Robot (OtonomZero)

Bu proje, Raspberry Pi 5 ve Raspberry Pi Cam 3 kullanarak siyah zemin üzerinde beyaz şerit takip eden, engellere karşı manevra yapabilen ve zemin geçitlerinde durabilen bir robot uygulamasıdır.

## Özellikler

- Siyah zemin üzerinde beyaz şerit takibi
- Renk tabanlı engel algılama (turuncu ve sarı engeller)
- Engellere karşı akıllı manevra yapabilme
- Zemin geçitlerinde 5 saniye durma
- Kesik şerit takibi
- Gelişmiş motor kontrolü
- Kapsamlı loglama ve debug özellikleri
- GPIO kontrolü için gpiozero kütüphanesi kullanımı

## Donanım Gereksinimleri

- Raspberry Pi 5
- Raspberry Pi Camera 3
- Motor sürücü kartı (L298N veya benzeri)
- DC motorlar (2 adet, 12V 280 RPM)
- Güç kaynağı
- Robot şasisi (16cm genişlik, 25cm uzunluk, 23cm yükseklik)

## Pist Özellikleri

- Siyah zemin üzerinde beyaz şeritler
- Pist genişliği: 100cm
- Şerit genişliği: 40cm
- Kesik şerit uzunluğu: 20cm
- Kesikler arası mesafe: 20cm
- 90 derecelik virajlar ve U dönüşleri
- 2 adet zemin geçidi (yaya geçidi ve hemzemin geçit)

## Engel Özellikleri

- Sollama yapılması gereken araç: 20x30x25 cm (turuncu)
- Sol şerite yerleştirilen engel araç: 20x45x25 cm (sarı)

## GPIO Bağlantıları

- Sol Motorlar:
  - ENA: GPIO 12
  - IN1: GPIO 16
  - IN2: GPIO 18
- Sağ Motorlar:
  - ENA: GPIO 32
  - IN1: GPIO 36
  - IN2: GPIO 38

## Kurulum

Detaylı kurulum adımları için [KURULUM.md](KURULUM.md) dosyasını inceleyiniz.

Kısaca:

1. Sistem paketlerini yükleyin:

```bash
sudo apt update
sudo apt install -y python3-libcamera python3-picamera2 python3-opencv python3-gpiozero python3-rpi.gpio
```

2. Python paketlerini yükleyin:

```bash
pip3 install -r requirements.txt
```

3. Raspberry Pi kamera modülünü etkinleştirin:

```bash
sudo raspi-config
# Interface Options -> Camera -> Enable seçin
```

4. Programı çalıştırın:

```bash
# Normal mod
python3 main.py

# Debug modu
export DEBUG_MODE=true
python3 main.py
```

## Proje Yapısı

- `main.py`: Ana program dosyası
- `motor_controller.py`: Motor kontrol sınıfı
- `line_detector.py`: Şerit algılama sınıfı
- `obstacle_detector.py`: Engel algılama sınıfı
- `config.py`: Yapılandırma ayarları
- `robot_log.txt`: Log dosyası
- `debug_images/`: Debug görüntülerinin kaydedildiği klasör (debug modunda)

## Yapılandırma

`config.py` dosyasını düzenleyerek robot davranışını özelleştirebilirsiniz:

### Fiziksel Pist ve Araç Özellikleri
- Pist genişliği, şerit genişliği, kesik şerit özellikleri
- Robot boyutları ve kamera yüksekliği

### Motor Ayarları
- Motor hızları (DEFAULT_SPEED, TURN_SPEED, SLOW_SPEED, CURVE_SPEED)
- GPIO pin tanımlamaları

### Görüntü İşleme Ayarları
- Kamera çözünürlüğü ve frame rate
- ROI (İlgi Alanı) yüksekliği ve konumu
- Binary threshold değeri

### Şerit Takip Ayarları
- Merkez pozisyondan sapma eşiği
- Minimum şerit piksel sayısı

### Zemin Geçit Ayarları
- Durma süresi
- Algılama eşik değeri
- Yaklaşma mesafesi

### Engel Algılama Ayarları
- Algılama eşik değeri
- Kaçınma manevra süresi
- Engel renk aralıkları (HSV)

## Hata Ayıklama

Debug modunda çalıştırıldığında, program şu özellikleri sağlar:

1. Kapsamlı loglama (`robot_log.txt`)
2. Görüntü işleme sonuçlarının kaydedilmesi (`debug_images/` klasörü)
3. Detaylı motor hareketleri ve durum bilgileri

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.
