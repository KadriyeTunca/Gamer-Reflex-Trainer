import cv2
import numpy as np
import time
import random
import csv
import os
from datetime import datetime

# Ekran boyutu tanımlıyoruz
WIDTH, HEIGHT = 1000, 800
# Renk tanımları (BGR) 
COLORS = { 
          "pembe": (180, 105, 240), 
          "sari": (0, 255, 255), 
          "mavi": (255, 0, 0), 
          "yesil": (106, 187, 106) 
          }
          
# Global değişkenler
game_started = False
game_over = False
targets = []
target_color_name = None
start_time = None

# Performans verileri
total_rounds = 0
correct_clicks = 0
wrong_clicks = 0
reaction_times = []
results = []  # CSV için veriler

# Dosya oluşturma
os.makedirs("results", exist_ok=True)
session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_path = f"results/session_{session_id}.csv"

# CSV başlıklarını oluştur
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Tur", "DogruMu", "TepkiSuresi", "HedefRenk", "TiklananRenk"])

def draw_start_screen():
    screen = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    cv2.putText(screen, 'GAMER REFLEX TRAINER', (200, 150),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
    cv2.putText(screen, 'BASLA', (430, 400),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
    cv2.rectangle(screen, (380, 350), (620, 450), (255, 0, 0), 3)
    return screen

def draw_end_screen():
    screen = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    avg_reaction = np.mean(reaction_times) if reaction_times else 0
    total_clicks = correct_clicks + wrong_clicks
    error_rate = (wrong_clicks / total_clicks * 100) if total_clicks > 0 else 0

    cv2.putText(screen, 'TEST TAMAMLANDI', (300, 150),
                cv2.FONT_HERSHEY_SIMPLEX, 1.6, (0, 255, 255), 3)
    cv2.putText(screen, f"Toplam Tur: {total_rounds}", (300, 250),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(screen, f"Dogru Tiklama: {correct_clicks}", (300, 300),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(screen, f"Yanlis Tiklama: {wrong_clicks}", (300, 350),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(screen, f"Ortalama Tepki Suresi: {avg_reaction:.3f} sn", (300, 400),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(screen, f"Hata Orani: %{error_rate:.1f}", (300, 450),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    cv2.putText(screen, f"Kaydedildi: results/session_{session_id}.csv", (200, 500),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)
    cv2.putText(screen, "ESC ile cikis yapabilirsiniz", (300, 600),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 1)
    return screen

def generate_round():
    global targets, target_color_name, start_time, total_rounds
    total_rounds += 1
    target_color_name = random.choice(list(COLORS.keys()))
    target_color = COLORS[target_color_name]
    distractors = [c for c in COLORS.keys() if c != target_color_name]
    random.shuffle(distractors)
    targets = []
    x, y = random.randint(100, WIDTH-100), random.randint(150, HEIGHT-100)
    radius = random.randint(30, 60)
    targets.append((x, y, radius, target_color_name, target_color))
    for i in range(random.randint(2, 3)):
        color_name = distractors[i % len(distractors)]
        color = COLORS[color_name]
        x, y = random.randint(100, WIDTH-100), random.randint(150, HEIGHT-100)
        radius = random.randint(30, 60)
        targets.append((x, y, radius, color_name, color))
    start_time = time.time()

def draw_game():
    game_screen = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    color_of_text = COLORS[target_color_name]
    cv2.putText(game_screen, f"Hedef renk: {target_color_name.upper()}",
                (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color_of_text, 3)
    for (x, y, r, name, color) in targets:
        cv2.circle(game_screen, (x, y), r, color, -1)
    return game_screen

def mouse_callback(event, x, y, flags, param):
    global game_started, correct_clicks, wrong_clicks, game_over
    if not game_started and not game_over:
        if event == cv2.EVENT_LBUTTONDOWN and 380 <= x <= 620 and 350 <= y <= 450:
            game_started = True
            generate_round()
        return

    if event == cv2.EVENT_LBUTTONDOWN and game_started:
        for (cx, cy, r, color_name, color) in targets:
            if (x - cx) ** 2 + (y - cy) ** 2 <= r ** 2:
                if color_name == target_color_name:
                    rt = time.time() - start_time
                    reaction_times.append(rt)
                    correct_clicks += 1
                    results.append([total_rounds, 1, rt, target_color_name, color_name])
                else:
                    rt = time.time() - start_time
                    wrong_clicks += 1
                    results.append([total_rounds, 0, rt, target_color_name, color_name])

                # CSV'ye kaydet
                with open(csv_path, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(results[-1])

                if total_rounds >= 10:
                    game_over = True
                else:
                    generate_round()
                break

cv2.namedWindow("Gamer Reflex Trainer")
cv2.setMouseCallback("Gamer Reflex Trainer", mouse_callback)

while True:
    if not game_started and not game_over:
        frame = draw_start_screen()
    elif game_over:
        frame = draw_end_screen()
    else:
        frame = draw_game()

    cv2.imshow("Gamer Reflex Trainer", frame)
    key = cv2.waitKey(10) & 0xFF
    if key == 27:
        break

cv2.destroyAllWindows()
