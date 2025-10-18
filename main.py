import cv2
import numpy as np

# Ekran boyutu tanımlıyoruz
WIDTH, HEIGHT = 1000, 800
# Renk tanımları (BGR) 
COLORS = { 
          "pembe": (180, 105, 240), 
          "sari": (0, 255, 255), 
          "mavi": (255, 0, 0), 
          "yesil": (106, 187, 106) 
          }

def draw_start_screen():
    screen = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    cv2.putText(screen, 'GAMER REFLEX TRAİNER', (200,150),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
    cv2.putText(screen, 'BASLA', (430, 400),
                  cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255),3)
    cv2.rectangle(screen, (380, 350), (620, 450), (255, 0, 0), 3)
    return screen
    
    
def draw_end_screen():
    screen = np.zeros((HEIGHT, WIDTH,3), dtype=np.uint8)
    