# ============================================================
# models.py
# Definisi tabel-tabel MySQL menggunakan SQLAlchemy ORM
# Tabel: users, business_profiles, consultations
# ============================================================

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime,
    ForeignKey, Enum, JSON
)
from sqlalchemy.orm import relationship
from database import Base
import enum


# ─── Enum untuk Skala Bisnis ────────────────────────────────────────────────
class BusinessScale(str, enum.Enum):
    """Enum skala bisnis — digunakan di tabel business_profiles."""
    MICRO      = "Mikro (kurang dari 5 karyawan)"
    SMALL      = "Kecil (5 hingga 19 karyawan)"
    MEDIUM     = "Menengah (20 hingga 99 karyawan)"
    LARGE      = "Besar (100 karyawan ke atas)"


# ─── Enum untuk Status Konsultasi ───────────────────────────────────────────
class ConsultationStatus(str, enum.Enum):
    """Status pemrosesan konsultasi oleh AI."""
    PENDING    = "pending"
    SUCCESS    = "success"
    FAILED     = "failed"


# ============================================================
# TABEL: users
# Menyimpan data pengguna platform
# ============================================================
class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name       = Column(String(100), nullable=False, comment="Nama lengkap pengguna")
    email      = Column(String(150), unique=True, index=True, nullable=False, comment="Email unik pengguna")
    company    = Column(String(150), nullable=True, comment="Nama perusahaan/organisasi")
    
    # Timestamps — disimpan dalam UTC
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ─── Relasi: satu user bisa punya banyak business_profiles ───────────────
    # back_populates membuat relasi dua arah (bidirectional)
    business_profiles = relationship(
        "BusinessProfile",
        back_populates="user",
        cascade="all, delete-orphan"  # Hapus profiles jika user dihapus
    )

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"


# ============================================================
# TABEL: business_profiles
# Menyimpan profil bisnis yang dikonsultasikan
# ============================================================
class BusinessProfile(Base):
    __tablename__ = "business_profiles"

    id             = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign Key ke tabel users — NULL jika konsultasi anonim
    user_id        = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    business_name  = Column(String(200), nullable=False, comment="Nama bisnis/usaha")
    industry       = Column(String(100), nullable=False, comment="Sektor industri bisnis")
    
    # Menggunakan Enum MySQL native untuk konsistensi data
    business_scale = Column(
        Enum(BusinessScale),
        nullable=False,
        comment="Skala/ukuran bisnis"
    )
    location       = Column(String(200), nullable=False, comment="Lokasi bisnis (kota/provinsi)")
    description    = Column(Text, nullable=True, comment="Deskripsi singkat bisnis (opsional)")
    
    created_at     = Column(DateTime, default=datetime.utcnow, nullable=False)

    # ─── Relasi: banyak consultations bisa terhubung ke satu business_profile ─
    user          = relationship("User", back_populates="business_profiles")
    consultations = relationship(
        "Consultation",
        back_populates="business_profile",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<BusinessProfile(id={self.id}, name='{self.business_name}', industry='{self.industry}')>"


# ============================================================
# TABEL: consultations
# Menyimpan setiap sesi konsultasi + hasil AI
# ============================================================
class Consultation(Base):
    __tablename__ = "consultations"

    id                   = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign Key ke business_profiles — wajib ada
    business_profile_id  = Column(
        Integer,
        ForeignKey("business_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # ─── Input dari User ───────────────────────────────────────────────────
    problem_statement    = Column(Text, nullable=False, comment="Deskripsi masalah bisnis dari user")
    
    # ─── Output dari AI ────────────────────────────────────────────────────
    # JSON Column: menyimpan output AI yang terstruktur (dict/list)
    # SQLAlchemy JSON type otomatis serialize/deserialize Python dict ↔ JSON string
    ai_response_json     = Column(JSON, nullable=True, comment="Hasil analisis AI dalam format JSON terstruktur")
    
    # Menyimpan raw prompt yang dikirim ke AI (berguna untuk debugging)
    prompt_used          = Column(Text, nullable=True, comment="Prompt lengkap yang dikirimkan ke AI")
    
    # Model AI yang digunakan (contoh: "gemini-1.5-flash", "gpt-4o")
    ai_model_used        = Column(String(100), nullable=True, comment="Nama model AI yang digunakan")
    
    status               = Column(
        Enum(ConsultationStatus),
        default=ConsultationStatus.PENDING,
        nullable=False
    )
    
    # Menyimpan pesan error jika AI gagal merespons
    error_message        = Column(Text, nullable=True, comment="Pesan error jika konsultasi gagal")
    
    # Waktu pemrosesan AI dalam milidetik (untuk monitoring performa)
    processing_time_ms   = Column(Integer, nullable=True, comment="Durasi pemrosesan AI dalam milidetik")
    
    created_at           = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # ─── Relasi ke business_profile ────────────────────────────────────────
    business_profile     = relationship("BusinessProfile", back_populates="consultations")

    def __repr__(self):
        return (
            f"<Consultation(id={self.id}, "
            f"profile_id={self.business_profile_id}, "
            f"status='{self.status}')>"
        )
