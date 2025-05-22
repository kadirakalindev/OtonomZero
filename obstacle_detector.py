"""
Engel algılama sınıfı - Renk tabanlı engel tespiti için optimize edilmiş
"""

import cv2
import numpy as np
import config
import time

class ObstacleDetector:
    def __init__(self):
        """
        Engel algılama sınıfı başlatıcı
        """
        self.frame_width = config.CAMERA_RESOLUTION[0]
        self.frame_height = config.CAMERA_RESOLUTION[1]

        # İlgi alanı (ROI) - görüntünün orta kısmı
        self.roi_top = config.ROI_TOP_OFFSET
        self.roi_bottom = self.frame_height // 2

        # Son tespit zamanı
        self.last_detection_time = time.time()
        self.last_obstacle_position = None

        # Engel renk aralıkları
        self.color_ranges = config.OBSTACLE_COLOR_RANGES

    def detect_obstacles(self, frame):
        """
        Görüntüden engelleri tespit eder - renk tabanlı tespit

        Args:
            frame: Kameradan alınan görüntü

        Returns:
            has_obstacle: Engel var mı?
            obstacle_position: Engelin pozisyonu (sol, orta, sağ)
            processed_frame: İşlenmiş görüntü (debug için)
        """
        # İlgi alanını (ROI) belirle - orta kısım
        roi = frame[self.roi_top:self.roi_bottom, 0:self.frame_width]

        # HSV renk uzayına dönüştür
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # Engel maskelerini oluştur
        masks = {}
        for color_name, (lower, upper) in self.color_ranges.items():
            lower = np.array(lower)
            upper = np.array(upper)
            masks[color_name] = cv2.inRange(hsv, lower, upper)

        # Tüm maskeleri birleştir
        combined_mask = np.zeros_like(masks['orange'])
        for mask in masks.values():
            combined_mask = cv2.bitwise_or(combined_mask, mask)

        # Gürültüyü azalt
        kernel = np.ones((5, 5), np.uint8)
        filtered_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
        filtered_mask = cv2.morphologyEx(filtered_mask, cv2.MORPH_CLOSE, kernel)

        # Konturları bul
        contours, _ = cv2.findContours(filtered_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # İşlenmiş görüntüyü hazırla (debug için)
        processed_frame = roi.copy()

        # Bölgeleri çiz
        cv2.line(processed_frame, (self.frame_width//3, 0), (self.frame_width//3, self.roi_bottom - self.roi_top), (0, 0, 255), 2)
        cv2.line(processed_frame, (2*self.frame_width//3, 0), (2*self.frame_width//3, self.roi_bottom - self.roi_top), (0, 0, 255), 2)

        # Engel tespiti değişkenleri
        has_obstacle = False
        obstacle_position = None
        obstacle_area = 0
        obstacle_x = 0

        # Konturları değerlendir
        for contour in contours:
            area = cv2.contourArea(contour)

            # Minimum alan kontrolü
            if area < config.OBSTACLE_MIN_AREA:
                continue

            # Engel tespit edildi
            has_obstacle = True

            # Kontur etrafına dikdörtgen çiz
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(processed_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # En büyük engeli takip et
            if area > obstacle_area:
                obstacle_area = area
                obstacle_x = x + w // 2  # Engelin merkezi

        # Engel pozisyonunu belirle
        if has_obstacle:
            # Engelin hangi bölgede olduğunu belirle
            if obstacle_x < self.frame_width // 3:
                obstacle_position = "left"
            elif obstacle_x < 2 * self.frame_width // 3:
                obstacle_position = "center"
            else:
                obstacle_position = "right"

            # Engel bilgilerini görüntüye ekle
            cv2.putText(processed_frame, f"Obstacle: {obstacle_position}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # Son tespit bilgilerini güncelle
            self.last_detection_time = time.time()
            self.last_obstacle_position = obstacle_position

        return has_obstacle, obstacle_position, processed_frame

    def get_avoidance_direction(self, obstacle_position):
        """
        Engelden kaçınma yönünü belirler

        Args:
            obstacle_position: Engelin pozisyonu

        Returns:
            direction: Kaçınma yönü ("left", "right", "backward_right", "backward_left")
        """
        if obstacle_position == "left":
            # Sol taraftaki engel için sağa dön
            return "right"
        elif obstacle_position == "right":
            # Sağ taraftaki engel için sola dön
            return "left"
        elif obstacle_position == "center":
            # Merkezdeki engel için geri git ve sağa dön (varsayılan)
            return "backward_right"
        else:
            # Pozisyon bilinmiyorsa veya geçersizse, varsayılan olarak sağa dön
            return "right"

    def detect_obstacle_color(self, frame):
        """
        Engelin rengini tespit eder

        Args:
            frame: Kameradan alınan görüntü

        Returns:
            color: Engelin rengi ("orange", "yellow", None)
            confidence: Tespit güven değeri (0.0 - 1.0)
        """
        # İlgi alanını (ROI) belirle
        roi = frame[self.roi_top:self.roi_bottom, 0:self.frame_width]

        # HSV renk uzayına dönüştür
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # Her renk için maske oluştur ve piksel sayısını hesapla
        color_pixels = {}
        for color_name, (lower, upper) in self.color_ranges.items():
            lower = np.array(lower)
            upper = np.array(upper)
            mask = cv2.inRange(hsv, lower, upper)

            # Gürültüyü azalt
            kernel = np.ones((5, 5), np.uint8)
            filtered_mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

            # Renk piksel sayısı
            color_pixels[color_name] = np.sum(filtered_mask == 255)

        # En çok piksele sahip rengi bul
        max_color = None
        max_pixels = config.OBSTACLE_MIN_AREA  # Minimum piksel eşiği

        for color, pixels in color_pixels.items():
            if pixels > max_pixels:
                max_pixels = pixels
                max_color = color

        # Güven değeri hesapla
        total_pixels = roi.shape[0] * roi.shape[1]
        confidence = max_pixels / total_pixels if max_color else 0.0

        return max_color, confidence
