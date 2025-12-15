import cv2
import numpy as np
import time
import random
import csv
import os
from datetime import datetime

# Ekran boyutu
WIDTH, HEIGHT = 1000, 800

# Renkler (BGR)
COLORS = {
    "pembe": (180, 105, 240),
    "sari": (0, 255, 255),
    "mavi": (255, 0, 0),
    "yesil": (106, 187, 106)
}

# Oyun durumu
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
results = []

# Hız kontrolü
base_speed = 3
speed_multiplier = 1.0

# Dosya ayarları
os.makedirs("results", exist_ok=True)
session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_path = f"results/session_{session_id}.csv"

with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Tur", "DogruMu", "TepkiSuresi", "HedefRenk", "TiklananRenk"])

# ---------------- SCREENS ---------------- #

def draw_start_screen():
    screen = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    cv2.putText(screen, "GAMER REFLEX TRAINER", (200, 150),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
    cv2.putText(screen, "BASLA", (430, 400),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
    cv2.rectangle(screen, (380, 350), (620, 450), (255, 0, 0), 3)
    return screen

def draw_end_screen():
    screen = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    avg_reaction = np.mean(reaction_times) if reaction_times else 0
    total_clicks = correct_clicks + wrong_clicks
    error_rate = (wrong_clicks / total_clicks * 100) if total_clicks > 0 else 0

    cv2.putText(screen, "TEST TAMAMLANDI", (300, 150),
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
    cv2.putText(screen, f"Kaydedildi: {csv_path}", (200, 500),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)
    cv2.putText(screen, "ESC ile cikis yapabilirsiniz", (300, 600),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 1)
    return screen

# ---------------- GAME LOGIC ---------------- #

def generate_round():
    global targets, target_color_name, start_time, total_rounds
    total_rounds += 1
    target_color_name = random.choice(list(COLORS.keys()))
    distractors = [c for c in COLORS.keys() if c != target_color_name]
    random.shuffle(distractors)
    targets = []

    def create_target(color_name):
        x = random.randint(100, WIDTH - 100)
        y = random.randint(150, HEIGHT - 100)
        r = random.randint(30, 60)
        dx = random.choice([-1, 1]) * base_speed * speed_multiplier
        dy = random.choice([-1, 1]) * base_speed * speed_multiplier
        return [x, y, r, color_name, COLORS[color_name], dx, dy]

    targets.append(create_target(target_color_name))

    for i in range(random.randint(2, 3)):
        targets.append(create_target(distractors[i % len(distractors)]))

    start_time = time.time()

def draw_game():
    game_screen = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    cv2.putText(game_screen, f"Hedef renk: {target_color_name.upper()}",
                (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2,
                COLORS[target_color_name], 3)

    for t in targets:
        t[0] += t[5]
        t[1] += t[6]

        if t[0] - t[2] <= 0 or t[0] + t[2] >= WIDTH:
            t[5] *= -1
        if t[1] - t[2] <= 100 or t[1] + t[2] >= HEIGHT:
            t[6] *= -1

        cv2.circle(game_screen, (int(t[0]), int(t[1])), t[2], t[4], -1)

    return game_screen

# ---------------- INPUT ---------------- #

def mouse_callback(event, x, y, flags, param):
    global game_started, correct_clicks, wrong_clicks, game_over, speed_multiplier

    if not game_started and not game_over:
        if event == cv2.EVENT_LBUTTONDOWN and 380 <= x <= 620 and 350 <= y <= 450:
            game_started = True
            generate_round()
        return

    if event == cv2.EVENT_LBUTTONDOWN and game_started:
        for t in targets:
            if (x - t[0]) ** 2 + (y - t[1]) ** 2 <= t[2] ** 2:
                rt = time.time() - start_time

                if t[3] == target_color_name:
                    correct_clicks += 1
                    reaction_times.append(rt)
                    results.append([total_rounds, 1, rt, target_color_name, t[3]])
                else:
                    wrong_clicks += 1
                    speed_multiplier += 0.2
                    results.append([total_rounds, 0, rt, target_color_name, t[3]])

                with open(csv_path, "a", newline="", encoding="utf-8") as f:
                    csv.writer(f).writerow(results[-1])

                if total_rounds >= 10:
                    game_over = True
                else:
                    generate_round()
                break

# ---------------- MAIN ---------------- #

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
    if cv2.waitKey(10) & 0xFF == 27:
        break

cv2.destroyAllWindows()
