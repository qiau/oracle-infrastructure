# Hermes Agent

[Hermes Agent](https://github.com/NousResearch/hermes-agent) dari Nous Research dijalankan sebagai **gateway** yang terhubung ke Telegram. Bot bisa diajak chat, mengerjakan tugas, menjalankan tool, dan menyimpan memory/skill antar sesi.

Layanan ini berdiri sendiri sebagai project Compose. Kembali ke [README root](../README.md) untuk gambaran seluruh infrastruktur.

---

## Ringkasan Service

| Item | Nilai |
| --- | --- |
| Image | `nousresearch/hermes-agent:latest` |
| Command | `gateway run` |
| Container | `hermes` |
| Network | `hermes` (external, satu network dengan `9router`) |
| Volume | `./data:/opt/data`, `./workspace:/workspace` |
| Resource | memori `2G`, CPU `1.0`, `shm_size: 1g` |
| Keamanan | `no-new-privileges:true` |
| Restart | `unless-stopped` |

Arti volume:

| Path host | Path container | Isi |
| --- | --- | --- |
| `hermes/data/` | `/opt/data` | Sumber state utama: `config.yaml`, `.env`, `SOUL.md`, session, memory, skill, cron, log |
| `hermes/workspace/` | `/workspace` | File kerja agent (dokumen, hasil generate, dsb.) |

> `data/` adalah satu-satunya sumber state Hermes. Jangan menjalankan dua container gateway terhadap folder `data/` yang sama secara bersamaan.

---

## Prasyarat

- External network `hermes` sudah dibuat:
  ```bash
  docker network create hermes
  ```
- Bot Telegram dari [@BotFather](https://t.me/BotFather) — token berbentuk `123456789:ABCdef...`
- Telegram user ID numerik (bukan username), mis. lewat [@userinfobot](https://t.me/userinfobot)
- API key model provider (OpenAI, Anthropic, Nous, dsb.) **atau** endpoint `9router` yang sudah berjalan

---

## Konfigurasi `.env`

```bash
cp .env.example .env
chmod 600 .env
nano .env
```

| Variabel | Wajib | Keterangan |
| --- | --- | --- |
| `TZ` | Tidak | Timezone, default `Asia/Jakarta` |
| `TELEGRAM_BOT_TOKEN` | Ya | Token bot dari BotFather |
| `TELEGRAM_ALLOWED_USERS` | Ya | User ID yang boleh memakai bot, pisahkan dengan koma |

`.env` di folder ini diteruskan ke container sebagai environment (lewat `env_file`). Kunci API provider sebaiknya disimpan di `data/.env` — file itu dibuat oleh wizard dan ikut persist di volume. Jangan commit `.env` maupun `data/`.

---

## Setup Pertama Kali

**1. Jalankan wizard** untuk membuat config, `data/.env`, dan `SOUL.md`:

```bash
docker compose run --rm hermes setup
```

Wizard akan menanyakan provider model/API key dan platform messaging. Pilih Telegram bila diminta, lalu isi token dan user ID.

**2. Nyalakan service:**

```bash
docker compose up -d
```

**3. Cek log:**

```bash
docker compose logs -f --tail=100
```

**4. Buka bot di Telegram** dan kirim `/start`. Jika bot tidak merespons, lihat bagian [Troubleshooting](#troubleshooting).

> Jika wizard dilewati, isi minimal `TELEGRAM_BOT_TOKEN` dan `TELEGRAM_ALLOWED_USERS` di `.env`, lalu konfigurasi provider model secara manual di `data/config.yaml` / `data/.env`.

---

## Menghubungkan Telegram

1. Buat bot lewat **@BotFather** (`/newbot`) dan salin tokennya.
2. Ambil user ID numerik kamu (mis. **@userinfobot**).
3. Isi kedua nilai di `.env`.
4. `docker compose up -d` (atau `docker compose restart hermes` jika sudah berjalan).

Catatan grup:

- Default-nya bot hanya menerima pesan yang relevan. Untuk grup, matikan **Group Privacy** di BotFather atau jadikan bot admin, lalu keluarkan dan masukkan ulang bot ke grup.
- `TELEGRAM_ALLOWED_USERS` tetap berlaku di grup — hanya user terdaftar yang bisa memicu bot.

---

## Menggunakan Model via 9Router

`hermes` dan `9router` berada di network `hermes` yang sama, sehingga 9Router bisa dipakai sebagai endpoint OpenAI-compatible:

```text
http://9router:20128/v1
```

Langkah singkat:

1. Pastikan container `9router` berjalan dan sudah dikonfigurasi (lihat folder [`../9router`](../9router)).
2. Buat API key di dashboard 9Router. Nilai `REQUIRE_API_KEY=true` membuat endpoint menolak request tanpa key.
3. Di Hermes, daftarkan provider dengan base URL di atas dan API key tersebut — lewat wizard (`docker compose run --rm hermes setup`) atau `data/config.yaml`.
4. Restart: `docker compose restart hermes`.

Alternatif: memakai API key provider langsung (tanpa 9Router). Cukup isi key di `data/.env`, mis. `OPENAI_API_KEY` atau `ANTHROPIC_API_KEY`.

---

## Operasional

```bash
# Log realtime
docker compose logs -f --tail=100

# Restart
docker compose restart

# Stop tanpa menghapus data
docker compose down

# Update image
docker compose pull && docker compose up -d

# Masuk ke container
docker exec -it hermes bash

# Perintah Hermes di dalam container
docker exec -it hermes hermes --help
docker exec -it hermes hermes gateway status
```

Log gateway juga ditulis ke `data/logs/` (mis. `data/logs/gateways/default/current`) dan tetap ada setelah container di-recreate.

---

## Backup & Restore

Yang perlu di-backup:

| Path | Isi |
| --- | --- |
| `data/` | Config, API key, session, memory, skill, cron, log |
| `workspace/` | File kerja agent |

Hentikan container dulu agar state SQLite konsisten:

```bash
docker compose stop
tar czf hermes-backup-$(date +%F).tar.gz data workspace
docker compose up -d
```

Simpan arsip di tempat terenkripsi — `data/.env` berisi API key dan `data/` berisi riwayat percakapan.

---

## Troubleshooting

| Gejala | Penyebab umum | Solusi |
| --- | --- | --- |
| Container langsung exit / restart terus | `.env` belum ada atau token kosong | `docker compose config`, lalu `docker compose logs` |
| Bot tidak merespons | Token salah, bot belum di-`/start`, atau tidak ada koneksi keluar | Cek log; pastikan token valid dan host bisa mengakses Telegram |
| Bot mengabaikan pesan | User ID tidak ada di `TELEGRAM_ALLOWED_USERS` | Tambahkan ID, lalu restart |
| Bot diam di grup | Group Privacy masih aktif | Matikan di BotFather atau jadikan bot admin, lalu re-add bot |
| Error koneksi ke 9Router | Container `9router` mati / beda network | `docker network inspect hermes`, cek `docker ps` |
| Container OOM / mati saat browsing | Limit memori terlalu kecil | Naikkan `memory` di `compose.yaml` (disarankan 2–4 GB) |
| State rusak setelah restore | Container masih berjalan saat backup | Stop container sebelum backup/restore |

Debug cepat:

```bash
docker compose config
docker inspect hermes
docker exec -it hermes hermes gateway status
```

---

## Keamanan

- **Token bot = kendali penuh bot.** Jika bocor, revoke lewat `/revoke` di BotFather lalu ganti di `.env`.
- **Batasi akses** dengan `TELEGRAM_ALLOWED_USERS`; jangan biarkan bot terbuka untuk publik.
- **`data/` berisi credential** (API key, session, memory). Jangan commit atau membagikannya.
- Container memakai `no-new-privileges`, tanpa port yang dipublikasikan ke host, dan limit CPU/memori.
- Hermes berjalan di network terpisah (`hermes`), tidak bercampur dengan database atau layanan publik.

---

## Referensi

- [Dokumentasi Hermes Agent](https://hermes-agent.nousresearch.com/docs/)
- [Docker setup](https://hermes-agent.nousresearch.com/docs/user-guide/docker)
- [Telegram setup](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram)
- [Konfigurasi](https://hermes-agent.nousresearch.com/docs/user-guide/configuration)
