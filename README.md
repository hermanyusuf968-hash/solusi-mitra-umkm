# Solusi Mitra UMKM — Frontend Baru (HTML/CSS/JS murni)

Frontend ini menggantikan `frontend.py` (Streamlit) dengan website statis ringan
yang berbicara langsung ke `backend.py` (FastAPI) yang sudah ada — **tidak ada
perubahan apa pun di backend**.

## Cara menjalankan

1. Jalankan backend seperti biasa:
   ```bash
   uvicorn backend:app --reload --host 0.0.0.0 --port 8000
   ```

2. Buka `index.html` di folder ini dengan server statis apa pun, contoh:
   ```bash
   cd frontend-baru
   python3 -m http.server 5500
   ```
   Lalu buka `http://localhost:5500` di browser.

   (Tidak disarankan membuka langsung lewat `file://` di sebagian browser
   karena beberapa fitur fetch bisa dibatasi oleh kebijakan CORS lokal.)

3. Jika backend Anda berjalan di alamat/port selain `http://localhost:8000`,
   ubah satu baris ini di `index.html` (dekat bagian atas `<head>`):
   ```html
   <script>
     window.__BACKEND_URL__ = "http://localhost:8000";
   </script>
   ```

## Struktur

```
frontend-baru/
├── index.html     # Shell SPA: navbar, semua halaman (view), footer
├── style.css      # Semua desain: token warna dari logo, animasi, layout
├── app.js         # Router hash-based + semua panggilan API + interaktivitas
└── assets/
    ├── mark-padded.png   # Lambang logo (navbar & footer)
    └── favicon.png       # Ikon tab browser
```

Tidak ada framework, tidak ada langkah build, tidak ada `npm install`.
Murni HTML/CSS/JS agar tetap ringan dan cepat dimuat.

## Yang berubah dari versi lama

- **Bukan lagi Streamlit** — sekarang SPA murni dengan client-side routing
  (`#/`, `#/konsultasi`, `#/riwayat`, `#/detail`), jadi perpindahan halaman
  tidak memuat ulang seluruh aplikasi.
- **Warna** diturunkan langsung dari `logo.jpg`/`logo_web.png`: emas (bar chart)
  dan biru elektrik (panah), di atas latar gelap hangat khas brand "Solusi
  Mitra UMKM" — bukan palet biru-putih generik.
- **Animasi**: splash loading saat pertama buka, progress bar tipis di atas
  saat pindah halaman, scroll-reveal di beranda, skeleton loading saat data
  dashboard/detail sedang diambil, progress bertahap saat konsultasi diproses,
  hover halus di semua kartu dan tombol. Semua menghormati
  `prefers-reduced-motion` untuk pengguna yang sensitif terhadap animasi.
- **Endpoint API yang dipakai** (semua sudah ada di `backend.py`, tidak ada
  endpoint baru): `GET /health`, `GET /api/stats/`, `POST /api/consultations/`,
  `GET /api/consultations/`, `GET /api/consultations/{id}`.

## Catatan untuk produksi

- `CORSMiddleware` di `backend.py` saat ini `allow_origins=["*"]` — aman untuk
  development, tapi sebaiknya dibatasi ke domain frontend Anda saat deploy.
- File di `assets/` sudah dikompres (total ±100 KB) — tidak perlu CDN untuk
  skala UMKM ini.
