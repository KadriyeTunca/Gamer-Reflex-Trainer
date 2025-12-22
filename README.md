# Gamer Reflex Trainer

## Proje Tanımı

**Gamer Reflex Trainer**, oyuncuların ve bilgisayar kullanıcılarının refleks, tepki süresi ve doğruluk performanslarını ölçmek amacıyla geliştirilen, çok aşamalı bir bilgisayar görüşü ve etkileşim tabanlı test uygulamasıdır. Proje, bitirme çalışması kapsamında tasarlanmış olup, ölçülebilir ve analiz edilebilir performans verileri üretmeyi hedefler.

Uygulama; mouse, klavye ve göz takibi olmak üzere üç ana aşamadan oluşacak şekilde planlanmıştır. Mevcut sürümde mouse tabanlı refleks testi tamamlanmıştır.

---

## Projenin Amacı

* Kullanıcı reflekslerini objektif metriklerle ölçmek
* Tepki süresi ve hata oranı gibi performans göstergelerini kayıt altına almak
* Adaptif zorluk mekanizması ile gerçekçi bir test ortamı oluşturmak
* Toplanan verileri akademik analiz ve istatistiksel değerlendirme için uygun formatta saklamak

---

## Sistem Mimarisi

Proje, modüler ve genişletilebilir bir yapı ile tasarlanmıştır.

* **Tek giriş noktası:** `main.py`
* Her test aşaması ayrı bir fonksiyon olarak tanımlanmıştır
* Ortak veri kaydı sistemi (CSV) tüm aşamalar tarafından paylaşılmaktadır

```text
main.py
 └── stage_1_mouse_test()
     ├── Başlangıç ekranı
     ├── Oyun döngüsü
     ├── Performans ölçümü
     └── CSV veri kaydı
```

Bu yapı sayesinde ilerleyen aşamalarda klavye ve göz takibi testleri mevcut kodu bozmadan sisteme eklenebilecektir.

---

## Aşamalar

### Stage 1 – Mouse Refleks Testi (Tamamlandı)

Bu aşamada kullanıcının mouse ile görsel hedeflere tepki süresi ölçülür.

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
* Mouse ve klavye verileri ile karşılaştırmalı refleks analizi

---

## Veri Kaydı ve CSV Yapısı

Tüm test aşamaları tek bir CSV dosyası üzerinde kayıt tutar.

**Dosya yolu:**

```text
results/performance_log.csv
```

**CSV Kolonları:**

```text
Asama, Tur, DogruMu, TepkiSuresi, HedefRenk, TiklananRenk, Zaman
```

Bu yapı sayesinde:

* Uzun vadeli performans takibi yapılabilir
* Veriler Excel, Python, R gibi araçlarla analiz edilebilir
* Akademik çalışmalara doğrudan girdi sağlanabilir

---

## Kullanılan Teknolojiler

* Python 3
* OpenCV
* NumPy
* CSV / Dosya tabanlı veri kaydı

---

## Kurulum ve Çalıştırma

Gerekli kütüphaneleri yükleyin:

```bash
pip install opencv-python numpy
```

Projeyi çalıştırmak için:

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

Bu proje, insan-bilgisayar etkileşimi, oyun analitiği ve bilişsel performans ölçümü alanlarında örnek bir uygulama olarak kullanılabilecek şekilde tasarlanmıştır.

---

## Lisans

Bu proje eğitim ve akademik amaçlı geliştirilmiştir.
