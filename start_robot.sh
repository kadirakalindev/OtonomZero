#!/bin/bash
# Şerit takip eden robot başlatma betiği

# Renkli çıktı için
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Şerit Takip Eden Robot Başlatılıyor ===${NC}"

# Çalışma dizinini kontrol et
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"
echo -e "${GREEN}Çalışma dizini: $(pwd)${NC}"

# pigpio daemon'ı kontrol et
if ! pgrep pigpiod > /dev/null; then
    echo -e "${YELLOW}pigpio daemon çalışmıyor, başlatılıyor...${NC}"
    sudo pigpiod
    sleep 1
else
    echo -e "${GREEN}pigpio daemon zaten çalışıyor${NC}"
fi

# Kamera modülünü kontrol et
echo -e "${BLUE}Kamera modülü kontrol ediliyor...${NC}"
if ! libcamera-hello --list-cameras > /dev/null 2>&1; then
    echo -e "${RED}Kamera algılanamadı! Kamera bağlantısını kontrol edin.${NC}"
    echo -e "${YELLOW}Kamera olmadan devam edilecek...${NC}"
else
    echo -e "${GREEN}Kamera algılandı${NC}"
    libcamera-hello --list-cameras
fi

# Python modüllerini kontrol et
echo -e "${BLUE}Python modülleri kontrol ediliyor...${NC}"

# picamera2 modülünü kontrol et
if ! python3 -c "import picamera2" 2>/dev/null; then
    echo -e "${RED}picamera2 modülü bulunamadı!${NC}"
    echo -e "${YELLOW}Sembolik bağlantı oluşturuluyor...${NC}"
    
    # Python sürümünü al
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    
    # Modülün konumunu bul
    PICAMERA_PATH=$(sudo find /usr/lib -name "picamera2" -type d 2>/dev/null | head -n 1)
    
    if [ -n "$PICAMERA_PATH" ]; then
        echo -e "${GREEN}picamera2 modülü bulundu: $PICAMERA_PATH${NC}"
        # Hedef dizini oluştur
        sudo mkdir -p /usr/local/lib/python$PYTHON_VERSION/dist-packages/
        # Sembolik bağlantı oluştur
        sudo ln -sf $PICAMERA_PATH /usr/local/lib/python$PYTHON_VERSION/dist-packages/
        echo -e "${GREEN}Sembolik bağlantı oluşturuldu${NC}"
    else
        echo -e "${RED}picamera2 modülü bulunamadı! Lütfen yükleyin:${NC}"
        echo -e "${YELLOW}sudo apt install -y python3-picamera2 python3-libcamera libcamera-apps${NC}"
    fi
else
    echo -e "${GREEN}picamera2 modülü bulundu${NC}"
fi

# libcamera modülünü kontrol et
if ! python3 -c "import libcamera" 2>/dev/null; then
    echo -e "${RED}libcamera modülü bulunamadı!${NC}"
    echo -e "${YELLOW}Sembolik bağlantı oluşturuluyor...${NC}"
    
    # Python sürümünü al
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    
    # Modülün konumunu bul
    LIBCAMERA_PATH=$(sudo find /usr/lib -name "libcamera" -type d 2>/dev/null | head -n 1)
    
    if [ -n "$LIBCAMERA_PATH" ]; then
        echo -e "${GREEN}libcamera modülü bulundu: $LIBCAMERA_PATH${NC}"
        # Hedef dizini oluştur
        sudo mkdir -p /usr/local/lib/python$PYTHON_VERSION/dist-packages/
        # Sembolik bağlantı oluştur
        sudo ln -sf $LIBCAMERA_PATH /usr/local/lib/python$PYTHON_VERSION/dist-packages/
        echo -e "${GREEN}Sembolik bağlantı oluşturuldu${NC}"
    else
        echo -e "${RED}libcamera modülü bulunamadı! Lütfen yükleyin:${NC}"
        echo -e "${YELLOW}sudo apt install -y python3-picamera2 python3-libcamera libcamera-apps${NC}"
    fi
else
    echo -e "${GREEN}libcamera modülü bulundu${NC}"
fi

# Debug modu kontrolü
if [ "$1" == "--debug" ]; then
    echo -e "${YELLOW}Debug modu aktif${NC}"
    export DEBUG_MODE=true
else
    echo -e "${GREEN}Normal mod${NC}"
    export DEBUG_MODE=false
fi

# Programı başlat
echo -e "${BLUE}Program başlatılıyor...${NC}"
echo -e "${YELLOW}Çıkmak için CTRL+C tuşlarına basın${NC}"
python3 main.py

# Program sonlandığında
echo -e "${BLUE}Program sonlandı${NC}"
