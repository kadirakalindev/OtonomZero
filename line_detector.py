"""
Şerit algılama sınıfı - Siyah zemin üzerinde beyaz şerit için optimize edilmiş
"""

import cv2
import numpy as np
import config
import time

class LineDetector:
    def __init__(self):
        """
        Şerit algılama sınıfı başlatıcı
        """
        self.last_position = None
        self.last_detection_time = time.time()
        self.frame_width = config.CAMERA_RESOLUTION[0]
        self.frame_center = self.frame_width // 2
        self.roi_height = config.ROI_HEIGHT

        # Kesik şerit takibi için değişkenler
        self.line_lost_counter = 0
        self.max_line_lost_frames = 10  # Maksimum kayıp kare sayısı

        # Şerit genişliği piksel cinsinden (yaklaşık)
        # 40cm şerit genişliği, 100cm pist genişliği, 640px görüntü genişliği
        self.line_width_px = int((config.LANE_WIDTH / config.TRACK_WIDTH) * self.frame_width)

    def detect_line(self, frame):
        """
        Görüntüden şerit pozisyonunu tespit eder

        Args:
            frame: Kameradan alınan görüntü

        Returns:
            line_position: Şeridin merkeze göre pozisyonu (negatif: sol, pozitif: sağ)
            processed_frame: İşlenmiş görüntü (debug için)
        """
        # Görüntüyü gri tonlamaya çevir
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # İlgi alanını (ROI) belirle - alt kısım
        height, width = gray.shape
        roi = gray[height - self.roi_height:height, 0:width]

        # Görüntüyü bulanıklaştır
        blur = cv2.GaussianBlur(roi, (5, 5), 0)

        # İkili (binary) görüntüye çevir - beyaz şerit için normal threshold
        _, binary = cv2.threshold(blur, config.BINARY_THRESHOLD, 255, cv2.THRESH_BINARY)

        # Gürültüyü azalt
        kernel = np.ones((3, 3), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

        # Şerit pozisyonunu bul
        line_position = self._find_line_position(binary)

        # İşlenmiş görüntüyü hazırla (debug için)
        processed_frame = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)

        # Merkez çizgisini çiz
        cv2.line(processed_frame, (self.frame_center, 0), (self.frame_center, self.roi_height), (0, 0, 255), 2)

        # Tespit edilen şerit pozisyonunu çiz
        if line_position is not None:
            position = self.frame_center + line_position
            cv2.line(processed_frame, (position, 0), (position, self.roi_height), (0, 255, 0), 2)

            # Şerit genişliğini göster
            half_width = self.line_width_px // 2
            cv2.rectangle(processed_frame,
                         (position - half_width, self.roi_height // 2),
                         (position + half_width, self.roi_height // 2 + 20),
                         (0, 255, 255), 2)

        return line_position, processed_frame

    def _find_line_position(self, binary_image):
        """
        İkili görüntüden şerit pozisyonunu hesaplar

        Args:
            binary_image: İkili görüntü

        Returns:
            position: Şeridin merkeze göre pozisyonu (negatif: sol, pozitif: sağ)
        """
        # Görüntünün alt yarısını kullan
        height = binary_image.shape[0]
        half_height = height // 2

        # Her sütundaki beyaz pikselleri say
        histogram = np.sum(binary_image[half_height:, :], axis=0)

        # Minimum piksel sayısı kontrolü
        if np.max(histogram) < config.LINE_DETECTION_MIN_PIXELS:
            self.line_lost_counter += 1
            if self.line_lost_counter > self.max_line_lost_frames:
                # Uzun süre şerit bulunamadı, son pozisyonu sıfırla
                self.last_position = None
                return None
            elif self.last_position is not None:
                # Kısa süreli kayıp, son bilinen pozisyonu kullan
                return self.last_position
            else:
                return None

        # Şerit bulundu, sayacı sıfırla
        self.line_lost_counter = 0

        # Şerit pozisyonunu bul (maksimum beyaz piksel)
        line_x = np.argmax(histogram)

        # Merkeze göre pozisyonu hesapla
        position = line_x - self.frame_center

        # Ani değişimleri yumuşat (son pozisyon varsa)
        if self.last_position is not None:
            # Pozisyon değişimini sınırla
            max_change = 20  # Maksimum piksel değişimi
            if abs(position - self.last_position) > max_change:
                # Değişimi sınırla
                direction = 1 if position > self.last_position else -1
                position = self.last_position + (direction * max_change)

        # Son pozisyonu güncelle
        self.last_position = position
        self.last_detection_time = time.time()

        return position

    def is_crosswalk(self, frame):
        """
        Zemin geçidi (yaya geçidi) algılar

        Args:
            frame: Kameradan alınan görüntü

        Returns:
            is_crosswalk: Zemin geçidi tespit edildi mi?
            confidence: Tespit güven değeri (0.0 - 1.0)
            processed_frame: İşlenmiş görüntü (debug için)
        """
        # Görüntüyü gri tonlamaya çevir
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # İlgi alanını (ROI) belirle - alt kısım, zemin geçidi için özel ROI yüksekliği
        height, width = gray.shape
        roi_height = config.CROSSWALK_ROI_HEIGHT
        roi = gray[height - roi_height:height, 0:width]

        # Görüntüyü bulanıklaştır
        blur = cv2.GaussianBlur(roi, (5, 5), 0)

        # İkili (binary) görüntüye çevir - beyaz şerit için normal threshold
        _, binary = cv2.threshold(blur, config.BINARY_THRESHOLD, 255, cv2.THRESH_BINARY)

        # Yatay çizgileri vurgula
        kernel_horizontal = np.ones((1, 20), np.uint8)
        dilated_horizontal = cv2.dilate(binary, kernel_horizontal, iterations=1)

        # Dikey çizgileri vurgula (yaya geçidi için)
        kernel_vertical = np.ones((10, 1), np.uint8)
        dilated_vertical = cv2.dilate(binary, kernel_vertical, iterations=1)

        # Yatay ve dikey çizgileri birleştir
        combined = cv2.bitwise_or(dilated_horizontal, dilated_vertical)

        # Gürültüyü azalt
        kernel = np.ones((3, 3), np.uint8)
        filtered = cv2.morphologyEx(combined, cv2.MORPH_OPEN, kernel)

        # Beyaz piksel oranını hesapla
        white_ratio = np.sum(filtered == 255) / (filtered.shape[0] * filtered.shape[1])

        # Zemin geçidi için eşik değeri kontrolü
        is_crosswalk = white_ratio > config.CROSSWALK_DETECTION_THRESHOLD

        # İşlenmiş görüntüyü hazırla (debug için)
        processed_frame = cv2.cvtColor(filtered, cv2.COLOR_GRAY2BGR)

        # Zemin geçidi tespiti bilgilerini görüntüye ekle
        if is_crosswalk:
            cv2.putText(processed_frame, f"Crosswalk: {white_ratio:.2f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        return is_crosswalk, white_ratio, processed_frame

    def detect_lane_type(self, binary_image):
        """
        Şerit tipini tespit eder (kesik veya düz)

        Args:
            binary_image: İkili görüntü

        Returns:
            lane_type: Şerit tipi ("dashed" veya "solid")
            confidence: Tespit güven değeri (0.0 - 1.0)
        """
        # Şerit genişliğini kullanarak kesik şerit tespiti yap
        _, width = binary_image.shape

        # Şerit pozisyonunu bul
        line_position = self._find_line_position(binary_image)

        if line_position is None:
            return "unknown", 0.0

        # Şerit pozisyonunu piksel koordinatına çevir
        line_x = self.frame_center + line_position

        # Şerit genişliğinin yarısı
        half_width = self.line_width_px // 2

        # Şerit bölgesini belirle
        left = max(0, line_x - half_width)
        right = min(width, line_x + half_width)

        # Şerit bölgesini al
        lane_region = binary_image[:, left:right]

        # Dikey yönde şerit bölgesini analiz et
        vertical_profile = np.sum(lane_region, axis=1)

        # Kesik şerit tespiti için dikey profili analiz et
        # Kesik şeritlerde dikey profilde boşluklar olacaktır
        normalized_profile = vertical_profile / np.max(vertical_profile) if np.max(vertical_profile) > 0 else vertical_profile

        # Profildeki değişimleri hesapla
        changes = np.diff(normalized_profile > 0.5)
        change_count = np.sum(np.abs(changes))

        # Değişim sayısı fazlaysa kesik şerit
        is_dashed = change_count >= 2
        confidence = min(1.0, change_count / 4)

        return "dashed" if is_dashed else "solid", confidence
