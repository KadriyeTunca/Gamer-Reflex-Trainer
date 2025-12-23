import cv2
import numpy as np
import random
import time
import csv
import os
from datetime import datetime

# =====================
# AYARLAR
# =====================
WIDTH, HEIGHT = 1000, 800

PLAYER_COLOR = (180, 105, 240)  # PEMBE
TEXT_COLOR = (255, 255, 255)
SUCCESS_COLOR = (0, 255, 0)     # YEŞİL - DOĞRU KOMUT
ERROR_COLOR = (0, 0, 255)       # KIRMIZI - YANLIŞ KOMUT

PLAYER_RADIUS = 18
MAX_RADIUS = 50

BASE_SPEED = 4.0
SPEED_INCREASE = 0.2

MAX_MOVES = 20

COMMANDS = ["YUKARI", "ASAGI", "SOL", "SAG"]
COMMAND_DISPLAY = {
    "YUKARI": "YUKARI (W)",
    "ASAGI": "ASAGI (S)",
    "SOL": "SOL (A)",
    "SAG": "SAG (D)"
}
KEY_MAP = {
    "YUKARI": [ord("w"), ord("W"), 2490368],  # w, W, yukarı ok tuşu
    "ASAGI": [ord("s"), ord("S"), 2621440],   # s, S, aşağı ok tuşu
    "SOL": [ord("a"), ord("A"), 2424832],     # a, A, sol ok tuşu
    "SAG": [ord("d"), ord("D"), 2555904]      # d, D, sağ ok tuşu
}

# =====================
# YARDIMCI FONKSİYONLAR
# =====================
def get_new_command(direction, player_x, player_y, player_radius):
    """Ekran kenarlarında mantıksız komutları engelle ve mevcut yönü engelle"""
    available = COMMANDS.copy()
    
    # Üst kenarda YUKARI engelle
    if player_y - player_radius <= 140:
        if "YUKARI" in available:
            available.remove("YUKARI")
    
    # Alt kenarda ASAGI engelle
    if player_y + player_radius >= HEIGHT - 20:
        if "ASAGI" in available:
            available.remove("ASAGI")
    
    # Sol kenarda SOL engelle
    if player_x - player_radius <= 20:
        if "SOL" in available:
            available.remove("SOL")
    
    # Sağ kenarda SAG engelle
    if player_x + player_radius >= WIDTH - 20:
        if "SAG" in available:
            available.remove("SAG")
    
    # MEVCUT YÖNDEKİ KOMUTU ENGELLE (yukarı giderken yukarı çıkmasın)
    if direction in available:
        available.remove(direction)
    
    # Eğer hiç komut kalmadıysa (çok nadir), tersi yönü ver
    if not available:
        opposite = {"YUKARI": "ASAGI", "ASAGI": "YUKARI", "SOL": "SAG", "SAG": "SOL"}
        return opposite.get(direction, random.choice(COMMANDS))
    
    return random.choice(available)

# =====================
# OYUN DEĞİŞKENLERİ
# =====================
player_x, player_y = WIDTH // 2, HEIGHT // 2
player_radius = PLAYER_RADIUS

direction = random.choice(COMMANDS)
speed = BASE_SPEED

current_command = get_new_command(direction, player_x, player_y, player_radius)
total_moves = 0
correct_moves = 0

# Görsel geri bildirim için
feedback_time = 0
feedback_type = None  # "success" veya "error"

# Zaman takibi
game_start_time = time.time()
command_start_time = time.time()
reaction_times = []  # Sadece doğru tuşlar için

# CSV kayıt için detaylı veri
move_log = []  # Her hamle kaydedilecek

# =====================
# ANA DÖNGÜ
# =====================
cv2.namedWindow("Stage 2 - Keyboard Reflex")

while total_moves < MAX_MOVES:
    screen = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

    # -----------------
    # OTOMATİK HAREKET
    # -----------------
    if direction == "YUKARI":
        player_y -= speed
    elif direction == "ASAGI":
        player_y += speed
    elif direction == "SOL":
        player_x -= speed
    elif direction == "SAG":
        player_x += speed

    # -----------------
    # SINIR KONTROLÜ VE SEKME
    # -----------------
    # Sol-Sağ sınırlar
    if player_x - player_radius <= 0:
        player_x = player_radius
        direction = "SAG"
    elif player_x + player_radius >= WIDTH:
        player_x = WIDTH - player_radius
        direction = "SOL"
    
    # Üst-Alt sınırlar
    if player_y - player_radius <= 120:
        player_y = 120 + player_radius
        direction = "ASAGI"
    elif player_y + player_radius >= HEIGHT:
        player_y = HEIGHT - player_radius
        direction = "YUKARI"

    # -----------------
    # TUŞ OKUMA
    # -----------------
    key = cv2.waitKey(20) & 0xFF
    if key == 27:  # ESC
        break

    # Herhangi bir oyun tuşuna basıldı mı?
    pressed_command = None
    for cmd, key_codes in KEY_MAP.items():
        if key in key_codes:
            pressed_command = cmd
            break
    
    if pressed_command:
        total_moves += 1
        
        # Reaksiyon süresini hesapla
        reaction_time = time.time() - command_start_time
        
        # DOĞRU TUŞ
        if pressed_command == current_command:
            reaction_times.append(reaction_time)
            
            direction = current_command
            speed += SPEED_INCREASE
            correct_moves += 1
            
            feedback_type = "success"
            feedback_time = time.time()
            
            # O ana kadarki doğruluk oranını hesapla
            current_accuracy = (correct_moves / total_moves) * 100
            
            # O ana kadarki ortalama reaksiyon süresini hesapla (sadece doğrular)
            avg_reaction_so_far = sum(reaction_times) / len(reaction_times)
            
            # Kaydı ekle (doğru)
            move_log.append({
                "saat": datetime.now().strftime("%H:%M"),
                "tur": total_moves,
                "hedef_tus": current_command,
                "basilan_tus": pressed_command,
                "dogru_mu": 1,
                "reaksiyon_suresi": reaction_time,
                "dogruluk_orani": current_accuracy,
                "ort_reaksiyon": avg_reaction_so_far
            })
        
        # YANLIŞ TUŞ
        else:
            direction = pressed_command
            
            feedback_type = "error"
            feedback_time = time.time()
            
            # O ana kadarki doğruluk oranını hesapla
            current_accuracy = (correct_moves / total_moves) * 100
            
            # O ana kadarki ortalama reaksiyon (yanlışta değişmez, son değeri koy)
            avg_reaction_so_far = sum(reaction_times) / len(reaction_times) if reaction_times else 0
            
            # Kaydı ekle (yanlış)
            move_log.append({
                "saat": datetime.now().strftime("%H:%M"),
                "tur": total_moves,
                "hedef_tus": current_command,
                "basilan_tus": pressed_command,
                "dogru_mu": 0,
                "reaksiyon_suresi": reaction_time,
                "dogruluk_orani": current_accuracy,
                "ort_reaksiyon": avg_reaction_so_far
            })
        
        # Yeni komut üret ve zamanlayıcıyı sıfırla
        current_command = get_new_command(direction, player_x, player_y, player_radius)
        command_start_time = time.time()

    # -----------------
    # ÇİZİMLER
    # -----------------
    # Ana daire
    cv2.circle(screen, (int(player_x), int(player_y)),
               int(player_radius), PLAYER_COLOR, -1)

    # Komut yazısı (ortada)
    cv2.putText(
        screen,
        f"KOMUT: {COMMAND_DISPLAY[current_command]}",
        (280, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.4,
        TEXT_COLOR,
        3
    )

    # Skor (sağ üst) - Doğruluk oranı
    cv2.putText(
        screen,
        f"{correct_moves}/{total_moves}",
        (WIDTH - 150, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.2,
        TEXT_COLOR,
        3
    )

    # Hız bilgisi (sol üst)
    cv2.putText(
        screen,
        f"Hiz: {speed:.1f}",
        (30, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (200, 200, 200),
        2
    )

    # Geri bildirim (TIK veya X)
    if feedback_type and time.time() - feedback_time < 0.3:
        if feedback_type == "success":
            # Yeşil TİK - Daire içinde artı
            cv2.circle(screen, (WIDTH // 2, HEIGHT // 2), 60, SUCCESS_COLOR, 8)
            cv2.line(screen, (WIDTH // 2 - 25, HEIGHT // 2), 
                    (WIDTH // 2 + 25, HEIGHT // 2), SUCCESS_COLOR, 8)
            cv2.line(screen, (WIDTH // 2, HEIGHT // 2 - 25), 
                    (WIDTH // 2, HEIGHT // 2 + 25), SUCCESS_COLOR, 8)
        else:
            # Kırmızı X - Çarpı
            cv2.line(screen, (WIDTH // 2 - 30, HEIGHT // 2 - 30), 
                    (WIDTH // 2 + 30, HEIGHT // 2 + 30), ERROR_COLOR, 8)
            cv2.line(screen, (WIDTH // 2 + 30, HEIGHT // 2 - 30), 
                    (WIDTH // 2 - 30, HEIGHT // 2 + 30), ERROR_COLOR, 8)
    else:
        feedback_type = None

    cv2.imshow("Stage 2 - Keyboard Reflex", screen)

# OYUN BİTTİ
total_time = time.time() - game_start_time
accuracy = (correct_moves / total_moves * 100) if total_moves > 0 else 0
avg_reaction = sum(reaction_times) / len(reaction_times) if reaction_times else 0

# CSV'ye kaydet - HER HAMLE AYRI SATIR
results_folder = "results"
csv_file = os.path.join(results_folder, "performance_log_keyboard.csv")

# results klasörü yoksa oluştur
if not os.path.exists(results_folder):
    os.makedirs(results_folder)

# Dosya var mı ve içinde başlık var mı kontrol et
file_exists = os.path.isfile(csv_file)
needs_header = True

if file_exists:
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            # Eğer dosyada başlık varsa (Saat ile başlıyorsa)
            if first_line.startswith("Saat"):
                needs_header = False
    except:
        needs_header = True

with open(csv_file, 'a', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    
    # Başlık satırı (sadece gerekiyorsa)
    if needs_header:
        writer.writerow([
            "Saat", "Tur", "HedefTus", "BasilanTus", "DogruMu", "ReaksiyonSuresi", "DogrulukOrani", "OrtReaksiyon"
        ])
    
    # Her hamleyi kaydet
    for move in move_log:
        writer.writerow([
            move['saat'],
            move['tur'],
            move['hedef_tus'],
            move['basilan_tus'],
            move['dogru_mu'],
            f"{move['reaksiyon_suresi']:.3f}",
            f"{move['dogruluk_orani']:.1f}",
            f"{move['ort_reaksiyon']:.3f}"
        ])

print("\n" + "="*50)
print("OYUN BİTTİ!")
print("="*50)
print(f"Doğruluk Oranı: {correct_moves}/{total_moves} (%{accuracy:.1f})")
print(f"Toplam Süre: {total_time:.2f} saniye")
print(f"Ortalama Reaksiyon Süresi: {avg_reaction:.3f} saniye")
print(f"Final Hız: {speed:.1f}")
print("="*50)
print(f"✓ {len(move_log)} hamle kaydedildi: {csv_file}")

cv2.destroyAllWindows()