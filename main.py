"""
Gamer Reflex Trainer - Ana Uygulama
Üç aşamalı refleks test sistemi:
1. Mouse Refleks Testi
2. Klavye Refleks Testi  
3. Göz Odak Takip Testi (MediaPipe)
"""

import cv2
import numpy as np
import time
import random
import csv
import os
from datetime import datetime
from collections import deque

# MediaPipe sadece göz takibi için gerekli
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("UYARI: MediaPipe kurulu değil. Göz takibi özelliği devre dışı.")
    print("Kurmak için: pip install mediapipe==0.10.9")

# Global oyuncu bilgileri
player_name = ""
all_stage_results = []  # Her aşamanın sonuçlarını tutar


def get_player_name():
    """İsim giriş ekranı"""
    global player_name
    WIDTH, HEIGHT = 800, 600
    name = ""
    
    while True:
        screen = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        
        cv2.putText(screen, "GAMER REFLEX TRAINER", (150, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
        cv2.putText(screen, "Adinizi girin:", (280, 250),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # İsim kutusu
        cv2.rectangle(screen, (200, 280), (600, 340), (50, 50, 50), -1)
        cv2.rectangle(screen, (200, 280), (600, 340), (0, 255, 0), 2)
        cv2.putText(screen, name + "_", (220, 325),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
        
        cv2.putText(screen, "ENTER = Basla | BACKSPACE = Sil", (220, 420),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (150, 150, 150), 2)
        
        cv2.imshow("Gamer Reflex Trainer", screen)
        key = cv2.waitKey(50) & 0xFF
        
        if key == 13 and len(name) > 0:  # ENTER
            player_name = name
            cv2.destroyAllWindows()
            return
        elif key == 8 and len(name) > 0:  # BACKSPACE
            name = name[:-1]
        elif key == 27:  # ESC
            cv2.destroyAllWindows()
            return None
        elif 32 <= key <= 126 and len(name) < 15:  # Printable chars
            name += chr(key)


def show_stage_stats(stage_name, correct, total, avg_reaction, next_stage=None):
    """Aşama sonrası istatistik ekranı"""
    global all_stage_results
    WIDTH, HEIGHT = 900, 650
    
    accuracy = (correct / total * 100) if total > 0 else 0
    all_stage_results.append({
        'stage': stage_name, 'correct': correct, 'total': total,
        'accuracy': accuracy, 'avg_reaction': avg_reaction
    })
    
    while True:
        screen = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        
        cv2.putText(screen, f"{stage_name}", (300, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 255, 255), 3)
        cv2.putText(screen, "TAMAMLANDI!", (340, 130),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(screen, f"Oyuncu: {player_name}", (340, 180),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2)
        
        cv2.putText(screen, f"Dogru: {correct}/{total}", (300, 260),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        cv2.putText(screen, f"Dogruluk: %{accuracy:.1f}", (300, 310),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        cv2.putText(screen, f"Ort. Tepki: {avg_reaction:.3f}s", (300, 360),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        
        if next_stage:
            cv2.putText(screen, "[ENTER] Devam", (340, 450),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(screen, "[ESC] Ana Menu", (300, 510),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (150, 150, 150), 2)
        
        cv2.imshow("Sonuclar", screen)
        key = cv2.waitKey(100) & 0xFF
        
        if key == 13:  # ENTER
            cv2.destroyAllWindows()
            return True
        elif key == 27:  # ESC
            cv2.destroyAllWindows()
            return False


def show_final_evaluation():
    """Tüm aşamalar sonrası final değerlendirmesi"""
    global all_stage_results
    WIDTH, HEIGHT = 900, 700
    
    if not all_stage_results:
        return
    
    total_correct = sum(r['correct'] for r in all_stage_results)
    total_all = sum(r['total'] for r in all_stage_results)
    avg_accuracy = sum(r['accuracy'] for r in all_stage_results) / len(all_stage_results)
    avg_reaction = sum(r['avg_reaction'] for r in all_stage_results if r['avg_reaction'] > 0)
    avg_reaction = avg_reaction / len([r for r in all_stage_results if r['avg_reaction'] > 0]) if avg_reaction > 0 else 0
    
    # Değerlendirme
    if avg_reaction < 0.4 and avg_accuracy >= 85:
        rating = "MUKEMMELSIN!"
        rating_color = (0, 255, 255)
    elif avg_reaction < 0.6 and avg_accuracy >= 70:
        rating = "Cok iyi!"
        rating_color = (0, 255, 0)
    elif avg_accuracy >= 50:
        rating = "Fena degil"
        rating_color = (0, 165, 255)
    else:
        rating = "Pratik yap!"
        rating_color = (0, 0, 255)
    
    while True:
        screen = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        
        cv2.putText(screen, "FINAL DEGERLENDIRMESI", (220, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 255, 255), 3)
        cv2.putText(screen, f"Oyuncu: {player_name}", (350, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (200, 200, 200), 2)
        
        y = 180
        for r in all_stage_results:
            text = f"{r['stage']}: %{r['accuracy']:.0f} - {r['avg_reaction']:.3f}s"
            cv2.putText(screen, text, (200, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            y += 50
        
        cv2.line(screen, (150, y), (750, y), (100, 100, 100), 2)
        y += 40
        
        cv2.putText(screen, f"Toplam Dogru: {total_correct}/{total_all}", (200, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(screen, f"Genel Dogruluk: %{avg_accuracy:.1f}", (200, y + 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(screen, f"Ort. Tepki Suresi: {avg_reaction:.3f}s", (200, y + 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        cv2.putText(screen, rating, (300, y + 180),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.8, rating_color, 4)
        
        cv2.putText(screen, "[ESC] Cikis", (380, HEIGHT - 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (150, 150, 150), 2)
        
        cv2.imshow("Final", screen)
        if cv2.waitKey(100) & 0xFF == 27:
            cv2.destroyAllWindows()
            all_stage_results = []
            return


# =====================================================================
# STAGE 1: MOUSE REFLEKS TESTİ
# =====================================================================

def stage_1_mouse_test():
    """Mouse ile görsel hedeflere tepki süresi ölçümü"""
    
    # EKRAN BOYUTU
    WIDTH, HEIGHT = 1000, 800

    # RENKLER (BGR)
    COLORS = {
        "pembe": (180, 105, 240),
        "sari": (0, 255, 255),
        "mavi": (255, 0, 0),
        "yesil": (106, 187, 106)
    }

    # OYUN DURUMU
    game_started = False
    game_over = False
    targets = []
    target_color_name = None
    start_time = None

    # PERFORMANS
    total_rounds = 0
    correct_clicks = 0
    wrong_clicks = 0
    reaction_times = []

    # HIZ KONTROLÜ
    base_speed = 3
    speed_multiplier = 1.0

    # CSV
    os.makedirs("results", exist_ok=True)
    csv_path = "results/performance_log.csv"

    if not os.path.exists(csv_path):
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Asama", "Tur", "DogruMu", "TepkiSuresi",
                "HedefRenk", "TiklananRenk", "Zaman"
            ])

    def draw_start_screen():
        screen = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        cv2.putText(screen, "GAMER REFLEX TRAINER", (210, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
        cv2.putText(screen, "STAGE 1: MOUSE TEST", (300, 220),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(screen, "BASLA", (430, 400),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        cv2.rectangle(screen, (380, 330), (620, 450), (255, 0, 0), 3)
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
        cv2.putText(screen, "ESC ile cikis", (380, 550),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (200, 200, 200), 1)
        return screen

    def generate_round():
        nonlocal targets, target_color_name, start_time, total_rounds
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
            targets.append(create_target(distractors[i]))
        start_time = time.time()

    def draw_game():
        screen = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        cv2.putText(screen, f"Hedef renk: {target_color_name.upper()}",
                    (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2,
                    COLORS[target_color_name], 3)

        for t in targets:
            t[0] += t[5]
            t[1] += t[6]
            if t[0] - t[2] <= 0 or t[0] + t[2] >= WIDTH:
                t[5] *= -1
            if t[1] - t[2] <= 100 or t[1] + t[2] >= HEIGHT:
                t[6] *= -1
            cv2.circle(screen, (int(t[0]), int(t[1])), t[2], t[4], -1)
        return screen

    def mouse_callback(event, x, y, flags, param):
        nonlocal game_started, game_over
        nonlocal correct_clicks, wrong_clicks, speed_multiplier

        if not game_started and not game_over:
            if event == cv2.EVENT_LBUTTONDOWN and 380 <= x <= 620 and 350 <= y <= 450:
                game_started = True
                generate_round()
            return

        if event == cv2.EVENT_LBUTTONDOWN and game_started:
            for t in targets:
                if (x - t[0]) ** 2 + (y - t[1]) ** 2 <= t[2] ** 2:
                    rt = time.time() - start_time
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    if t[3] == target_color_name:
                        correct_clicks += 1
                        reaction_times.append(rt)
                        row = ["Mouse", total_rounds, 1, rt, target_color_name, t[3], now]
                    else:
                        wrong_clicks += 1
                        speed_multiplier += 0.2
                        row = ["Mouse", total_rounds, 0, rt, target_color_name, t[3], now]

                    with open(csv_path, "a", newline="", encoding="utf-8") as f:
                        csv.writer(f).writerow(row)

                    if total_rounds >= 10:
                        game_over = True
                    else:
                        generate_round()
                    break

    cv2.namedWindow("Stage 1 - Mouse Test")
    cv2.setMouseCallback("Stage 1 - Mouse Test", mouse_callback)

    while True:
        if not game_started and not game_over:
            frame = draw_start_screen()
        elif game_over:
            frame = draw_end_screen()
        else:
            frame = draw_game()

        cv2.imshow("Stage 1 - Mouse Test", frame)
        if cv2.waitKey(10) & 0xFF == 27:
            break

    cv2.destroyAllWindows()
    avg_reaction = np.mean(reaction_times) if reaction_times else 0
    return correct_clicks, total_rounds, avg_reaction


# =====================================================================
# STAGE 2: KLAVYE REFLEKS TESTİ
# =====================================================================

def stage_2_keyboard_test():
    """W, A, S, D tuşları ile yön tabanlı refleks ölçümü"""
    
    WIDTH, HEIGHT = 1000, 800

    PLAYER_COLOR = (180, 105, 240)
    TEXT_COLOR = (255, 255, 255)
    SUCCESS_COLOR = (0, 255, 0)
    ERROR_COLOR = (0, 0, 255)

    PLAYER_RADIUS = 18
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
        "YUKARI": [ord("w"), ord("W")],
        "ASAGI": [ord("s"), ord("S")],
        "SOL": [ord("a"), ord("A")],
        "SAG": [ord("d"), ord("D")]
    }

    def get_new_command(direction, player_x, player_y, player_radius):
        available = COMMANDS.copy()
        if player_y - player_radius <= 140 and "YUKARI" in available:
            available.remove("YUKARI")
        if player_y + player_radius >= HEIGHT - 20 and "ASAGI" in available:
            available.remove("ASAGI")
        if player_x - player_radius <= 20 and "SOL" in available:
            available.remove("SOL")
        if player_x + player_radius >= WIDTH - 20 and "SAG" in available:
            available.remove("SAG")
        if direction in available:
            available.remove(direction)
        if not available:
            opposite = {"YUKARI": "ASAGI", "ASAGI": "YUKARI", "SOL": "SAG", "SAG": "SOL"}
            return opposite.get(direction, random.choice(COMMANDS))
        return random.choice(available)

    player_x, player_y = WIDTH // 2, HEIGHT // 2
    player_radius = PLAYER_RADIUS
    direction = random.choice(COMMANDS)
    speed = BASE_SPEED
    current_command = get_new_command(direction, player_x, player_y, player_radius)
    
    total_moves = 0
    correct_moves = 0
    feedback_time = 0
    feedback_type = None
    
    game_start_time = time.time()
    command_start_time = time.time()
    reaction_times = []
    move_log = []

    cv2.namedWindow("Stage 2 - Keyboard Reflex")

    while total_moves < MAX_MOVES:
        screen = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

        # Otomatik hareket
        if direction == "YUKARI":
            player_y -= speed
        elif direction == "ASAGI":
            player_y += speed
        elif direction == "SOL":
            player_x -= speed
        elif direction == "SAG":
            player_x += speed

        # Sınır kontrolü
        if player_x - player_radius <= 0:
            player_x = player_radius
            direction = "SAG"
        elif player_x + player_radius >= WIDTH:
            player_x = WIDTH - player_radius
            direction = "SOL"
        if player_y - player_radius <= 120:
            player_y = 120 + player_radius
            direction = "ASAGI"
        elif player_y + player_radius >= HEIGHT:
            player_y = HEIGHT - player_radius
            direction = "YUKARI"

        key = cv2.waitKey(20) & 0xFF
        if key == 27:
            break

        pressed_command = None
        for cmd, key_codes in KEY_MAP.items():
            if key in key_codes:
                pressed_command = cmd
                break

        if pressed_command:
            total_moves += 1
            reaction_time = time.time() - command_start_time

            if pressed_command == current_command:
                reaction_times.append(reaction_time)
                direction = current_command
                speed += SPEED_INCREASE
                correct_moves += 1
                feedback_type = "success"
            else:
                direction = pressed_command
                feedback_type = "error"
            
            feedback_time = time.time()
            
            current_accuracy = (correct_moves / total_moves) * 100
            avg_reaction_so_far = sum(reaction_times) / len(reaction_times) if reaction_times else 0
            
            move_log.append({
                "saat": datetime.now().strftime("%H:%M"),
                "tur": total_moves,
                "hedef_tus": current_command,
                "basilan_tus": pressed_command,
                "dogru_mu": 1 if pressed_command == current_command else 0,
                "reaksiyon_suresi": reaction_time,
                "dogruluk_orani": current_accuracy,
                "ort_reaksiyon": avg_reaction_so_far
            })
            
            current_command = get_new_command(direction, player_x, player_y, player_radius)
            command_start_time = time.time()

        # Çizimler
        cv2.circle(screen, (int(player_x), int(player_y)), int(player_radius), PLAYER_COLOR, -1)
        cv2.putText(screen, f"KOMUT: {COMMAND_DISPLAY[current_command]}", (280, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.4, TEXT_COLOR, 3)
        cv2.putText(screen, f"{correct_moves}/{total_moves}", (WIDTH - 150, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, TEXT_COLOR, 3)
        cv2.putText(screen, f"Hiz: {speed:.1f}", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (200, 200, 200), 2)

        if feedback_type and time.time() - feedback_time < 0.3:
            if feedback_type == "success":
                cv2.circle(screen, (WIDTH // 2, HEIGHT // 2), 60, SUCCESS_COLOR, 8)
            else:
                cv2.line(screen, (WIDTH // 2 - 30, HEIGHT // 2 - 30),
                        (WIDTH // 2 + 30, HEIGHT // 2 + 30), ERROR_COLOR, 8)
                cv2.line(screen, (WIDTH // 2 + 30, HEIGHT // 2 - 30),
                        (WIDTH // 2 - 30, HEIGHT // 2 + 30), ERROR_COLOR, 8)
        else:
            feedback_type = None

        cv2.imshow("Stage 2 - Keyboard Reflex", screen)

    # Sonuç
    total_time = time.time() - game_start_time
    accuracy = (correct_moves / total_moves * 100) if total_moves > 0 else 0
    avg_reaction = sum(reaction_times) / len(reaction_times) if reaction_times else 0

    # CSV kaydet
    os.makedirs("results", exist_ok=True)
    csv_file = "results/performance_log_keyboard.csv"
    
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Saat", "Tur", "HedefTus", "BasilanTus", "DogruMu",
                           "ReaksiyonSuresi", "DogrulukOrani", "OrtReaksiyon"])
        for move in move_log:
            writer.writerow([
                move['saat'], move['tur'], move['hedef_tus'], move['basilan_tus'],
                move['dogru_mu'], f"{move['reaksiyon_suresi']:.3f}",
                f"{move['dogruluk_orani']:.1f}", f"{move['ort_reaksiyon']:.3f}"
            ])

    print(f"\nOYUN BİTTİ! Doğruluk: {accuracy:.1f}%, Ort. Reaksiyon: {avg_reaction:.3f}s")
    cv2.destroyAllWindows()
    return correct_moves, total_moves, avg_reaction


# =====================================================================
# STAGE 3: GÖZ ODAK TAKİP TESTİ
# =====================================================================

def stage_3_eye_tracking():
    """MediaPipe ile göz takibi ve odaklanma testi"""
    
    if not MEDIAPIPE_AVAILABLE:
        print("HATA: MediaPipe kurulu değil!")
        print("Kurmak için: pip install mediapipe==0.10.9")
        return

    # Sabitler
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    BALL_RADIUS = 45
    BALL_SPEED_OPTIONS = [-5, -4, -3, 3, 4, 5]
    FOCUS_THRESHOLD = 100
    FOCUS_REQUIRED_TIME = 1.0
    POINT_REWARD = 5
    SMOOTHING_FACTOR = 0.22
    GAZE_HISTORY_SIZE = 6
    FOCUS_LOSS_TOLERANCE = 0.5
    FOCUS_DECAY_RATE = 0.3
    DETECTION_CONFIDENCE = 0.7
    TRACKING_CONFIDENCE = 0.7
    CALIBRATION_HOLD_TIME = 2.0
    CALIBRATION_STABILITY_THRESHOLD = 0.04

    COLORS = {
        'yellow': (0, 255, 255), 'magenta': (255, 0, 255),
        'green': (0, 255, 0), 'orange': (0, 165, 255),
        'blue': (255, 0, 0), 'red': (0, 0, 255),
        'cyan': (255, 255, 0), 'purple': (128, 0, 255),
        'white': (255, 255, 255), 'gray': (150, 150, 150),
        'dark_gray': (50, 50, 50),
    }

    LANDMARK_INDICES = {
        'left_iris_center': 468, 'right_iris_center': 473,
        'left_eye_left': 33, 'left_eye_right': 133,
        'right_eye_left': 362, 'right_eye_right': 263,
        'left_eye_top': 159, 'left_eye_bottom': 145,
        'right_eye_top': 386, 'right_eye_bottom': 374,
    }

    def get_random_bright_color():
        color_list = ['yellow', 'magenta', 'green', 'orange', 'blue', 'red', 'cyan', 'purple']
        return COLORS[random.choice(color_list)]

    def calculate_distance(x1, y1, x2, y2):
        return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def clamp(value, min_val, max_val):
        return max(min_val, min(max_val, value))

    class EyeFocusTrainer:
        def __init__(self):
            self._init_camera()
            self._init_mediapipe()
            self._init_ball()
            self._init_game_state()
            self._init_eye_tracking()
            self._init_calibration()

        def _init_camera(self):
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, SCREEN_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, SCREEN_HEIGHT)
            self.screen_width = SCREEN_WIDTH
            self.screen_height = SCREEN_HEIGHT

        def _init_mediapipe(self):
            self.mp_face_mesh = mp.solutions.face_mesh
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=DETECTION_CONFIDENCE,
                min_tracking_confidence=TRACKING_CONFIDENCE
            )

        def _init_ball(self):
            self.ball_radius = BALL_RADIUS
            self.ball_x = self.screen_width // 2
            self.ball_y = self.screen_height // 2
            self.ball_speed_x = random.choice(BALL_SPEED_OPTIONS)
            self.ball_speed_y = random.choice(BALL_SPEED_OPTIONS)
            self.ball_color = get_random_bright_color()

        def _init_game_state(self):
            self.score = 0
            self.focus_start_time = None
            self.focus_duration = 0.0
            self.is_focused = False
            self.warning_message = ""
            self.warning_time = 0
            self.success_message = ""
            self.success_time = 0
            self.focus_loss_start = None
            self.accumulated_focus = 0.0
            
            # CSV logging for eye tracking
            self.focus_events = []  # List to store all focus events
            self.game_start_time = time.time()
            self.total_focus_attempts = 0
            self.successful_focuses = 0
            self.focus_durations = []  # List to store successful focus durations

        def _init_eye_tracking(self):
            self.iris_x = 0.5
            self.iris_y = 0.5
            self.face_detected = False
            self.eyes_valid = False
            self.gaze_x = self.screen_width // 2
            self.gaze_y = self.screen_height // 2
            self.gaze_history_x = deque(maxlen=GAZE_HISTORY_SIZE)
            self.gaze_history_y = deque(maxlen=GAZE_HISTORY_SIZE)
            self.prev_gaze_x = self.screen_width // 2
            self.prev_gaze_y = self.screen_height // 2

        def _init_calibration(self):
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
            self.iris_center = (0.5, 0.5)
            self.iris_left = None
            self.iris_right = None
            self.iris_top = None
            self.iris_bottom = None
            self.calibration_iris_history = []

        def update_ball(self):
            self.ball_x += self.ball_speed_x
            self.ball_y += self.ball_speed_y
            if self.ball_x <= self.ball_radius or self.ball_x >= self.screen_width - self.ball_radius:
                self.ball_speed_x = -self.ball_speed_x
                self.ball_color = get_random_bright_color()
            if self.ball_y <= self.ball_radius or self.ball_y >= self.screen_height - self.ball_radius:
                self.ball_speed_y = -self.ball_speed_y
                self.ball_color = get_random_bright_color()
            self.ball_x = clamp(self.ball_x, self.ball_radius, self.screen_width - self.ball_radius)
            self.ball_y = clamp(self.ball_y, self.ball_radius, self.screen_height - self.ball_radius)

        def reset_ball(self):
            margin = 150
            self.ball_x = random.randint(self.ball_radius + margin, self.screen_width - self.ball_radius - margin)
            self.ball_y = random.randint(self.ball_radius + margin, self.screen_height - self.ball_radius - margin)
            self.ball_speed_x = random.choice(BALL_SPEED_OPTIONS)
            self.ball_speed_y = random.choice(BALL_SPEED_OPTIONS)
            self.ball_color = get_random_bright_color()

        def get_iris_position(self, landmarks):
            idx = LANDMARK_INDICES
            left_iris = landmarks[idx['left_iris_center']]
            left_eye_left = landmarks[idx['left_eye_left']]
            left_eye_right = landmarks[idx['left_eye_right']]
            left_eye_top = landmarks[idx['left_eye_top']]
            left_eye_bottom = landmarks[idx['left_eye_bottom']]
            right_iris = landmarks[idx['right_iris_center']]
            right_eye_left = landmarks[idx['right_eye_left']]
            right_eye_right = landmarks[idx['right_eye_right']]
            right_eye_top = landmarks[idx['right_eye_top']]
            right_eye_bottom = landmarks[idx['right_eye_bottom']]

            left_eye_width = left_eye_right.x - left_eye_left.x
            if left_eye_width > 0.005:
                left_iris_x = (left_iris.x - left_eye_left.x) / left_eye_width
            else:
                return None, None

            left_eye_height = left_eye_bottom.y - left_eye_top.y
            if left_eye_height > 0.002:
                left_iris_y = (left_iris.y - left_eye_top.y) / left_eye_height
            else:
                return None, None

            right_eye_width = right_eye_right.x - right_eye_left.x
            if right_eye_width > 0.005:
                right_iris_x = (right_iris.x - right_eye_left.x) / right_eye_width
            else:
                return None, None

            right_eye_height = right_eye_bottom.y - right_eye_top.y
            if right_eye_height > 0.002:
                right_iris_y = (right_iris.y - right_eye_top.y) / right_eye_height
            else:
                return None, None

            avg_iris_x = (left_iris_x + right_iris_x) / 2
            avg_iris_y = (left_iris_y + right_iris_y) / 2

            if not (0.1 < avg_iris_x < 0.9 and 0.1 < avg_iris_y < 0.9):
                return None, None

            return avg_iris_x, avg_iris_y

        def detect_face(self, frame):
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)
            self.face_detected = False
            self.eyes_valid = False

            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]
                self.face_detected = True
                landmarks = face_landmarks.landmark
                iris_x, iris_y = self.get_iris_position(landmarks)
                if iris_x is not None and iris_y is not None:
                    self.iris_x = iris_x
                    self.iris_y = iris_y
                    self.eyes_valid = True
            return frame

        def run_calibration(self, frame):
            if self.current_calibration_index >= len(self.calibration_order):
                self._finish_calibration()
                return frame

            current_point_name = self.calibration_order[self.current_calibration_index]
            current_point = self.calibration_points[current_point_name]
            screen_x, screen_y = current_point['screen']

            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (self.screen_width, self.screen_height), (20, 20, 20), -1)
            frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)

            pulse = int(20 * np.sin(time.time() * 4) + 60)
            cv2.circle(frame, (screen_x, screen_y), pulse, (0, 80, 200), -1)
            cv2.circle(frame, (screen_x, screen_y), 45, COLORS['red'], -1)
            cv2.circle(frame, (screen_x, screen_y), 45, COLORS['white'], 4)
            cv2.circle(frame, (screen_x, screen_y), 15, COLORS['white'], -1)

            cv2.putText(frame, "KALIBRASYON", (self.screen_width // 2 - 150, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, COLORS['cyan'], 3)
            cv2.putText(frame, "Sadece GOZLERINIZLE kirmizi noktaya bakin!",
                        (self.screen_width // 2 - 300, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, COLORS['white'], 2)

            point_names = {'center': 'MERKEZ', 'left': 'SOL', 'right': 'SAG', 'top': 'YUKARI', 'bottom': 'ASAGI'}
            progress_text = f"Nokta: {point_names[current_point_name]} ({self.current_calibration_index + 1}/5)"
            cv2.putText(frame, progress_text, (20, self.screen_height - 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, COLORS['cyan'], 2)

            if self.face_detected and self.eyes_valid:
                self.calibration_iris_history.append((self.iris_x, self.iris_y))
                if len(self.calibration_iris_history) > 15:
                    self.calibration_iris_history.pop(0)

                is_stable = True
                if len(self.calibration_iris_history) >= 8:
                    recent = self.calibration_iris_history[-8:]
                    x_values = [p[0] for p in recent]
                    y_values = [p[1] for p in recent]
                    x_range = max(x_values) - min(x_values)
                    y_range = max(y_values) - min(y_values)
                    if x_range > CALIBRATION_STABILITY_THRESHOLD or y_range > CALIBRATION_STABILITY_THRESHOLD:
                        is_stable = False

                if is_stable:
                    self.calibration_hold_time += 1 / 30.0
                    progress = min(self.calibration_hold_time / CALIBRATION_HOLD_TIME, 1.0)
                    bar_width = 400
                    bar_x = self.screen_width // 2 - bar_width // 2
                    bar_y = self.screen_height // 2 + 100
                    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + 35), COLORS['dark_gray'], -1)
                    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + int(bar_width * progress), bar_y + 35), COLORS['green'], -1)

                    if self.calibration_hold_time >= CALIBRATION_HOLD_TIME:
                        recent = self.calibration_iris_history[-8:] if len(self.calibration_iris_history) >= 8 else self.calibration_iris_history
                        avg_x = sum(p[0] for p in recent) / len(recent)
                        avg_y = sum(p[1] for p in recent) / len(recent)
                        self.calibration_points[current_point_name]['iris'] = (avg_x, avg_y)
                        self.current_calibration_index += 1
                        self.calibration_hold_time = 0
                        self.calibration_iris_history.clear()
                else:
                    self.calibration_hold_time = max(0, self.calibration_hold_time - 0.05)
                    cv2.putText(frame, "SABIT BAKIN!", (self.screen_width // 2 - 100, self.screen_height // 2 + 80),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS['orange'], 2)
            else:
                self.calibration_hold_time = max(0, self.calibration_hold_time - 0.1)
                status = "YUZ TESPIT EDILEMIYOR!" if not self.face_detected else "GOZ TESPIT EDILEMIYOR!"
                cv2.putText(frame, status, (self.screen_width // 2 - 200, self.screen_height // 2 + 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS['red'], 3)

            return frame

        def _finish_calibration(self):
            self.iris_center = self.calibration_points['center']['iris']
            self.iris_left = self.calibration_points['left']['iris']
            self.iris_right = self.calibration_points['right']['iris']
            self.iris_top = self.calibration_points['top']['iris']
            self.iris_bottom = self.calibration_points['bottom']['iris']
            self.is_calibrated = True
            print("Kalibrasyon tamamlandi!")

        def calculate_gaze(self):
            if not self.is_calibrated or not self.eyes_valid:
                return
            if not all([self.iris_center, self.iris_left, self.iris_right, self.iris_top, self.iris_bottom]):
                return

            # Get calibration ranges
            center_x = self.iris_center[0]
            center_y = self.iris_center[1]
            
            # Calculate X position relative to center
            # Note: When looking LEFT, iris moves RIGHT in the eye (towards nose)
            # When looking RIGHT, iris moves LEFT in the eye (towards ear)
            # So we need to INVERT the X direction
            
            diff_x = self.iris_x - center_x
            diff_y = self.iris_y - center_y
            
            # Get the range from calibration
            left_range = abs(center_x - self.iris_left[0]) if self.iris_left[0] != center_x else 0.05
            right_range = abs(self.iris_right[0] - center_x) if self.iris_right[0] != center_x else 0.05
            top_range = abs(center_y - self.iris_top[1]) if self.iris_top[1] != center_y else 0.05
            bottom_range = abs(self.iris_bottom[1] - center_y) if self.iris_bottom[1] != center_y else 0.05
            
            # Normalize based on direction
            if diff_x < 0:
                # Looking towards left side of calibration
                norm_x = diff_x / left_range if left_range > 0.001 else 0
            else:
                # Looking towards right side of calibration  
                norm_x = diff_x / right_range if right_range > 0.001 else 0
                
            if diff_y < 0:
                norm_y = diff_y / top_range if top_range > 0.001 else 0
            else:
                norm_y = diff_y / bottom_range if bottom_range > 0.001 else 0

            # Clamp values
            norm_x = clamp(norm_x, -1.5, 1.5)
            norm_y = clamp(norm_y, -1.5, 1.5)
            
            # Amplification factors - makes gaze tracking more responsive
            X_AMPLIFICATION = 1.8  # Horizontal sensitivity boost
            Y_AMPLIFICATION = 1.8  # Vertical sensitivity boost
            
            norm_x = norm_x * X_AMPLIFICATION
            norm_y = norm_y * Y_AMPLIFICATION
            
            # Re-clamp after amplification
            norm_x = clamp(norm_x, -1.5, 1.5)
            norm_y = clamp(norm_y, -1.5, 1.5)
            
            # Use consistent margins for both axes
            EDGE_MARGIN = 60  # Reduced margin = more range
            target_x = int(self.screen_width / 2 + norm_x * (self.screen_width / 2 - EDGE_MARGIN))
            target_y = int(self.screen_height / 2 + norm_y * (self.screen_height / 2 - EDGE_MARGIN))

            self.gaze_history_x.append(target_x)
            self.gaze_history_y.append(target_y)

            if len(self.gaze_history_x) >= 3:
                weights = np.linspace(0.5, 1.0, len(self.gaze_history_x))
                weights = weights / weights.sum()
                avg_x = np.average(list(self.gaze_history_x), weights=weights)
                avg_y = np.average(list(self.gaze_history_y), weights=weights)
            else:
                avg_x = target_x
                avg_y = target_y

            max_jump = 150
            delta_x = avg_x - self.prev_gaze_x
            delta_y = avg_y - self.prev_gaze_y
            if abs(delta_x) > max_jump:
                avg_x = self.prev_gaze_x + (max_jump if delta_x > 0 else -max_jump)
            if abs(delta_y) > max_jump:
                avg_y = self.prev_gaze_y + (max_jump if delta_y > 0 else -max_jump)

            self.gaze_x = int(self.prev_gaze_x + (avg_x - self.prev_gaze_x) * SMOOTHING_FACTOR)
            self.gaze_y = int(self.prev_gaze_y + (avg_y - self.prev_gaze_y) * SMOOTHING_FACTOR)

            self.gaze_x = clamp(self.gaze_x, 50, self.screen_width - 50)
            self.gaze_y = clamp(self.gaze_y, 50, self.screen_height - 50)
            self.prev_gaze_x = self.gaze_x
            self.prev_gaze_y = self.gaze_y

        def check_focus(self):
            if not self.eyes_valid or not self.is_calibrated:
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
                        
                        # Log successful focus event to CSV data
                        self.successful_focuses += 1
                        self.focus_durations.append(self.focus_duration)
                        self.focus_events.append({
                            'zaman': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'olay_turu': 'BASARILI_ODAK',
                            'odak_suresi': round(self.focus_duration, 3),
                            'goz_x': self.gaze_x,
                            'goz_y': self.gaze_y,
                            'top_x': self.ball_x,
                            'top_y': self.ball_y,
                            'mesafe': round(calculate_distance(self.gaze_x, self.gaze_y, self.ball_x, self.ball_y), 1),
                            'skor': self.score
                        })
                        
                        self._reset_focus()
                        self.reset_ball()
            else:
                if self.is_focused:
                    if self.focus_loss_start is None:
                        self.focus_loss_start = time.time()
                    else:
                        loss_duration = time.time() - self.focus_loss_start
                        if loss_duration > FOCUS_LOSS_TOLERANCE:
                            if self.accumulated_focus > 0.3:
                                self.warning_message = "Odak kaybedildi!"
                                self.warning_time = time.time()
                                
                                # Log failed focus event
                                self.total_focus_attempts += 1
                                self.focus_events.append({
                                    'zaman': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    'olay_turu': 'ODAK_KAYBI',
                                    'odak_suresi': round(self.accumulated_focus, 3),
                                    'goz_x': self.gaze_x,
                                    'goz_y': self.gaze_y,
                                    'top_x': self.ball_x,
                                    'top_y': self.ball_y,
                                    'mesafe': round(calculate_distance(self.gaze_x, self.gaze_y, self.ball_x, self.ball_y), 1),
                                    'skor': self.score
                                })
                            self._reset_focus()
                        elif self.accumulated_focus > 0:
                            self.accumulated_focus -= FOCUS_DECAY_RATE * (1/30)

        def _reset_focus(self):
            self.is_focused = False
            self.focus_start_time = None
            self.focus_duration = 0.0
            self.focus_loss_start = None
            self.accumulated_focus = 0.0

        def draw_ui(self, frame):
            # Bakış hedefi
            if self.eyes_valid and self.is_calibrated:
                x, y = int(self.gaze_x), int(self.gaze_y)
                cv2.circle(frame, (x, y), 35, COLORS['magenta'], 3)
                cv2.circle(frame, (x, y), 15, COLORS['magenta'], -1)
                cv2.line(frame, (x - 50, y), (x + 50, y), COLORS['magenta'], 2)
                cv2.line(frame, (x, y - 50), (x, y + 50), COLORS['magenta'], 2)

            # Top
            x, y = int(self.ball_x), int(self.ball_y)
            cv2.circle(frame, (x, y), self.ball_radius, self.ball_color, -1)
            cv2.circle(frame, (x, y), self.ball_radius, COLORS['white'], 3)
            if self.is_focused:
                cv2.circle(frame, (x, y), self.ball_radius + 20, COLORS['green'], 4)

            # Üst bar
            cv2.rectangle(frame, (0, 0), (self.screen_width, 80), (30, 30, 30), -1)
            cv2.putText(frame, f"SKOR: {self.score}", (20, 55),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, COLORS['green'], 3)

            if self.is_focused:
                progress = min(self.focus_duration / FOCUS_REQUIRED_TIME, 1.0)
                bar_x = self.screen_width // 2 - 150
                cv2.rectangle(frame, (bar_x, 28), (bar_x + 300, 53), (60, 60, 60), -1)
                cv2.rectangle(frame, (bar_x, 28), (bar_x + int(300 * progress), 53), COLORS['green'], -1)

            # Durum
            if self.eyes_valid:
                status_text, status_color = "GOZ OK", COLORS['green']
            elif self.face_detected:
                status_text, status_color = "GOZ YOK", COLORS['orange']
            else:
                status_text, status_color = "YUZ YOK", COLORS['red']
            cv2.putText(frame, status_text, (self.screen_width - 150, 55),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, status_color, 2)

            # Mesajlar
            if self.warning_message and time.time() - self.warning_time < 1.5:
                cv2.putText(frame, self.warning_message, (self.screen_width // 2 - 150, self.screen_height // 2),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, COLORS['red'], 3)
            if self.success_message and time.time() - self.success_time < 1.5:
                cv2.putText(frame, self.success_message, (self.screen_width // 2 - 100, self.screen_height // 2),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, COLORS['green'], 4)

            cv2.putText(frame, "R = Yeniden Kalibrasyon | Q = Cikis", (self.screen_width // 2 - 250, self.screen_height - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLORS['gray'], 2)
            return frame

        def reset_calibration(self):
            self.is_calibrated = False
            self.current_calibration_index = 0
            self.calibration_hold_time = 0
            self.gaze_history_x.clear()
            self.gaze_history_y.clear()
            for point in self.calibration_points.values():
                point['iris'] = None
            print("Yeniden kalibrasyon baslatiliyor...")

        def run(self):
            print("\n" + "=" * 60)
            print("GOZ ODAK TAKIP OYUNU - MediaPipe Edition")
            print("=" * 60)
            
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

            self.cap.release()
            cv2.destroyAllWindows()
            self.face_mesh.close()
            
            # Save results to CSV
            self._save_csv_results()
            
            print(f"\nOYUN BITTI! Toplam skor: {self.score}")
            return self.score
        
        def _save_csv_results(self):
            """Save eye tracking results to CSV file"""
            os.makedirs("results", exist_ok=True)
            csv_file = "results/performance_log_eye_tracking.csv"
            
            try:
                file_exists = os.path.isfile(csv_file)
                with open(csv_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    if not file_exists:
                        writer.writerow([
                            "Oyuncu", "Zaman", "OlayTuru", "OdakSuresi", 
                            "GozX", "GozY", "TopX", "TopY", "Mesafe", "Skor"
                        ])
                    
                    for event in self.focus_events:
                        writer.writerow([
                            player_name if player_name else "Bilinmiyor",
                            event['zaman'],
                            event['olay_turu'],
                            event['odak_suresi'],
                            event['goz_x'],
                            event['goz_y'],
                            event['top_x'],
                            event['top_y'],
                            event['mesafe'],
                            event['skor']
                        ])
                print(f"  - {csv_file} kaydedildi")
            except PermissionError:
                print(f"  UYARI: {csv_file} dosyasi acik oldugu icin kaydedilemedi!")
                print(f"  Lutfen Excel veya baska bir programda aciksa kapatin.")
            
            # Also save a summary
            summary_file = "results/eye_tracking_summary.csv"
            summary_exists = os.path.isfile(summary_file)
            
            total_time = time.time() - self.game_start_time
            avg_focus_duration = sum(self.focus_durations) / len(self.focus_durations) if self.focus_durations else 0
            total_attempts = self.successful_focuses + self.total_focus_attempts
            accuracy = (self.successful_focuses / total_attempts * 100) if total_attempts > 0 else 0
            
            try:
                with open(summary_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    if not summary_exists:
                        writer.writerow([
                            "Oyuncu", "Tarih", "ToplamSure", "BasariliOdak", 
                            "BasarisizOdak", "DogrulukOrani", "OrtOdakSuresi", "ToplamSkor"
                        ])
                    
                    writer.writerow([
                        player_name if player_name else "Bilinmiyor",
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        f"{total_time:.1f}",
                        self.successful_focuses,
                        self.total_focus_attempts,
                        f"{accuracy:.1f}",
                        f"{avg_focus_duration:.3f}",
                        self.score
                    ])
                print(f"  - {summary_file} kaydedildi")
            except PermissionError:
                print(f"  UYARI: {summary_file} dosyasi acik oldugu icin kaydedilemedi!")
                print(f"  Lutfen Excel veya baska bir programda aciksa kapatin.")
            
            print(f"\nSonuclar islendi.")

    trainer = EyeFocusTrainer()
    score = trainer.run()
    # Eye tracking returns score as success count, 10 total rounds assumed
    return score if score else 0, 10, 0.0


# =====================================================================
# ANA MENÜ
# =====================================================================

def show_next_stage_screen(current_stage, next_stage_name):
    """Sonraki aşamaya geçiş ekranı"""
    global player_name
    WIDTH, HEIGHT = 900, 650
    
    while True:
        screen = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        
        cv2.putText(screen, f"Tebrikler {player_name}!", (280, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)
        cv2.putText(screen, f"{current_stage} tamamlandi!", (300, 180),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        
        # Next Stage butonu
        cv2.rectangle(screen, (250, 280), (650, 380), (0, 100, 0), -1)
        cv2.rectangle(screen, (250, 280), (650, 380), (0, 255, 0), 3)
        cv2.putText(screen, f"NEXT: {next_stage_name}", (280, 340),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        
        cv2.putText(screen, "[ENTER] Devam | [ESC] Cikis", (300, 480),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (150, 150, 150), 2)
        
        cv2.imshow("Sonraki Asama", screen)
        key = cv2.waitKey(100) & 0xFF
        
        if key == 13:  # ENTER
            cv2.destroyAllWindows()
            return True
        elif key == 27:  # ESC
            cv2.destroyAllWindows()
            return False


def run_all_stages():
    """Tüm aşamaları sırayla çalıştır"""
    global all_stage_results, player_name
    all_stage_results = []
    
    # İsim al
    cv2.destroyAllWindows()
    get_player_name()
    if not player_name:
        return
    
    # Stage 1
    cv2.destroyAllWindows()
    stats = stage_1_mouse_test()
    if stats:
        correct, total, avg_rt = stats
        show_stage_stats("Stage 1: Mouse", correct, total, avg_rt, "Stage 2")
        if not show_next_stage_screen("Stage 1: Mouse", "Stage 2: Keyboard"):
            return
    
    # Stage 2
    cv2.destroyAllWindows()
    stats = stage_2_keyboard_test()
    if stats:
        correct, total, avg_rt = stats
        show_stage_stats("Stage 2: Keyboard", correct, total, avg_rt, "Stage 3")
        if MEDIAPIPE_AVAILABLE:
            if not show_next_stage_screen("Stage 2: Keyboard", "Stage 3: Eye"):
                return
    
    # Stage 3
    cv2.destroyAllWindows()
    if MEDIAPIPE_AVAILABLE:
        stats = stage_3_eye_tracking()
        if stats:
            correct, total, avg_rt = stats
            show_stage_stats("Stage 3: Eye", correct, total, avg_rt)
    
    # Final değerlendirme
    show_final_evaluation()



def show_main_menu():
    """Ana menü ekranı"""
    WIDTH, HEIGHT = 800, 600
    
    while True:
        screen = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        
        cv2.putText(screen, "GAMER REFLEX TRAINER", (150, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
        
        # Büyük BAŞLA butonu
        cv2.rectangle(screen, (250, 180), (550, 280), (0, 100, 0), -1)
        cv2.rectangle(screen, (250, 180), (550, 280), (0, 255, 0), 3)
        cv2.putText(screen, "BASLA", (330, 245),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        cv2.putText(screen, "(Tum asamalar)", (310, 300),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (150, 150, 150), 2)
        
        cv2.putText(screen, "[1] Sadece Mouse Testi", (200, 380),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2)
        cv2.putText(screen, "[2] Sadece Klavye Testi", (200, 420),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2)
        if MEDIAPIPE_AVAILABLE:
            cv2.putText(screen, "[3] Sadece Goz Testi", (200, 460),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2)
        
        cv2.putText(screen, "[ENTER] Basla | [ESC] Cikis", (240, 550),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 2)
        
        cv2.imshow("Gamer Reflex Trainer", screen)
        key = cv2.waitKey(100) & 0xFF
        
        if key == 13:  # ENTER - Tüm aşamalar
            cv2.destroyAllWindows()
            run_all_stages()
        elif key == ord('1'):
            cv2.destroyAllWindows()
            stage_1_mouse_test()
        elif key == ord('2'):
            cv2.destroyAllWindows()
            stage_2_keyboard_test()
        elif key == ord('3') and MEDIAPIPE_AVAILABLE:
            cv2.destroyAllWindows()
            stage_3_eye_tracking()
        elif key == 27:  # ESC
            break
    
    cv2.destroyAllWindows()


# =====================================================================
# PROGRAM BAŞLANGICI
# =====================================================================

if __name__ == "__main__":
    show_main_menu()

