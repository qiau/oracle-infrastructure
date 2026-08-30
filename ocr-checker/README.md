# OCR Checker

Checker gambar dari channel Telegram menggunakan **Tesseract OCR** untuk mendeteksi teks target.

Semua aplikasi berjalan di Docker. VPS host hanya membutuhkan Docker & Docker Compose.

## Struktur

```text
ocr-checker/
├── app/
│   ├── login.py
│   ├── get_channels.py
│   └── main.py
├── config/
│   └── channels.json
├── sessions/
│   └── telegram.session
├── results/
├── .env
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

- `app/` → source code
- `config/` → konfigurasi channel
- `sessions/` → Telegram session
- `results/` → hasil checker

## Environment

Buat `.env`:

```env
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=xxxxxxxxxxxxxxxxxxxxxxxx
```

Jangan commit `.env` atau `sessions/telegram.session`.

## Setup Pertama Kali

### 1. Login Telegram

```bash
docker compose run --rm ocr-checker python -m app.login
```

Session akan disimpan ke:

```text
sessions/telegram.session
```

### 2. Ambil daftar channel

Setelah login berhasil:

```bash
docker compose run --rm ocr-checker python -m app.get_channels
```

Daftar channel akan disimpan ke:

```text
config/channels.json
```

### 3. Jalankan Checker

```bash
docker compose up -d
```

## Session Telegram Invalid

Jika session sudah expired, revoked, atau logout:

```bash
docker compose run --rm ocr-checker python -m app.login
```

Setelah login berhasil:

```bash
docker compose up -d
```

Jika session valid, **tidak perlu login ulang**.

## Monitoring

Lihat status:

```bash
docker compose ps
```

Lihat log:

```bash
docker compose logs -f ocr-checker
```

Stop:

```bash
docker compose down
```

Restart:

```bash
docker compose restart ocr-checker
```

## OCR

Menggunakan:

- Tesseract OCR
- `pytesseract`
- OpenCV Headless

Gambar diproses langsung di memory dan tidak disimpan permanen ke disk.

## Keamanan

Tambahkan ke `.gitignore`:

```gitignore
.env

sessions/**
!sessions/.gitkeep

results/**
!results/.gitkeep

__pycache__/
*.pyc
```

**Jangan pernah membagikan `telegram.session` karena file tersebut dapat digunakan untuk mengakses session Telegram.**
