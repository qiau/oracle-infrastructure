# OCR Checker

Sistem untuk memeriksa gambar dari channel Telegram dan mendeteksi teks tertentu menggunakan **Tesseract OCR**.

Aplikasi berjalan sepenuhnya di Docker sehingga VPS host tidak perlu menginstall Python, virtual environment, Tesseract, atau dependency OCR secara langsung.

## Struktur Project

```text
ocr-checker/
├── app/
│   ├── login.py
│   └── ...
│
├── config/
│   └── channels.json
│
├── sessions/
│   └── telegram.session
│
├── results/
│   └── ...
│
├── .env
├── .gitignore
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

### Folder

| Folder      | Fungsi                                  |
| ----------- | --------------------------------------- |
| `app/`      | Source code aplikasi                    |
| `config/`   | Konfigurasi channel yang akan diperiksa |
| `sessions/` | Session Telegram                        |
| `results/`  | Hasil proses checker                    |

> File session Telegram bersifat sensitif. Jangan commit ke Git.

---

## Konfigurasi Environment

Buat file `.env` di root project:

```env
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=xxxxxxxxxxxxxxxxxxxxxxxx
```

`API_ID` dan `API_HASH` digunakan oleh Telethon untuk terhubung ke Telegram.

Jangan masukkan `.env` ke repository.

---

## Instalasi

Pastikan VPS sudah memiliki:

- Docker
- Docker Compose

Tidak perlu membuat Python virtual environment di host.

Build image:

```bash
docker compose build
```

Build hanya diperlukan ketika pertama kali membuat image atau ketika `Dockerfile` / `requirements.txt` berubah.

---

# Telegram Session

Aplikasi menggunakan session Telegram yang disimpan di:

```text
sessions/telegram.session
```

Session ini memungkinkan aplikasi terhubung kembali ke Telegram tanpa melakukan login OTP setiap kali container dijalankan.

## Membuat Session

Jika session belum tersedia, jalankan:

```bash
docker compose run --rm checker python -m app.login
```

Telethon kemudian akan meminta:

1. Nomor Telegram
2. OTP Telegram
3. Password 2FA jika akun menggunakan 2FA

Setelah login berhasil, session akan tersimpan di:

```text
sessions/telegram.session
```

Kemudian jalankan worker:

```bash
docker compose up -d
```

---

# ⚠️ Jika Session Telegram Invalid

**Jangan langsung menjalankan `app.login` setiap kali aplikasi dijalankan.**

Jika session masih valid:

```bash
docker compose up -d
```

langsung saja.

Jika session **expired, revoked, logout, atau tidak valid**, jalankan:

```bash
docker compose run --rm checker python -m app.login
```

Setelah login berhasil dan `sessions/telegram.session` sudah diperbarui:

```bash
docker compose up -d
```

### Alur sederhananya

```text
Session valid
    ↓
docker compose up -d
    ↓
Checker berjalan


Session invalid / belum ada
    ↓
docker compose run --rm checker python -m app.login
    ↓
Login Telegram
    ↓
sessions/telegram.session dibuat/diperbarui
    ↓
docker compose up -d
    ↓
Checker berjalan
```

---

# Menjalankan Aplikasi

Setelah session Telegram valid:

```bash
docker compose up -d
```

Melihat status container:

```bash
docker compose ps
```

Melihat log:

```bash
docker compose logs -f checker
```

Menghentikan aplikasi:

```bash
docker compose down
```

Restart:

```bash
docker compose restart checker
```

---

# Session Tidak Disimpan di Docker Image

Session Telegram disimpan di folder host:

```text
./sessions/
```

dan di-mount ke container:

```text
/app/sessions
```

Dengan demikian, menghapus atau membuat ulang container tidak menghapus session Telegram.

Contohnya:

```text
VPS
│
├── sessions/
│   └── telegram.session
│
└── Docker
    │
    └── checker
        └── /app/sessions/telegram.session
```

---

# OCR

OCR menggunakan:

- Tesseract OCR
- English language data
- pytesseract
- OpenCV Headless

Gambar diproses dari bagian yang diperlukan saja untuk mengurangi penggunaan CPU dan memory.

Untuk proses checker, gambar tidak perlu disimpan permanen ke disk. Gambar dapat diproses langsung di memory setelah didownload.

---

# Keamanan

Jangan commit file berikut ke Git:

```text
.env
sessions/telegram.session
```

Contoh `.gitignore`:

```gitignore
.env

sessions/**
!sessions/.gitkeep

results/**
!results/.gitkeep

__pycache__/
*.pyc
```

**Session Telegram harus diperlakukan seperti credential.** Jangan membagikan file `telegram.session` kepada orang lain.

---

# Quick Start

Jika session belum ada:

```bash
docker compose run --rm checker python -m app.login
```

Setelah login berhasil:

```bash
docker compose up -d
```

Jika session sudah valid:

```bash
docker compose up -d
```

Jika session kemudian menjadi invalid:

```bash
docker compose run --rm checker python -m app.login
docker compose up -d
```
