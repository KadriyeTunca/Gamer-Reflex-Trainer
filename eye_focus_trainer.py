"""
Göz Odak Takip Oyunu (MediaPipe ile Gerçek Göz Takibi)
- MediaPipe Face Mesh kullanarak göz bebeklerini takip eder
- Kalibrasyon ile ekran koordinatlarına eşler
- Hareket eden topu gözlerinizle takip edin
- 1 saniye odaklanma = +5 puan
"""

import cv2
import numpy as np
import mediapipe as mp
import random
import time
from collections import deque


# ============================================
# SABİTLER VE KONFİGÜRASYON
# ============================================

# Ekran boyutları
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# Top özellikleri
BALL_RADIUS = 45
BALL_SPEED_OPTIONS = [-5, -4, -3, 3, 4, 5]

# Odak kontrolü
FOCUS_THRESHOLD = 100  # Piksel cinsinden odak mesafesi
FOCUS_REQUIRED_TIME = 1.0  # Saniye
POINT_REWARD = 5

# Smoothing ve stabilizasyon
SMOOTHING_FACTOR = 0.22  # Daha hızlı tepki - rahat takip için
GAZE_HISTORY_SIZE = 6  # Daha az gecikme

# Odak kaybı toleransı (stabilizasyon için)
FOCUS_LOSS_TOLERANCE = 0.5  # Saniye - küçük refleksleri tolere et
FOCUS_DECAY_RATE = 0.3  # Odak kaybında ne kadar hızlı düşsün

# MediaPipe güven eşikleri
DETECTION_CONFIDENCE = 0.7
TRACKING_CONFIDENCE = 0.7

# Kalibrasyon
CALIBRATION_HOLD_TIME = 2.0  # Saniye
CALIBRATION_STABILITY_THRESHOLD = 0.04  # İris hareketi toleransı (gevşetildi)

# Renkler (BGR formatında)
COLORS = {
    'yellow': (0, 255, 255),
    'magenta': (255, 0, 255),
    'green': (0, 255, 0),
    'orange': (0, 165, 255),
    'blue': (255, 0, 0),
    'red': (0, 0, 255),
    'cyan': (255, 255, 0),
    'purple': (128, 0, 255),
    'white': (255, 255, 255),
    'gray': (150, 150, 150),
    'dark_gray': (50, 50, 50),
}

# MediaPipe Landmark indeksleri
LANDMARK_INDICES = {
    'left_iris_center': 468,
    'right_iris_center': 473,
    'left_eye_left': 33,
    'left_eye_right': 133,
    'right_eye_left': 362,
    'right_eye_right': 263,
    'left_eye_top': 159,
    'left_eye_bottom': 145,
    'right_eye_top': 386,
    'right_eye_bottom': 374,
}


# ============================================
# YARDIMCI FONKSİYONLAR
# ============================================

def get_random_bright_color():
    """Rastgele parlak renk seç"""
    color_list = ['yellow', 'magenta', 'green', 'orange', 'blue', 'red', 'cyan', 'purple']
    return COLORS[random.choice(color_list)]


def calculate_distance(x1, y1, x2, y2):
    """İki nokta arasındaki mesafeyi hesapla"""
    return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def clamp(value, min_val, max_val):
    """Değeri min-max arasında sınırla"""
    return max(min_val, min(max_val, value))


# ============================================
# ANA SINIF
# ============================================

class EyeFocusTrainer:
    def __init__(self):
        self._init_camera()
        self._init_mediapipe()
        self._init_ball()
        self._init_game_state()
        self._init_eye_tracking()
        self._init_calibration()
    
    def _init_camera(self):
        """Kamera başlatma"""
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, SCREEN_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, SCREEN_HEIGHT)
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
    
    def _init_mediapipe(self):
        """MediaPipe Face Mesh başlatma"""
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=DETECTION_CONFIDENCE,
            min_tracking_confidence=TRACKING_CONFIDENCE
        )
    
    def _init_ball(self):
        """Top özelliklerini başlat"""
        self.ball_radius = BALL_RADIUS
        self.ball_x = self.screen_width // 2
        self.ball_y = self.screen_height // 2
        self.ball_speed_x = random.choice(BALL_SPEED_OPTIONS)
        self.ball_speed_y = random.choice(BALL_SPEED_OPTIONS)
        self.ball_color = get_random_bright_color()
    
    def _init_game_state(self):
        """Oyun durumunu başlat"""
        self.score = 0
        self.focus_start_time = None
        self.focus_duration = 0.0
        self.is_focused = False
        self.warning_message = ""
        self.warning_time = 0
        self.success_message = ""
        self.success_time = 0
        
        # Stabilizasyon için ek değişkenler
        self.focus_loss_start = None  # Odak kaybının başladığı zaman
        self.accumulated_focus = 0.0  # Biriken odak süresi (toleranslı)
    
    def _init_eye_tracking(self):
        """Göz takip verilerini başlat"""
        self.iris_x = 0.5
        self.iris_y = 0.5
        self.face_detected = False
        self.eyes_valid = False
        
        # Bakış noktası
        self.gaze_x = self.screen_width // 2
        self.gaze_y = self.screen_height // 2
        
        # Smoothing için geçmiş değerler
        self.gaze_history_x = deque(maxlen=GAZE_HISTORY_SIZE)
        self.gaze_history_y = deque(maxlen=GAZE_HISTORY_SIZE)
        self.prev_gaze_x = self.screen_width // 2
        self.prev_gaze_y = self.screen_height // 2
    
    def _init_calibration(self):
        """Kalibrasyon verilerini başlat"""
        self.calibration_points = {
            'center': {'screen': (self.screen_width // 2, self.screen_height // 2), 'iris': None},
            'left': {'screen': (200, self.screen_height // 2), 'iris': None},
            'right': {'screen': (self.screen_width - 200, self.screen_height // 2), 'iris': None},
            'top': {'screen': (self.screen_width // 2, 150), 'iris': None},
            'bottom': {'screen': (self.screen_width // 2, self.screen_height - 150), 'iris': None},
        }
        self.calibration_order = ['center', 'left', 'right', 'top', 'bottom']
        self.current_calibration_index = 0
        self.is_calibrated = False
        self.calibration_hold_time = 0
        
        # Kalibrasyon sonuçları
        self.iris_center = (0.5, 0.5)
        self.iris_left = None
        self.iris_right = None
        self.iris_top = None
        self.iris_bottom = None
        
        # Kalibrasyon stabilitesi için
        self.calibration_iris_history = []

    # ============================================
    # TOP KONTROLÜ
    # ============================================

    def update_ball(self):
        """Topu hareket ettir"""
        self.ball_x += self.ball_speed_x
        self.ball_y += self.ball_speed_y
        
        # Duvar çarpışmaları
        if self.ball_x <= self.ball_radius or self.ball_x >= self.screen_width - self.ball_radius:
            self.ball_speed_x = -self.ball_speed_x
            self.ball_color = get_random_bright_color()
            
        if self.ball_y <= self.ball_radius or self.ball_y >= self.screen_height - self.ball_radius:
            self.ball_speed_y = -self.ball_speed_y
            self.ball_color = get_random_bright_color()
        
        # Sınırları zorla
        self.ball_x = clamp(self.ball_x, self.ball_radius, self.screen_width - self.ball_radius)
        self.ball_y = clamp(self.ball_y, self.ball_radius, self.screen_height - self.ball_radius)

    def reset_ball(self):
        """Topu yeni pozisyona taşı"""
        margin = 150
        self.ball_x = random.randint(self.ball_radius + margin, self.screen_width - self.ball_radius - margin)
        self.ball_y = random.randint(self.ball_radius + margin, self.screen_height - self.ball_radius - margin)
        self.ball_speed_x = random.choice(BALL_SPEED_OPTIONS)
        self.ball_speed_y = random.choice(BALL_SPEED_OPTIONS)
        self.ball_color = get_random_bright_color()

    # ============================================
    # GÖZ TAKİBİ
    # ============================================

    def get_iris_position(self, landmarks):
        """İris pozisyonunu hesapla (göz içindeki pozisyon, 0-1 arası)"""
        idx = LANDMARK_INDICES
        
        # Sol göz
        left_iris = landmarks[idx['left_iris_center']]
        left_eye_left = landmarks[idx['left_eye_left']]
        left_eye_right = landmarks[idx['left_eye_right']]
        left_eye_top = landmarks[idx['left_eye_top']]
        left_eye_bottom = landmarks[idx['left_eye_bottom']]
        
        # Sağ göz
        right_iris = landmarks[idx['right_iris_center']]
        right_eye_left = landmarks[idx['right_eye_left']]
        right_eye_right = landmarks[idx['right_eye_right']]
        right_eye_top = landmarks[idx['right_eye_top']]
        right_eye_bottom = landmarks[idx['right_eye_bottom']]
        
        # Sol göz X normalize
        left_eye_width = left_eye_right.x - left_eye_left.x
        if left_eye_width > 0.005:
            left_iris_x = (left_iris.x - left_eye_left.x) / left_eye_width
        else:
            return None, None  # Geçersiz göz tespiti
        
        # Sol göz Y normalize (göz kapakları arası)
        left_eye_height = left_eye_bottom.y - left_eye_top.y
        if left_eye_height > 0.002:
            left_iris_y = (left_iris.y - left_eye_top.y) / left_eye_height
        else:
            return None, None
        
        # Sağ göz X normalize
        right_eye_width = right_eye_right.x - right_eye_left.x
        if right_eye_width > 0.005:
            right_iris_x = (right_iris.x - right_eye_left.x) / right_eye_width
        else:
            return None, None
        
        # Sağ göz Y normalize
        right_eye_height = right_eye_bottom.y - right_eye_top.y
        if right_eye_height > 0.002:
            right_iris_y = (right_iris.y - right_eye_top.y) / right_eye_height
        else:
            return None, None
        
        # İki gözün ortalaması
        avg_iris_x = (left_iris_x + right_iris_x) / 2
        avg_iris_y = (left_iris_y + right_iris_y) / 2
        
        # Değerlerin mantıklı aralıkta olup olmadığını kontrol et
        if not (0.1 < avg_iris_x < 0.9 and 0.1 < avg_iris_y < 0.9):
            # Aşırı değerler = muhtemelen hatalı tespit
            return None, None
        
        return avg_iris_x, avg_iris_y

    def detect_face(self, frame):
        """MediaPipe ile yüz ve göz iris tespiti"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        self.face_detected = False
        self.eyes_valid = False
        
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            self.face_detected = True
            
            h, w, _ = frame.shape
            landmarks = face_landmarks.landmark
            
            # İris pozisyonunu hesapla
            iris_x, iris_y = self.get_iris_position(landmarks)
            
            if iris_x is not None and iris_y is not None:
                self.iris_x = iris_x
                self.iris_y = iris_y
                self.eyes_valid = True
                
                # Görselleştirme: İris noktalarını çiz
                self._draw_eye_landmarks(frame, landmarks, w, h)
        
        return frame

    def _draw_eye_landmarks(self, frame, landmarks, w, h):
        """Göz landmark'larını çiz"""
        idx = LANDMARK_INDICES
        
        # İris merkezleri (yeşil)
        for key in ['left_iris_center', 'right_iris_center']:
            point = landmarks[idx[key]]
            px = (int(point.x * w), int(point.y * h))
            cv2.circle(frame, px, 5, COLORS['green'], -1)
        
        # Göz köşeleri (mavi)
        corner_keys = ['left_eye_left', 'left_eye_right', 'right_eye_left', 'right_eye_right']
        for key in corner_keys:
            point = landmarks[idx[key]]
            px = (int(point.x * w), int(point.y * h))
            cv2.circle(frame, px, 3, COLORS['blue'], -1)
        
        # Göz kapakları (turuncu)
        eyelid_keys = ['left_eye_top', 'left_eye_bottom', 'right_eye_top', 'right_eye_bottom']
        for key in eyelid_keys:
            point = landmarks[idx[key]]
            px = (int(point.x * w), int(point.y * h))
            cv2.circle(frame, px, 2, COLORS['orange'], -1)

    # ============================================
    # KALİBRASYON
    # ============================================

    def run_calibration(self, frame):
        """Kalibrasyon modunu çalıştır"""
        if self.current_calibration_index >= len(self.calibration_order):
            self._finish_calibration()
            return frame
        
        current_point_name = self.calibration_order[self.current_calibration_index]
        current_point = self.calibration_points[current_point_name]
        screen_x, screen_y = current_point['screen']
        
        # Arka plan karart
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (self.screen_width, self.screen_height), (20, 20, 20), -1)
        frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)
        
        # Hedef noktayı çiz
        self._draw_calibration_target(frame, screen_x, screen_y)
        
        # Talimatları çiz
        self._draw_calibration_instructions(frame, current_point_name)
        
        # İlerlemeyi işle
        if self.face_detected and self.eyes_valid:
            # İris stabilitesini kontrol et
            self.calibration_iris_history.append((self.iris_x, self.iris_y))
            
            # Son 15 frame'i tut
            if len(self.calibration_iris_history) > 15:
                self.calibration_iris_history.pop(0)
            
            # Stabilite kontrolü - son 8 frame'de iris ne kadar hareket etti?
            is_stable = True
            if len(self.calibration_iris_history) >= 8:
                recent = self.calibration_iris_history[-8:]
                x_values = [p[0] for p in recent]
                y_values = [p[1] for p in recent]
                x_range = max(x_values) - min(x_values)
                y_range = max(y_values) - min(y_values)
                
                if x_range > CALIBRATION_STABILITY_THRESHOLD or y_range > CALIBRATION_STABILITY_THRESHOLD:
                    is_stable = False
            else:
                is_stable = True  # Yeterli veri yoksa kabul et
            
            if is_stable:
                self.calibration_hold_time += 1 / 30.0
                self._draw_calibration_progress(frame)
                
                if self.calibration_hold_time >= CALIBRATION_HOLD_TIME:
                    # Stabil pozisyonun ortalamasını al
                    recent = self.calibration_iris_history[-8:] if len(self.calibration_iris_history) >= 8 else self.calibration_iris_history
                    avg_x = sum(p[0] for p in recent) / len(recent)
                    avg_y = sum(p[1] for p in recent) / len(recent)
                    self.calibration_points[current_point_name]['iris'] = (avg_x, avg_y)
                    self.current_calibration_index += 1
                    self.calibration_hold_time = 0
                    self.calibration_iris_history.clear()
            else:
                # Stabil değil - ilerlemeyi yavaşça azalt
                self.calibration_hold_time = max(0, self.calibration_hold_time - 0.05)
                cv2.putText(frame, "SABIT BAKIN!", (self.screen_width // 2 - 100, self.screen_height // 2 + 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS['orange'], 2)
        else:
            self.calibration_hold_time = max(0, self.calibration_hold_time - 0.1)
            status = "YUZ TESPIT EDILEMIYOR!" if not self.face_detected else "GOZ TESPIT EDILEMIYOR!"
            cv2.putText(frame, status, (self.screen_width // 2 - 200, self.screen_height // 2 + 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS['red'], 3)
        
        return frame

    def _draw_calibration_target(self, frame, x, y):
        """Kalibrasyon hedef noktasını çiz"""
        pulse = int(20 * np.sin(time.time() * 4) + 60)
        cv2.circle(frame, (x, y), pulse, (0, 80, 200), -1)
        cv2.circle(frame, (x, y), 45, COLORS['red'], -1)
        cv2.circle(frame, (x, y), 45, COLORS['white'], 4)
        cv2.circle(frame, (x, y), 15, COLORS['white'], -1)

    def _draw_calibration_instructions(self, frame, current_point_name):
        """Kalibrasyon talimatlarını çiz"""
        cv2.putText(frame, "KALIBRASYON", (self.screen_width // 2 - 150, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, COLORS['cyan'], 3)
        
        cv2.putText(frame, "Sadece GOZLERINIZLE kirmizi noktaya bakin!",
                    (self.screen_width // 2 - 300, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, COLORS['white'], 2)
        
        cv2.putText(frame, "(Basinizi hareket ettirmeyin, sadece gozlerinizi kullanin)",
                    (self.screen_width // 2 - 350, 140),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLORS['gray'], 2)
        
        point_names = {
            'center': 'MERKEZ', 'left': 'SOL', 'right': 'SAG',
            'top': 'YUKARI', 'bottom': 'ASAGI'
        }
        progress_text = f"Nokta: {point_names[current_point_name]} ({self.current_calibration_index + 1}/5)"
        cv2.putText(frame, progress_text, (20, self.screen_height - 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, COLORS['cyan'], 2)
        
        # Debug bilgisi
        if self.eyes_valid:
            iris_text = f"Iris: X={self.iris_x:.3f} Y={self.iris_y:.3f}"
            cv2.putText(frame, iris_text, (20, self.screen_height - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLORS['gray'], 1)

    def _draw_calibration_progress(self, frame):
        """Kalibrasyon ilerleme çubuğunu çiz"""
        progress = min(self.calibration_hold_time / CALIBRATION_HOLD_TIME, 1.0)
        bar_width = 400
        bar_height = 35
        bar_x = self.screen_width // 2 - bar_width // 2
        bar_y = self.screen_height // 2 + 100
        
        # Arka plan
        cv2.rectangle(frame, (bar_x - 2, bar_y - 2), 
                      (bar_x + bar_width + 2, bar_y + bar_height + 2), COLORS['white'], 2)
        cv2.rectangle(frame, (bar_x, bar_y), 
                      (bar_x + bar_width, bar_y + bar_height), COLORS['dark_gray'], -1)
        
        # İlerleme
        fill_width = int(bar_width * progress)
        if fill_width > 0:
            cv2.rectangle(frame, (bar_x, bar_y), 
                          (bar_x + fill_width, bar_y + bar_height), COLORS['green'], -1)
        
        # Yüzde
        percent_text = f"{int(progress * 100)}%"
        cv2.putText(frame, percent_text, (bar_x + bar_width // 2 - 25, bar_y + 27),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS['white'], 2)

    def _finish_calibration(self):
        """Kalibrasyon tamamlandı"""
        self.iris_center = self.calibration_points['center']['iris']
        self.iris_left = self.calibration_points['left']['iris']
        self.iris_right = self.calibration_points['right']['iris']
        self.iris_top = self.calibration_points['top']['iris']
        self.iris_bottom = self.calibration_points['bottom']['iris']
        self.is_calibrated = True
        print("Kalibrasyon tamamlandi!")

    # ============================================
    # BAKIŞ NOKTASI HESAPLAMA
    # ============================================

    def calculate_gaze(self):
        """Kalibrasyon verilerine göre bakış noktasını hesapla"""
        if not self.is_calibrated or not self.eyes_valid:
            return
        
        # Kalibrasyon verilerinin geçerliliğini kontrol et
        if not all([self.iris_center, self.iris_left, self.iris_right, self.iris_top, self.iris_bottom]):
            return
        
        # X ekseni normalize
        center_x = self.iris_center[0]
        left_x = self.iris_left[0]
        right_x = self.iris_right[0]
        
        if self.iris_x < center_x:
            # Sola bakıyor
            range_x = center_x - left_x
            norm_x = -(center_x - self.iris_x) / range_x if range_x > 0.001 else 0
        else:
            # Sağa bakıyor
            range_x = right_x - center_x
            norm_x = (self.iris_x - center_x) / range_x if range_x > 0.001 else 0
        
        # Y ekseni normalize
        center_y = self.iris_center[1]
        top_y = self.iris_top[1]
        bottom_y = self.iris_bottom[1]
        
        if self.iris_y < center_y:
            # Yukarı bakıyor
            range_y = center_y - top_y
            norm_y = -(center_y - self.iris_y) / range_y if range_y > 0.001 else 0
        else:
            # Aşağı bakıyor
            range_y = bottom_y - center_y
            norm_y = (self.iris_y - center_y) / range_y if range_y > 0.001 else 0
        
        # Sınırla
        norm_x = clamp(norm_x, -1.5, 1.5)
        norm_y = clamp(norm_y, -1.5, 1.5)
        
        # Ekran koordinatlarına çevir
        target_x = int(self.screen_width / 2 + norm_x * (self.screen_width / 2 - 100))
        target_y = int(self.screen_height / 2 + norm_y * (self.screen_height / 2 - 50))  # Y için daha geniş alan
        
        # Geçmiş değerlere ekle
        self.gaze_history_x.append(target_x)
        self.gaze_history_y.append(target_y)
        
        # Ağırlıklı ortalama (son değerler daha önemli)
        if len(self.gaze_history_x) >= 3:
            weights = np.linspace(0.5, 1.0, len(self.gaze_history_x))
            weights = weights / weights.sum()
            
            avg_x = np.average(list(self.gaze_history_x), weights=weights)
            avg_y = np.average(list(self.gaze_history_y), weights=weights)
        else:
            avg_x = target_x
            avg_y = target_y
        
        # Ani büyük sıçramaları sınırla (ama çok kısıtlayıcı olmasın)
        max_jump = 150  # piksel - makul bir limit
        delta_x = avg_x - self.prev_gaze_x
        delta_y = avg_y - self.prev_gaze_y
        
        if abs(delta_x) > max_jump:
            avg_x = self.prev_gaze_x + (max_jump if delta_x > 0 else -max_jump)
        if abs(delta_y) > max_jump:
            avg_y = self.prev_gaze_y + (max_jump if delta_y > 0 else -max_jump)
        
        # Smoothing uygula
        self.gaze_x = int(self.prev_gaze_x + (avg_x - self.prev_gaze_x) * SMOOTHING_FACTOR)
        self.gaze_y = int(self.prev_gaze_y + (avg_y - self.prev_gaze_y) * SMOOTHING_FACTOR)
        
        # Sınırla
        self.gaze_x = clamp(self.gaze_x, 50, self.screen_width - 50)
        self.gaze_y = clamp(self.gaze_y, 50, self.screen_height - 50)
        
        self.prev_gaze_x = self.gaze_x
        self.prev_gaze_y = self.gaze_y

    # ============================================
    # ODAK KONTROLÜ
    # ============================================

    def check_focus(self):
        """Odaklanma durumunu kontrol et - Stabilize edilmiş versiyon"""
        if not self.eyes_valid or not self.is_calibrated:
            # Göz tespit edilemezse tolerans süresi kadar bekle
            if self.is_focused and self.focus_loss_start is None:
                self.focus_loss_start = time.time()
            
            if self.focus_loss_start:
                loss_duration = time.time() - self.focus_loss_start
                if loss_duration > FOCUS_LOSS_TOLERANCE:
                    self._reset_focus()
            return
        
        self.calculate_gaze()
        
        distance = calculate_distance(self.gaze_x, self.gaze_y, self.ball_x, self.ball_y)
        
        if distance < FOCUS_THRESHOLD:
            # Odak içinde - kayıp zamanlayıcısını sıfırla
            self.focus_loss_start = None
            
            if not self.is_focused:
                self.is_focused = True
                self.focus_start_time = time.time()
                self.accumulated_focus = 0.0
            else:
                self.focus_duration = time.time() - self.focus_start_time
                self.accumulated_focus = self.focus_duration
                
                if self.accumulated_focus >= FOCUS_REQUIRED_TIME:
                    self.score += POINT_REWARD
                    self.success_message = f"+{POINT_REWARD} PUAN!"
                    self.success_time = time.time()
                    self._reset_focus()
                    self.reset_ball()
        else:
            # Odak dışında - tolerans kontrolü
            if self.is_focused:
                if self.focus_loss_start is None:
                    # İlk kayıp anı
                    self.focus_loss_start = time.time()
                else:
                    loss_duration = time.time() - self.focus_loss_start
                    
                    if loss_duration > FOCUS_LOSS_TOLERANCE:
                        # Tolerans aşıldı - odağı kaybet
                        if self.accumulated_focus > 0.3:
                            self.warning_message = "Odak kaybedildi!"
                            self.warning_time = time.time()
                        self._reset_focus()
                    # else: Tolerans içinde - odağı koru, biriken süreyi düşür
                    elif self.accumulated_focus > 0:
                        self.accumulated_focus -= FOCUS_DECAY_RATE * (1/30)  # Frame başına azalt

    def _reset_focus(self):
        """Odak durumunu sıfırla"""
        self.is_focused = False
        self.focus_start_time = None
        self.focus_duration = 0.0
        self.focus_loss_start = None
        self.accumulated_focus = 0.0

    # ============================================
    # ARAYÜZ ÇİZİMİ
    # ============================================

    def draw_ui(self, frame):
        """Arayüzü çiz"""
        self._draw_gaze_crosshair(frame)
        self._draw_ball(frame)
        self._draw_top_bar(frame)
        self._draw_messages(frame)
        self._draw_footer(frame)
        return frame

    def _draw_gaze_crosshair(self, frame):
        """Bakış noktası hedefini çiz"""
        if self.eyes_valid and self.is_calibrated:
            x, y = int(self.gaze_x), int(self.gaze_y)
            color = COLORS['magenta']
            
            cv2.circle(frame, (x, y), 35, color, 3)
            cv2.circle(frame, (x, y), 15, color, -1)
            cv2.line(frame, (x - 50, y), (x + 50, y), color, 2)
            cv2.line(frame, (x, y - 50), (x, y + 50), color, 2)

    def _draw_ball(self, frame):
        """Topu çiz"""
        x, y = int(self.ball_x), int(self.ball_y)
        
        cv2.circle(frame, (x, y), self.ball_radius, self.ball_color, -1)
        cv2.circle(frame, (x, y), self.ball_radius, COLORS['white'], 3)
        
        # Odaklanma halesi
        if self.is_focused:
            cv2.circle(frame, (x, y), self.ball_radius + 20, COLORS['green'], 4)

    def _draw_top_bar(self, frame):
        """Üst bilgi çubuğunu çiz"""
        cv2.rectangle(frame, (0, 0), (self.screen_width, 80), (30, 30, 30), -1)
        
        # Skor
        cv2.putText(frame, f"SKOR: {self.score}", (20, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, COLORS['green'], 3)
        
        # Odaklanma ilerleme çubuğu
        if self.is_focused:
            progress = min(self.focus_duration / FOCUS_REQUIRED_TIME, 1.0)
            bar_width = 300
            bar_height = 25
            bar_x = self.screen_width // 2 - bar_width // 2
            bar_y = 28
            
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (60, 60, 60), -1)
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + int(bar_width * progress), bar_y + bar_height), COLORS['green'], -1)
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), COLORS['white'], 2)
            
            time_text = f"{self.focus_duration:.1f}s"
            cv2.putText(frame, time_text, (bar_x + bar_width + 15, bar_y + 22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLORS['white'], 2)
        
        # Durum
        if self.eyes_valid:
            status_text = "GOZ OK"
            status_color = COLORS['green']
        elif self.face_detected:
            status_text = "GOZ YOK"
            status_color = COLORS['orange']
        else:
            status_text = "YUZ YOK"
            status_color = COLORS['red']
        
        cv2.putText(frame, status_text, (self.screen_width - 150, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, status_color, 2)

    def _draw_messages(self, frame):
        """Uyarı ve başarı mesajlarını çiz"""
        if self.warning_message and time.time() - self.warning_time < 1.5:
            cv2.putText(frame, self.warning_message, (self.screen_width // 2 - 150, self.screen_height // 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, COLORS['red'], 3)
        
        if self.success_message and time.time() - self.success_time < 1.5:
            cv2.putText(frame, self.success_message, (self.screen_width // 2 - 100, self.screen_height // 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, COLORS['green'], 4)

    def _draw_footer(self, frame):
        """Alt bilgi çubuğunu çiz"""
        text = "Mor hedefi topa getirin ve 1sn tutun | R = Yeniden Kalibrasyon | Q = Cikis"
        cv2.putText(frame, text, (self.screen_width // 2 - 400, self.screen_height - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLORS['gray'], 2)

    # ============================================
    # ANA DÖNGÜ
    # ============================================

    def reset_calibration(self):
        """Kalibrasyonu sıfırla"""
        self.is_calibrated = False
        self.current_calibration_index = 0
        self.calibration_hold_time = 0
        self.gaze_history_x.clear()
        self.gaze_history_y.clear()
        for point in self.calibration_points.values():
            point['iris'] = None
        print("Yeniden kalibrasyon baslatiliyor...")

    def run(self):
        """Ana döngü"""
        print("\n" + "=" * 60)
        print("GOZ ODAK TAKIP OYUNU - MediaPipe Edition")
        print("=" * 60)
        print("\nKontroller:")
        print("- Q = Cikis")
        print("- R = Yeniden kalibrasyon")
        print("=" * 60 + "\n")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Kamera okunamadi!")
                break
            
            frame = cv2.flip(frame, 1)
            frame = self.detect_face(frame)
            
            if not self.is_calibrated:
                frame = self.run_calibration(frame)
            else:
                self.update_ball()
                self.check_focus()
                frame = self.draw_ui(frame)
            
            cv2.imshow('Goz Odak Takip Oyunu', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                self.reset_calibration()
        
        self._cleanup()

    def _cleanup(self):
        """Kaynakları temizle"""
        self.cap.release()
        cv2.destroyAllWindows()
        self.face_mesh.close()
        print(f"\n{'=' * 60}")
        print(f"OYUN BITTI! Toplam skor: {self.score}")
        print(f"{'=' * 60}")


if __name__ == "__main__":
    trainer = EyeFocusTrainer()
    trainer.run()
