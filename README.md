# Gamer Reflex Trainer

## Proje Tanımı

**Gamer Reflex Trainer**, kullanıcıların refleks, tepki süresi ve doğruluk performanslarını ölçmek amacıyla geliştirilmiş, çok aşamalı ve etkileşim tabanlı bir performans analiz uygulamasıdır. Proje, bir bitirme çalışması kapsamında tasarlanmış olup, ölçülebilir ve akademik olarak analiz edilebilir veriler üretmeyi hedeflemektedir.

Uygulama; mouse, klavye ve göz takibi (eye tracking) olmak üzere üç ana aşamadan oluşacak şekilde planlanmıştır. Mevcut sürümde mouse tabanlı refleks testi tamamlanmış ve sistem, sonraki aşamalara uygun modüler bir mimari ile yapılandırılmıştır.

---

## Projenin Amacı

Bu çalışmanın temel amaçları şunlardır:

* Kullanıcı reflekslerini nesnel ve ölçülebilir metriklerle değerlendirmek
* Tepki süresi ve hata oranı gibi performans göstergelerini kayıt altına almak
* Adaptif zorluk mekanizması ile gerçekçi bir test ortamı oluşturmak
* Toplanan verileri akademik analiz ve istatistiksel değerlendirme için uygun formatta saklamak

---

## Sistem Mimarisi

Proje, modüler ve genişletilebilir bir yazılım mimarisi ile geliştirilmiştir.

* Uygulamanın tek giriş noktası `main.py` dosyasıdır
* Her test aşaması ayrı bir fonksiyon olarak tanımlanmıştır
* Ortak bir CSV veri kayıt sistemi tüm aşamalar tarafından paylaşılmaktadır

```text
main.py
 └── stage_1_mouse_test()
     ├── Başlangıç ekranı
     ├── Oyun döngüsü
     ├── Performans ölçümü
     └── CSV veri kaydı
```

Bu yapı sayesinde klavye ve göz takibi testleri, mevcut kod yapısı bozulmadan sisteme entegre edilebilecektir.

---

## Proje Klasör Yapısı

```text
Gamer-Reflex-Trainer/
│
├── .git/                    # Git sürüm kontrol dizini
├── .gitignore               # Git tarafından yok sayılan dosyalar
│
├── assets/                  # Görsel ve yardımcı medya dosyaları
├── ml_data/                 # İleride kullanılacak makine öğrenmesi verileri
├── modules/                 # Test aşamalarına ait modüller
│
├── results/
│   └── performance_log.csv  # Tüm test sonuçları (tek CSV dosyası)
│
├── main.py                  # Ana uygulama dosyası
├── requirements.txt         # Gerekli Python kütüphaneleri
└── README.md                # Proje dokümantasyonu
```

---

## Aşamalar

### Stage 1 – Mouse Refleks Testi (Tamamlandı)

Bu aşamada kullanıcının mouse kullanarak görsel hedeflere verdiği tepkiler ölçülmektedir.

**Özellikler:**

* Hareketli hedefler
* Rastgele konum, boyut ve yön
* Hedef renk kavramı ile doğru / yanlış tıklama ayrımı
* Yanlış tıklamalarda hedef hızının artması (adaptif zorluk)

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
* Mouse testinden sonra otomatik geçiş

---

### Stage 3 – Göz Takibi (Eye Tracking) Testi (Planlanıyor)

* OpenCV tabanlı yüz ve göz tespiti
* Bakış yönü ve odaklanma süresi analizi
* Mouse ve klavye verileri ile karşılaştırmalı refleks değerlendirmesi

---

## Veri Kaydı ve CSV Yapısı

Tüm test aşamalarına ait veriler tek bir CSV dosyasında saklanmaktadır.

**Dosya yolu:**

```text
results/performance_log.csv
```

**CSV Kolonları:**

```text
Asama, Tur, DogruMu, TepkiSuresi, HedefRenk, TiklananRenk, Zaman
```

Bu yapı sayesinde uzun vadeli performans takibi ve akademik analizler kolaylıkla gerçekleştirilebilir.

---

## Kullanılan Teknolojiler

* Python 3
* OpenCV
* NumPy
* CSV tabanlı veri kaydı

---

## Kurulum ve Çalıştırma

Gerekli kütüphaneleri yüklemek için:

```bash
pip install -r requirements.txt
```

Uygulamayı çalıştırmak için:

```bash
python main.py
```

---

## Gelecek Çalışmalar

* Klavye refleks testinin sisteme eklenmesi
* Göz takibi modülünün entegrasyonu
* Performans verileri için grafiksel raporlama
* Kullanıcı profiline göre kişiselleştirilmiş zorluk ayarları

---

## Akademik Kullanım

Bu proje, insan–bilgisayar etkileşimi, oyun analitiği ve bilişsel performans ölçümü alanlarında örnek bir uygulama olarak kullanılabilecek şekilde tasarlanmıştır.

---

## Lisans

Bu proje eğitim ve akademik amaçlarla geliştirilmiştir.
