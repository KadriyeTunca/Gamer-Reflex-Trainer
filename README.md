# Gamer Reflex Trainer

## Proje Tanımı

**Gamer Reflex Trainer**, kullanıcıların refleks, tepki süresi ve doğruluk performanslarını ölçmek amacıyla geliştirilen, çok aşamalı ve etkileşim tabanlı bir performans analiz uygulamasıdır. Proje, akademik kullanım ve bitirme çalışması kapsamında tasarlanmış olup ölçülebilir, kayıt altına alınabilir ve analiz edilebilir veriler üretmeyi hedefler.

Uygulama; mouse, klavye ve göz takibi olmak üzere üç ana aşamadan oluşacak şekilde planlanmıştır. Mevcut sürümde **Mouse Refleks Testi (Stage 1)** tamamlanmış durumdadır.

---

## Projenin Amacı

* Kullanıcı reflekslerini objektif metriklerle ölçmek
* Tepki süresi, doğruluk ve hata oranı gibi performans göstergelerini kaydetmek
* Adaptif zorluk mekanizması ile gerçekçi test senaryoları oluşturmak
* Toplanan verileri akademik analizlere uygun formatta saklamak

---

## Proje Yapısı

Proje, modüler ve genişletilebilir bir mimari ile tasarlanmıştır.

```text
Gamer-Reflex-Trainer/
│
├── .git/                 # Git versiyon kontrol dizini
├── assets/               # Görsel ve yardımcı medya dosyaları
├── ml_data/              # İleri aşamalarda kullanılacak veri setleri
├── modules/              # Test aşamalarının modüler yapıları
├── results/              # Performans çıktı dosyaları (CSV)
│   └── performance_log.csv
│
├── main.py               # Uygulamanın ana giriş noktası
├── requirements.txt      # Gerekli Python kütüphaneleri
├── .gitignore
└── README.md
```

---

## Sistem Mimarisi

* **Tek giriş noktası:** `main.py`
* Her test aşaması ayrı bir fonksiyon olarak tanımlanmıştır
* Ortak bir CSV kayıt sistemi tüm aşamalar tarafından kullanılmaktadır

```text
main.py
 └── stage_1_mouse_test()
     ├── Başlangıç ekranı
     ├── Oyun döngüsü
     ├── Performans ölçümü
     └── CSV veri kaydı
```

Bu yapı sayesinde klavye ve göz takibi testleri mevcut kod yapısı bozulmadan sisteme eklenebilecektir.

---

## Aşamalar

### Stage 1 – Mouse Refleks Testi (Tamamlandı)

Bu aşamada kullanıcının mouse ile görsel hedeflere verdiği tepki süresi ölçülür.

**Özellikler:**

* Hareketli hedefler
* Rastgele konum, boyut ve yön
* Hedef renk kavramı (doğru / yanlış tıklama ayrımı)
* Yanlış tıklama durumunda hedef hızının artması (adaptif zorluk)

**Ölçülen Metrikler:**

* Tur sayısı
* Doğru ve yanlış tıklama sayısı
* Tepki süresi (saniye)
* Ortalama tepki süresi
* Hata oranı

---

### Stage 2 – Klavye Refleks Testi (Planlanıyor)

* W, A, S, D tuşları ile yön tabanlı refleks ölçümü
* Merkeze yaklaşan hedef mantığı
* Erken veya yanlış tuş basımında ceza mekanizması
* Mouse aşaması sonrası otomatik geçiş

---

### Stage 3 – Göz Takibi (Eye Tracking) Testi (Planlanıyor)

* OpenCV tabanlı yüz ve göz tespiti
* Bakış yönü ve odaklanma süresi analizi
* Mouse ve klavye verileri ile karşılaştırmalı refleks değerlendirmesi

---

## Veri Kaydı

Tüm test aşamaları tek bir CSV dosyasında kayıt altına alınır.

```text
results/performance_log.csv
```

**CSV Kolonları:**

```text
Asama, Tur, DogruMu, TepkiSuresi, HedefRenk, TiklananRenk, Zaman
```

Bu yapı sayesinde:

* Uzun vadeli performans takibi yapılabilir
* Veriler Python, Excel veya R ile analiz edilebilir
* Akademik çalışmalara doğrudan girdi sağlanabilir

---

## Kullanılan Teknolojiler

* Python 3
* OpenCV
* NumPy
* CSV tabanlı veri kaydı

---

## Kurulum ve Çalıştırma

### 1. Python 3.10 (64-bit) Kurulumu

> ⚠️ **ÖNEMLİ:** MediaPipe sadece **64-bit Python** ile çalışır! 32-bit sürüm çalışmaz.

1. [Python İndirme Sayfası](https://www.python.org/downloads/windows/)'na git
2. **"Windows installer (64-bit)"** seçeneğini indir
3. Kurulum sırasında:
   - ✅ **"Add Python to PATH"** kutusunu **mutlaka işaretle**
   - "Install Now" tıkla

---

### 2. Python'u Sistem Ortam Değişkenlerine (PATH) Ekleme

Eğer kurulum sırasında PATH'e eklemediysen, manuel olarak ekle:

1. **Windows + R** bas, `sysdm.cpl` yaz, Enter
2. **"Gelişmiş"** sekmesine git
3. **"Ortam Değişkenleri"** butonuna tıkla
4. **"Sistem Değişkenleri"** bölümünde **"Path"** satırını seç, **"Düzenle"** tıkla
5. **"Yeni"** butonuna tıkla ve şu yolları ekle:

```
C:\Users\kadri\AppData\Local\Programs\Python\Python310\
C:\Users\kadri\AppData\Local\Programs\Python\Python310\Scripts\
```

6. Tüm pencereleri **Tamam** ile kapat
7. **PowerShell'i kapat ve yeniden aç** (değişikliklerin aktif olması için)

**Test etmek için:**
```powershell
python --version
```
Çıktı: `Python 3.10.x` gibi olmalı.

---

### 3. MediaPipe ve Gerekli Kütüphaneleri Kurma

> ⚠️ **ÖNEMLİ:** MediaPipe'ın **0.10.9** sürümünü kurmalısın! Yeni sürümler (0.10.31+) API değişikliği nedeniyle çalışmaz.

PowerShell'de şu komutu çalıştır:

```powershell
python -m pip install mediapipe==0.10.9 opencv-python numpy
```

Eğer `python` komutu çalışmazsa, tam yol ile dene:

```powershell
& "C:\Users\kadri\AppData\Local\Programs\Python\Python310\python.exe" -m pip install mediapipe==0.10.9 opencv-python numpy
```

---

### 4. Projeyi Klonla veya İndir

```bash
git clone https://github.com/KadriyeTunca/Gamer-Reflex-Trainer.git
cd Gamer-Reflex-Trainer
```

---

### 5. Göz Takibi Uygulamasını Çalıştır

```powershell
python eye_focus_trainer.py
```

Veya tam yol ile:

```powershell
& "C:\Users\kadri\AppData\Local\Programs\Python\Python310\python.exe" eye_focus_trainer.py
```

---

### 6. Kullanım

- **Kalibrasyon:** Uygulama açıldığında ekranda beliren kırmızı noktalara **gözlerinizle** bakın (başınızı hareket ettirmeyin)
- **Oyun:** Mor hedefi gözlerinizle topu takip ederek üzerine getirin ve 1 saniye tutun
- **R tuşu:** Yeniden kalibrasyon
- **Q tuşu:** Çıkış

---

### Sorun Giderme

| Hata | Çözüm |
|------|-------|
| `pip is not recognized` | PATH'e Python ekle (yukarıdaki 2. adım) |
| `No matching distribution found for mediapipe` | 64-bit Python kurmalısın |
| `module 'mediapipe' has no attribute 'solutions'` | `mediapipe==0.10.9` sürümünü kur |
| Mor hedef hareket etmiyor | Kalibrasyonu yeniden yap (R tuşu) |

---

## Neden Sanal Ortam ve Clone Kullanılır?

* Projenin bağımlılıkları sistemdeki diğer Python projeleriyle çakışmaz
* Aynı proje farklı bilgisayarlarda **aynı şekilde çalışır**
* Akademik ve profesyonel projelerde standart bir yaklaşımdır
* `requirements.txt` sayesinde tüm kütüphaneler tek komutla kurulur

---

## Gelecek Çalışmalar

* Klavye refleks testinin entegrasyonu
* Göz takibi modülünün eklenmesi
* Performans verileri için grafiksel raporlama
* Kullanıcı bazlı kişiselleştirilmiş analiz

---

## Akademik Kullanım

Bu proje, insan-bilgisayar etkileşimi, oyun analitiği ve bilişsel performans ölçümü alanlarında örnek bir uygulama olarak tasarlanmıştır.

---

## Lisans

Bu proje eğitim ve akademik amaçlarla geliştirilmiştir.
