"""
Göz Odak Takip Oyunu
- Kamera ile göz takibi yapar
- Ekranda hareket eden renkli bir top gösterir
- Kullanıcının gözleriyle topu takip etmesini bekler
- Odak süresi 1 saniyeyi geçerse +5 puan verir
- Odak kaybolursa uyarı gösterir
"""

import cv2
import numpy as np
import random
import time

class EyeFocusTrainer:
    def __init__(self):
        # Kamera başlat
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        # Haarcascade sınıflandırıcıları yükle
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        # Ekran boyutları
        self.screen_width = 1280
        self.screen_height = 720
        
        # Top özellikleri
        self.ball_radius = 30
        self.ball_x = random.randint(self.ball_radius, self.screen_width - self.ball_radius)
        self.ball_y = random.randint(self.ball_radius, self.screen_height - self.ball_radius)
        self.ball_speed_x = random.choice([-5, -4, -3, 3, 4, 5])
        self.ball_speed_y = random.choice([-5, -4, -3, 3, 4, 5])
        self.ball_color = self.random_color()
        
        # Oyun durumu
        self.score = 0
        self.focus_start_time = None
        self.focus_duration = 0.0
        self.is_focused = False
        self.warning_message = ""
        self.warning_time = 0
        self.success_message = ""
        self.success_time = 0
        
        # Göz pozisyonu
        self.eye_center_x = 0
        self.eye_center_y = 0
        self.eyes_detected = False
        
        # Odak eşik değeri (piksel cinsinden)
        self.focus_threshold = 200
        
    def random_color(self):
        """Rastgele parlak renk üret"""
        colors = [
            (0, 255, 255),    # Sarı
            (255, 0, 255),    # Magenta
            (0, 255, 0),      # Yeşil
            (255, 165, 0),    # Turuncu
            (255, 0, 0),      # Mavi
            (0, 0, 255),      # Kırmızı
            (255, 255, 0),    # Cyan
            (128, 0, 255),    # Mor
        ]
        return random.choice(colors)
    
    def update_ball(self):
        """Topu hareket ettir"""
        self.ball_x += self.ball_speed_x
        self.ball_y += self.ball_speed_y
        
        # Duvarlardan sekme
        if self.ball_x <= self.ball_radius or self.ball_x >= self.screen_width - self.ball_radius:
            self.ball_speed_x = -self.ball_speed_x
            self.ball_color = self.random_color()  # Her sekmede renk değiştir
            
        if self.ball_y <= self.ball_radius or self.ball_y >= self.screen_height - self.ball_radius:
            self.ball_speed_y = -self.ball_speed_y
            self.ball_color = self.random_color()
            
        # Sınırları kontrol et
        self.ball_x = max(self.ball_radius, min(self.screen_width - self.ball_radius, self.ball_x))
        self.ball_y = max(self.ball_radius, min(self.screen_height - self.ball_radius, self.ball_y))
    
    def detect_eyes(self, frame):
        """Gözleri tespit et"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        self.eyes_detected = False
        
        for (x, y, w, h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = frame[y:y+h, x:x+w]
            
            eyes = self.eye_cascade.detectMultiScale(roi_gray)
            
            if len(eyes) >= 2:
                self.eyes_detected = True
                
                # İlk iki göz için ortalama merkez hesapla
                eye1 = eyes[0]
                eye2 = eyes[1]
                
                # Göz merkezlerini hesapla
                eye1_center_x = x + eye1[0] + eye1[2] // 2
                eye1_center_y = y + eye1[1] + eye1[3] // 2
                eye2_center_x = x + eye2[0] + eye2[2] // 2
                eye2_center_y = y + eye2[1] + eye2[3] // 2
                
                # Ortalama göz merkezi
                self.eye_center_x = (eye1_center_x + eye2_center_x) // 2
                self.eye_center_y = (eye1_center_y + eye2_center_y) // 2
                
                # Gözleri çiz
                for (ex, ey, ew, eh) in eyes[:2]:
                    cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
                
                # Yüz çerçevesi
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                
                # Göz merkezi noktası
                cv2.circle(frame, (self.eye_center_x, self.eye_center_y), 5, (0, 0, 255), -1)
                
        return frame
    
    def check_focus(self):
        """Odaklanma durumunu kontrol et"""
        if not self.eyes_detected:
            self.reset_focus()
            return
        
        # Göz merkezi ile top arasındaki mesafe
        # Göz bakış yönünü tahmin etmek için basit bir yaklaşım
        # Gerçek göz takibi için daha gelişmiş yöntemler gerekir
        
        # Yüz pozisyonuna göre bakış yönü tahmini
        # Burada basitleştirilmiş bir yaklaşım kullanıyoruz
        frame_center_x = self.screen_width // 2
        
        # Göz pozisyonuna göre tahmini bakış noktası
        # Göz sola bakarsa, bakış noktası sağa olur (ayna etkisi)
        gaze_offset_x = (frame_center_x - self.eye_center_x) * 2
        estimated_gaze_x = frame_center_x + gaze_offset_x
        estimated_gaze_y = self.eye_center_y
        
        # Top ile bakış noktası arasındaki mesafe
        distance = np.sqrt((estimated_gaze_x - self.ball_x)**2 + (estimated_gaze_y - self.ball_y)**2)
        
        if distance < self.focus_threshold:
            if not self.is_focused:
                self.is_focused = True
                self.focus_start_time = time.time()
            else:
                self.focus_duration = time.time() - self.focus_start_time
                
                # 1 saniye odaklanma başarılı
                if self.focus_duration >= 1.0:
                    self.score += 5
                    self.success_message = "+5 PUAN! Harika odaklanma!"
                    self.success_time = time.time()
                    self.reset_focus()
                    self.reset_ball()
        else:
            if self.is_focused and self.focus_duration > 0.1:
                self.warning_message = "UYARI: Odaklanma kaybedildi!"
                self.warning_time = time.time()
            self.reset_focus()
    
    def reset_focus(self):
        """Odaklanmayı sıfırla"""
        self.is_focused = False
        self.focus_start_time = None
        self.focus_duration = 0.0
    
    def reset_ball(self):
        """Yeni top pozisyonu ve hız"""
        self.ball_x = random.randint(self.ball_radius + 100, self.screen_width - self.ball_radius - 100)
        self.ball_y = random.randint(self.ball_radius + 100, self.screen_height - self.ball_radius - 100)
        self.ball_speed_x = random.choice([-6, -5, -4, 4, 5, 6])
        self.ball_speed_y = random.choice([-6, -5, -4, 4, 5, 6])
        self.ball_color = self.random_color()
    
    def draw_ui(self, frame):
        """Arayüzü çiz"""
        # Topu çiz
        cv2.circle(frame, (int(self.ball_x), int(self.ball_y)), self.ball_radius, self.ball_color, -1)
        cv2.circle(frame, (int(self.ball_x), int(self.ball_y)), self.ball_radius, (255, 255, 255), 2)
        
        # Skor
        cv2.putText(frame, f"SKOR: {self.score}", (20, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
        
        # Odaklanma süresi
        focus_text = f"Odak Suresi: {self.focus_duration:.2f} saniye"
        cv2.putText(frame, focus_text, (20, 100), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        
        # Göz durumu
        if self.eyes_detected:
            eye_status = "Gozler Tespit Edildi"
            eye_color = (0, 255, 0)
        else:
            eye_status = "Gozler Tespit Edilemedi!"
            eye_color = (0, 0, 255)
        cv2.putText(frame, eye_status, (20, 150), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, eye_color, 2)
        
        # Odaklanma durumu
        if self.is_focused:
            focus_status = f"ODAKLANILIYOR... ({self.focus_duration:.1f}s / 1.0s)"
            cv2.putText(frame, focus_status, (self.screen_width//2 - 200, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            
            # İlerleme çubuğu
            progress = min(self.focus_duration / 1.0, 1.0)
            bar_width = 300
            bar_height = 20
            bar_x = self.screen_width//2 - bar_width//2
            bar_y = 60
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (100, 100, 100), -1)
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + int(bar_width * progress), bar_y + bar_height), (0, 255, 0), -1)
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (255, 255, 255), 2)
        
        # Uyarı mesajı
        if self.warning_message and time.time() - self.warning_time < 2:
            cv2.putText(frame, self.warning_message, (self.screen_width//2 - 200, self.screen_height//2), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        
        # Başarı mesajı
        if self.success_message and time.time() - self.success_time < 2:
            cv2.putText(frame, self.success_message, (self.screen_width//2 - 200, self.screen_height//2), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
        
        # Talimatlar
        instructions = "Gozlerinizle hareket eden topu takip edin. 1 saniye odaklanin = +5 puan!"
        cv2.putText(frame, instructions, (20, self.screen_height - 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
        
        # Çıkış talimatı
        cv2.putText(frame, "Cikmak icin 'Q' tusuna basin", (self.screen_width - 300, self.screen_height - 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
        
        return frame
    
    def run(self):
        """Ana döngü"""
        print("Göz Odak Takip Oyunu Başlatılıyor...")
        print("Kameranızın önüne geçin ve gözlerinizi açık tutun.")
        print("Hareket eden topu gözlerinizle takip edin.")
        print("Çıkmak için 'Q' tuşuna basın.")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Kamera okunamadı!")
                break
            
            # Ayna etkisi
            frame = cv2.flip(frame, 1)
            
            # Göz tespiti
            frame = self.detect_eyes(frame)
            
            # Top güncelle
            self.update_ball()
            
            # Odaklanma kontrolü
            self.check_focus()
            
            # Arayüzü çiz
            frame = self.draw_ui(frame)
            
            # Göster
            cv2.imshow('Goz Odak Takip Oyunu', frame)
            
            # Çıkış kontrolü
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Temizlik
        self.cap.release()
        cv2.destroyAllWindows()
        print(f"\nOyun bitti! Toplam skor: {self.score}")

if __name__ == "__main__":
    trainer = EyeFocusTrainer()
    trainer.run()
