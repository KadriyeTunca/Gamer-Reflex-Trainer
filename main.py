import cv2
import numpy as np
import time
import random
import csv
import os
from datetime import datetime


def stage_1_mouse_test():
    
    # EKRAN BOYUTU
    WIDTH, HEIGHT = 1000, 800

    # RENKLER (BGR)
    COLORS = {
        "pembe": (180, 105, 240),
        "sari": (0, 255, 255),
        "mavi": (255, 0, 0),
        "yesil": (106, 187, 106)
    }

    
    # OYUN DURUMU BAŞLANGIÇTA FALSE VE BOŞ TANIMLIYORUZ ÇÜNKÜ HENÜZ BAŞLATILMADI
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

    
    # CSV (TEK DOSYADA SIRALI VERİ TOPLAMA KODU)
    os.makedirs("results", exist_ok=True) # "exist_ok=True" ifadesi dosya zaten varsa hata vermemesi için
    csv_path = "results/performance_log.csv"

# "w" Csv dosyası için yeni dosya oluşturur
# newline boş olması satır atlama hatasını önler csv'ye karışmaz
# With dosya kısmında hata olsa bile bu bloğu çalıştır geç der 

    if not os.path.exists(csv_path): # dosya var mı yok mu kontrol yoksa alttaki kodlar çalışır
        with open(csv_path, "w", newline="", encoding="utf-8") as f: 
            writer = csv.writer(f)
            writer.writerow([
                "Asama",
                "Tur",
                "DogruMu",
                "TepkiSuresi",
                "HedefRenk",
                "TiklananRenk",
                "Zaman"
            ])

    
    # EKRANLAR
    def draw_start_screen():
        screen = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        cv2.putText(screen, "GAMER REFLEX TRAINER", (210, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3) # Başlık metni 1.5 ölçekli ve yeşil renkte 3 kalınlıkta
        cv2.putText(screen, "BASLA", (430, 400),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        cv2.rectangle(screen, (380, 330), (620, 450), (255, 0, 0), 3) # Başla butonunun etrafına dikdörtgen çiz sol üst köşe (380,330) sağ alt köşe (620,450)
        return screen  # Başla ekranını döndür

    def draw_end_screen():
        screen = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        avg_reaction = np.mean(reaction_times) if reaction_times else 0  # Ortalama tepki süresi hesaplama
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

 
    # OYUN MANTIĞI VE HEDEF OLUŞTURMA
    def generate_round():
        nonlocal targets, target_color_name, start_time, total_rounds #nonlocal ile dış değişkenlere erişim sağlanır 
        total_rounds += 1                                          # ilk tanımlandıkları yerden sonraki bloklarda kullanılabilirler
        target_color_name = random.choice(list(COLORS.keys()))
        distractors = [c for c in COLORS.keys() if c != target_color_name] # hedef renk dışındaki renkleri alır c için
        random.shuffle(distractors) # dikkat dağıtıcı renklerin sırasını karıştırır
        targets = []

        def create_target(color_name):
            x = random.randint(100, WIDTH - 100) # hedefin x koordinatını rastgele belirler
            y = random.randint(150, HEIGHT - 100)
            r = random.randint(30, 60) # hedefin yarıçapını rastgele belirler 
            dx = random.choice([-1, 1]) * base_speed * speed_multiplier # hedefin x eksenindeki hızını belirler<
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

    
    # MOUSE TIKLAMA İŞLEMLERİ
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

    
    # ANA DÖNGÜ

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
    return


# =====================
# PROGRAM BAŞLANGICI
# =====================
if __name__ == "__main__":
    stage_1_mouse_test()
