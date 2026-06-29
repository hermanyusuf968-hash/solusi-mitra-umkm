# ============================================================
# database.py
# Konfigurasi koneksi Database menggunakan SQLAlchemy
# Mendukung: MySQL (Railway/Production), SQLite (Fallback/Dev)
# ============================================================

import os
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Muat environment variables dari file .env
load_dotenv()

# ─── Ambil Konfigurasi Database dari Environment Variables ─────────────────
DB_HOST     = os.getenv("DB_HOST", "")
DB_PORT     = os.getenv("DB_PORT", "3306")
DB_USER     = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME     = os.getenv("DB_NAME", "ai_konsultasi_db")
DATABASE_URL = os.getenv("DATABASE_URL", "")

# ─── Bangun Connection URL ──────────────────────────────────────────────────
# Prioritas:
#   1. DATABASE_URL environment variable (Railway auto-inject)
#   2. Individual DB_* variables (manual config)
#   3. SQLite local fallback (development / tanpa database eksternal)

if DATABASE_URL:
    connection_url = DATABASE_URL
    # Railway mungkin memberikan URL dengan prefix "mysql://" (tanpa driver).
    # SQLAlchemy 2.x membutuhkan driver eksplisit, jadi kita ubah ke "mysql+pymysql://".
    if connection_url.startswith("mysql://"):
        connection_url = connection_url.replace("mysql://", "mysql+pymysql://", 1)
    # Jika Railway memberikan prefix "postgresql://" (untuk PostgreSQL), ubah juga.
    if connection_url.startswith("postgres://"):
        connection_url = connection_url.replace("postgres://", "postgresql://", 1)
elif DB_HOST:
    # Format: dialect+driver://user:password@host:port/dbname
    connection_url = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        f"?charset=utf8mb4"  # utf8mb4 mendukung emoji dan karakter Unicode lengkap
    )
else:
    # Fallback ke SQLite untuk development lokal tanpa MySQL
    connection_url = "sqlite:///./app.db"

# ─── Deteksi tipe database ──────────────────────────────────────────────────
is_sqlite = connection_url.startswith("sqlite")

# ─── Buat Engine SQLAlchemy ────────────────────────────────────────────────
# Engine adalah "jantung" koneksi database
# pool_pre_ping=True: tes koneksi sebelum digunakan (mencegah error koneksi mati)
# pool_recycle=3600: recycle koneksi setelah 1 jam untuk mencegah timeout MySQL

engine_kwargs = {
    "pool_pre_ping": True,
    "echo": False,  # Ganti ke True untuk debug SQL queries di terminal
}

# SQLite tidak mendukung pool_recycle dan pool_size options
if not is_sqlite:
    engine_kwargs["pool_recycle"] = 3600
    engine_kwargs["pool_size"] = 5
    engine_kwargs["max_overflow"] = 10
else:
    # SQLite membutuhkan check_same_thread=False untuk FastAPI (multi-threaded)
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(connection_url, **engine_kwargs)

# ─── Session Factory ────────────────────────────────────────────────────────
# SessionLocal adalah class factory — setiap pemanggilan SessionLocal()
# akan membuat sesi database baru yang terisolasi
SessionLocal = sessionmaker(
    autocommit=False,   # Transaksi harus di-commit secara eksplisit
    autoflush=False,    # Tidak flush otomatis sebelum query
    bind=engine
)

# ─── Base Class untuk Semua Model ORM ──────────────────────────────────────
# Setiap model (tabel) harus mewarisi Base agar terdaftar di SQLAlchemy
Base = declarative_base()


# ─── Dependency Injection: Database Session untuk FastAPI ──────────────────
def get_db():
    """
    Generator function untuk dependency injection di FastAPI.
    
    Pola ini memastikan sesi database selalu ditutup setelah request selesai,
    bahkan jika terjadi exception (karena ada blok finally).
    
    Penggunaan di FastAPI endpoint:
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db          # 'yield' menjadikan ini generator — db dikirim ke endpoint
    finally:
        db.close()        # Selalu tutup sesi setelah request, apapun yang terjadi


# ─── Fungsi Inisialisasi Database ───────────────────────────────────────────
def init_db():
    """
    Buat semua tabel yang didefinisikan di models.py jika belum ada.
    Dipanggil saat aplikasi FastAPI pertama kali dijalankan.
    """
    # Import models di sini untuk memastikan SQLAlchemy tahu tentang mereka
    from models import Base as ModelBase  # noqa: F401 - import untuk efek samping
    ModelBase.metadata.create_all(bind=engine)
    db_type = "SQLite (local)" if is_sqlite else "MySQL/PostgreSQL (remote)"
    print(f"✅ Database tables initialized successfully. [{db_type}]")
