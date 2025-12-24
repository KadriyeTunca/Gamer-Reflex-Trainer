@echo off
chcp 65001 >nul
echo.
echo ============================================
echo   Gamer Reflex Trainer - Kurulum Script'i
echo ============================================
echo.

:: Python kontrolü
echo [1/4] Python kontrol ediliyor...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo HATA: Python bulunamadi!
    echo.
    echo Python 3.10 64-bit indirin: https://www.python.org/downloads/
    echo Kurulum sirasinda "Add Python to PATH" kutusunu isaretleyin!
    echo.
    pause
    exit /b 1
)

:: 64-bit kontrolü
echo [2/4] Python 64-bit mi kontrol ediliyor...
python -c "import struct; exit(0 if struct.calcsize('P')*8==64 else 1)"
if errorlevel 1 (
    echo.
    echo HATA: 32-bit Python tespit edildi!
    echo MediaPipe sadece 64-bit Python ile calisir.
    echo.
    echo Lutfen 64-bit Python indirin: https://www.python.org/downloads/
    echo "Windows installer (64-bit)" secenegini indirin.
    echo.
    pause
    exit /b 1
)
echo    Python 64-bit - OK

:: MediaPipe kurulumu
echo [3/4] MediaPipe 0.10.9 kuruluyor...
python -m pip install mediapipe==0.10.9 opencv-python numpy --quiet
if errorlevel 1 (
    echo.
    echo HATA: Kutuphane kurulumu basarisiz!
    echo Lutfen internet baglantinizi kontrol edin.
    echo.
    pause
    exit /b 1
)
echo    MediaPipe 0.10.9 - OK

:: Başarılı
echo [4/4] Kurulum tamamlandi!
echo.
echo ============================================
echo   KURULUM BASARILI!
echo ============================================
echo.
echo Uygulamayi calistirmak icin:
echo   python eye_focus_trainer.py
echo.
echo Veya cift tikla: run.bat
echo.
pause
