# ============================================================
# database.py
# Konfigurasi koneksi MySQL menggunakan SQLAlchemy
# Menyediakan Session Factory dan Base class untuk semua model
# ============================================================

import os
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Muat environment variables dari file .env
load_dotenv()

# ─── Ambil Konfigurasi Database dari Environment Variables ─────────────────
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = os.getenv("DB_PORT", "3306")
DB_USER     = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME     = os.getenv("DB_NAME", "ai_konsultasi_db")

# ─── Buat Connection String (DATABASE_URL) ─────────────────────────────────
# Format: dialect+driver://user:password@host:port/dbname
# pymysql adalah driver Python murni untuk MySQL, tidak butuh MySQL client terinstall
DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    f"?charset=utf8mb4"  # utf8mb4 mendukung emoji dan karakter Unicode lengkap
)

# ─── Buat Engine SQLAlchemy ────────────────────────────────────────────────
# Engine adalah "jantung" koneksi database
# pool_pre_ping=True: tes koneksi sebelum digunakan (mencegah error koneksi mati)
# pool_recycle=3600: recycle koneksi setelah 1 jam untuk mencegah timeout MySQL
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,  # Ganti ke True untuk debug SQL queries di terminal
)

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
    print("✅ Database tables initialized successfully.")
