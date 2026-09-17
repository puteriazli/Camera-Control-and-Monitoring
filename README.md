# Camera Control & Monitoring

Aplikasi sederhana berbasis **Python dan OpenCV** untuk mengakses, menampilkan, dan mengontrol webcam/kamera secara real-time.

Project ini dibuat untuk memenuhi tugas **IoT & Embedded Systems**, dengan fokus pada akses kamera, live preview, pengaturan parameter kamera, single capture, burst capture, dan pergantian resolusi.

## Fitur

- Live preview kamera secara real-time menggunakan `cv2.imshow()`.
- Pemilihan backend kamera secara otomatis berdasarkan sistem operasi.
- Pengaturan resolusi kamera.
- Target frame rate hingga 30 FPS.
- Pengaturan **exposure** sebagai pendekatan terhadap shutter speed.
- Pengaturan **gain** sebagai pendekatan terhadap ISO.
- Trackbar untuk mengubah exposure dan gain secara live.
- Single capture menggunakan tombol `SPACE` atau `C`.
- Burst capture menggunakan tombol `B` selama tombol ditahan.
- Pergantian preset resolusi menggunakan tombol `R`.
- Penyimpanan gambar hasil capture dalam format `.jpg`.
- Overlay informasi resolusi, FPS, exposure, gain/ISO, dan kontrol keyboard.
- Pembersihan resource kamera dan window secara otomatis saat program berhenti.

## Teknologi yang Digunakan

| Komponen | Teknologi |
|---|---|
| Bahasa pemrograman | Python |
| Computer Vision | OpenCV |
| Package Python | `opencv-python` |
| Environment | Anaconda / Anaconda Prompt |
| Interface | OpenCV GUI (`cv2.imshow`, trackbar) |
| Format gambar | JPEG |
| Camera backend | OpenCV backend / DirectShow pada Windows / V4L2 pada Linux |
| Sistem operasi pengerjaan | Windows |
| Editor | Visual Studio Code |
| Hardware kamera | Webcam laptop / webcam yang terhubung ke komputer |

## Spesifikasi Komputer

Project dikerjakan menggunakan komputer/laptop dengan spesifikasi berikut:

| Spesifikasi | Detail |
|---|---|
| Perangkat | Lenovo IdeaPad Slim 14 |
| Sistem Operasi | Windows |
| Processor | Intel Core i5 Generasi ke-11 |
| RAM | 16 GB |
| GPU | Integrated graphics / tidak menggunakan GPU dedicated untuk project ini |
| Python | Versi terbaru yang digunakan pada environment pengerjaan |
| Environment Manager | Anaconda |
| Terminal | Anaconda Prompt |
| Code Editor | Visual Studio Code |

> **Catatan:** Project ini tidak membutuhkan GPU dedicated karena proses utama berupa akses webcam, live preview, pengaturan parameter kamera, dan penyimpanan frame menggunakan OpenCV.

## Struktur Project

Struktur sederhana yang digunakan:

```text
Camera-Control-and-Monitoring/
│
├── camera_control.py
├── captures/
│   └── *.jpg
└── README.md
```

Folder `captures/` dibuat otomatis oleh program apabila belum tersedia.

Ketika menggunakan burst capture, program membuat folder sesi secara otomatis:

```text
captures/
├── capture_20260917_174500_123.jpg
├── capture_20260917_174501_456.jpg
└── burst_20260917_174600/
    ├── burst_20260917_174600_001.jpg
    ├── burst_20260917_174600_002.jpg
    └── ...
```

Nama file aktual dibuat berdasarkan timestamp saat gambar disimpan.

## Instalasi

### 1. Pastikan Anaconda sudah terpasang

Project dapat dijalankan melalui **Anaconda Prompt**.

Cek versi Python:

```bash
python --version
```

### 2. Buat environment

Contoh:

```bash
conda create -n camera_control python
```

Aktifkan environment:

```bash
conda activate camera_control
```

### 3. Install OpenCV

```bash
pip install opencv-python
```

Verifikasi instalasi:

```bash
python -c "import cv2; print(cv2.__version__)"
```

Jika nomor versi OpenCV berhasil ditampilkan, library sudah terpasang.

## Menjalankan Program

Buka **Anaconda Prompt**, masuk ke folder project:

```bash
cd path/to/Camera-Control-and-Monitoring
```

Aktifkan environment:

```bash
conda activate camera_control
```

Jalankan program:

```bash
python camera_control.py
```

Program kemudian akan membuka:

1. Window **Live Preview - Camera Control**
2. Window **Kontrol Kamera (Exposure / Gain)**

## Kontrol Keyboard

| Tombol | Fungsi |
|---|---|
| `SPACE` | Mengambil satu foto |
| `C` | Mengambil satu foto |
| `B` (tahan) | Burst capture selama tombol ditahan |
| `R` | Mengganti preset resolusi |
| `Q` | Keluar dari program |
| `ESC` | Keluar dari program |

Preset resolusi yang tersedia:

```text
640 × 480
1280 × 720
1920 × 1080
```

Resolusi awal yang digunakan:

```text
1280 × 720
```

Target FPS:

```text
30 FPS
```

## Konfigurasi Kamera

Konfigurasi utama berada pada dictionary `CONFIG` di dalam `camera_control.py`.

Contoh:

```python
CONFIG = {
    "camera_index": 0,
    "backend": "auto",
    "resolution": (1280, 720),
    "fps_target": 30,
    "exposure": -6,
    "gain_iso": 100,
    "manual_exposure_mode": True,
    "output_dir": "captures",
    "jpeg_quality": 95,
}
```

### Camera Index

```python
"camera_index": 0
```

Nilai `0` digunakan untuk webcam utama/default.

Jika terdapat beberapa kamera dan kamera utama tidak terbuka, nilai dapat dicoba menjadi:

```python
"camera_index": 1
```

atau:

```python
"camera_index": 2
```

### Backend Kamera

Program menggunakan:

```python
"backend": "auto"
```

Dengan konfigurasi tersebut, program memilih backend berdasarkan sistem operasi.

Pada Windows:

```text
cv2.CAP_DSHOW
```

Pada Linux:

```text
cv2.CAP_V4L2
```

Jika backend yang dipilih gagal membuka kamera, program melakukan fallback ke backend default OpenCV.

## Exposure dan Gain / ISO

Webcam UVC pada umumnya tidak memiliki parameter **ISO** seperti kamera DSLR atau mirrorless.

Dalam project ini:

- `CAP_PROP_EXPOSURE` digunakan sebagai pendekatan terhadap shutter speed/exposure.
- `CAP_PROP_GAIN` digunakan sebagai proxy terhadap ISO atau sensor gain.

Nilai tersebut bergantung pada driver dan hardware kamera. Karena itu, perubahan nilai pada program tidak selalu menghasilkan perubahan fisik yang sama pada setiap webcam.

Project menggunakan:

```python
"exposure": -6
"gain_iso": 100
```

Nilai tersebut merupakan konfigurasi awal dan dapat disesuaikan dengan kemampuan kamera.

## Burst Capture

Burst capture bekerja dengan mendeteksi key-repeat dari sistem operasi karena OpenCV tidak menyediakan event `key up` secara langsung.

Alurnya:

```text
Tekan dan tahan B
       ↓
Burst capture aktif
       ↓
Frame disimpan secara berulang
       ↓
Tombol B dilepas
       ↓
Key-repeat berhenti
       ↓
Burst capture dihentikan
```

Setiap sesi burst disimpan dalam folder terpisah di dalam `captures/`.

## Output

Hasil single capture disimpan pada:

```text
captures/
```

Hasil burst capture disimpan pada:

```text
captures/burst_<timestamp>/
```

Gambar disimpan dalam format JPEG dengan kualitas:

```text
95
```

Timestamp digunakan pada nama file agar file hasil capture tidak saling menimpa.

## Penanganan Error

Program memiliki beberapa mekanisme dasar untuk menangani masalah kamera:

- Mencoba backend kamera sesuai sistem operasi.
- Melakukan fallback ke backend default OpenCV jika backend utama gagal.
- Memeriksa apakah kamera berhasil dibuka.
- Memberikan pesan jika frame gagal dibaca.
- Menyarankan pemeriksaan `camera_index` jika kamera tidak ditemukan.
- Me-release kamera menggunakan `cap.release()`.
- Menutup seluruh window OpenCV menggunakan `cv2.destroyAllWindows()`.

Pada Windows, jika kamera tidak dapat dibuka, pastikan kamera tidak sedang digunakan aplikasi lain seperti:

```text
Zoom
Microsoft Teams
OBS
Camera
```

Selain itu, periksa izin kamera pada:

```text
Settings → Privacy & security → Camera
```

## Keterbatasan

Project memiliki beberapa keterbatasan yang bergantung pada hardware dan driver kamera:

1. Tidak semua webcam mendukung pengaturan exposure dan gain secara manual.
2. Parameter yang disebut sebagai ISO merupakan pendekatan menggunakan sensor gain.
3. Nilai exposure dan gain dapat memiliki rentang yang berbeda pada setiap kamera.
4. Burst capture bergantung pada mekanisme key-repeat dari sistem operasi.
5. FPS dan resolusi aktual dapat berbeda dari nilai target apabila kamera atau driver tidak mendukung konfigurasi tersebut.
6. Project menggunakan GUI OpenCV sehingga membutuhkan lingkungan desktop yang mendukung window display.

## Pengujian

Pengujian dilakukan pada komputer dengan:

- Windows
- Intel Core i5 Generasi ke-11
- RAM 16 GB
- Python
- Anaconda / Anaconda Prompt
- OpenCV
- Webcam

Skenario pengujian meliputi:

- Membuka webcam.
- Menampilkan live preview.
- Mengubah exposure melalui trackbar.
- Mengubah gain/ISO melalui trackbar.
- Mengambil single capture.
- Menjalankan burst capture.
- Mengganti resolusi.
- Menghentikan aplikasi menggunakan `Q` atau `ESC`.
- Menutup window kamera secara langsung.

## Referensi Implementasi

Program menggunakan API OpenCV, terutama:

```python
cv2.VideoCapture()
cv2.imshow()
cv2.waitKey()
cv2.createTrackbar()
cv2.setTrackbarMin()
cv2.setTrackbarMax()
cv2.imwrite()
cv2.CAP_PROP_FRAME_WIDTH
cv2.CAP_PROP_FRAME_HEIGHT
cv2.CAP_PROP_FPS
cv2.CAP_PROP_EXPOSURE
cv2.CAP_PROP_GAIN
```

## Author

**Puteri Azli**

Project: **Camera Control & Monitoring**

---

**Catatan:** Detail spesifikasi hardware dan software pada README ini disesuaikan dengan lingkungan pengerjaan project. Versi Python dan versi OpenCV sebaiknya dicantumkan dengan nomor versi aktual apabila ingin membuat dokumentasi yang sepenuhnya reproducible.
