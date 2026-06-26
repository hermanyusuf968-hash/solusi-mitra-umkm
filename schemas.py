# ============================================================
# schemas.py
# Validasi data input/output menggunakan Pydantic v2
# Schema dipisahkan dari ORM Models untuk menjaga arsitektur bersih
# ============================================================

from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, EmailStr, Field, field_validator
from enum import Enum


# ─── Enum (sama dengan models.py, tapi untuk Pydantic) ─────────────────────
class BusinessScaleEnum(str, Enum):
    MICRO  = "Mikro (kurang dari 5 karyawan)"
    SMALL  = "Kecil (5 hingga 19 karyawan)"
    MEDIUM = "Menengah (20 hingga 99 karyawan)"
    LARGE  = "Besar (100 karyawan ke atas)"


# ============================================================
# SCHEMA: User
# ============================================================

class UserCreate(BaseModel):
    """Data yang dibutuhkan untuk membuat user baru."""
    name:    str       = Field(..., min_length=2, max_length=100, description="Nama lengkap")
    email:   EmailStr  = Field(..., description="Alamat email valid")
    company: Optional[str] = Field(None, max_length=150, description="Nama perusahaan (opsional)")


class UserResponse(BaseModel):
    """Data user yang dikembalikan ke client (tidak termasuk data sensitif)."""
    id:         int
    name:       str
    email:      str
    company:    Optional[str]
    created_at: datetime

    # model_config: aktifkan mode ORM agar Pydantic bisa baca SQLAlchemy objects
    model_config = {"from_attributes": True}


# ============================================================
# SCHEMA: BusinessProfile
# ============================================================

class BusinessProfileCreate(BaseModel):
    """Data profil bisnis untuk request konsultasi baru."""
    business_name:  str              = Field(..., min_length=2, max_length=200, examples=["Warung Makan Sederhana"])
    industry:       str              = Field(..., min_length=2, max_length=100, examples=["Kuliner & F&B"])
    business_scale: BusinessScaleEnum = Field(..., description="Skala/ukuran bisnis")
    location:       str              = Field(..., min_length=3, max_length=200, examples=["Jakarta Selatan, DKI Jakarta"])
    description:    Optional[str]    = Field(None, max_length=500, description="Deskripsi singkat bisnis")

    @field_validator("business_name", "industry", "location")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        """Hilangkan spasi berlebih di awal/akhir string."""
        return v.strip()


class BusinessProfileResponse(BaseModel):
    """Data profil bisnis yang dikembalikan ke client."""
    id:             int
    user_id:        Optional[int]
    business_name:  str
    industry:       str
    business_scale: str
    location:       str
    description:    Optional[str]
    created_at:     datetime

    model_config = {"from_attributes": True}


# ============================================================
# SCHEMA: Consultation Request
# Data yang dikirim dari Frontend ke Backend saat minta solusi
# ============================================================

class ConsultationRequest(BaseModel):
    """
    Payload lengkap untuk memulai sesi konsultasi AI.
    Menggabungkan data profil bisnis + masalah dalam satu request.
    """
    # Data Identitas (opsional — untuk mode anonim)
    user_name:    Optional[str]      = Field(None, max_length=100, description="Nama konsultan/pemilik")
    user_email:   Optional[str]      = Field(None, description="Email (opsional)")
    
    # Data Profil Bisnis
    business_name:  str              = Field(..., min_length=2, max_length=200, examples=["Toko Baju Online 'Modis'"])
    industry:       str              = Field(..., min_length=2, max_length=100, examples=["E-commerce Fashion"])
    business_scale: BusinessScaleEnum = Field(..., description="Pilih skala bisnis")
    location:       str              = Field(..., min_length=3, max_length=200, examples=["Bandung, Jawa Barat"])
    business_description: Optional[str] = Field(None, max_length=500)

    # Masalah yang Ingin Dikonsultasikan
    problem_statement: str = Field(
        ...,
        min_length=20,
        max_length=2000,
        description="Deskripsikan masalah bisnis Anda secara detail",
        examples=["Penjualan saya turun 40% dalam 3 bulan terakhir setelah ada kompetitor baru yang menjual produk serupa dengan harga lebih murah. Saya tidak tahu harus apa."]
    )

    @field_validator("problem_statement")
    @classmethod
    def validate_problem_length(cls, v: str) -> str:
        """Pastikan masalah cukup detail untuk dianalisis AI."""
        if len(v.strip()) < 20:
            raise ValueError("Deskripsikan masalah Anda minimal 20 karakter agar AI bisa menganalisis dengan baik.")
        return v.strip()


# ============================================================
# SCHEMA: AI Response JSON Structure
# Struktur JSON yang DIHARAPKAN dikembalikan oleh AI
# ============================================================

class ActionStep(BaseModel):
    """Satu langkah aksi dalam rencana solusi."""
    langkah:       int    = Field(..., description="Nomor urut langkah")
    judul:         str    = Field(..., description="Judul singkat langkah")
    deskripsi:     str    = Field(..., description="Penjelasan detail langkah")
    timeline:      str    = Field(..., description="Estimasi waktu (contoh: '1-2 Minggu')")
    prioritas:     str    = Field(..., description="Tingkat prioritas: Tinggi / Sedang / Rendah")


class AIConsultationResult(BaseModel):
    """
    Struktur JSON yang dihasilkan oleh AI.
    Pydantic akan memvalidasi format output sebelum disimpan ke DB.
    """
    ringkasan_masalah:    str              = Field(..., description="Ringkasan masalah dari sudut pandang analis")
    analisis_akar_masalah: List[str]       = Field(..., description="Daftar akar penyebab masalah")
    solusi_utama:         str              = Field(..., description="Solusi rekomendasi utama")
    langkah_aksi:         List[ActionStep] = Field(..., description="Rencana aksi step-by-step")
    estimasi_dampak:      str              = Field(..., description="Prediksi dampak positif jika solusi diterapkan")
    risiko_dan_mitigasi:  List[str]        = Field(..., description="Potensi risiko dan cara mitigasinya")
    sumber_daya_dibutuhkan: List[str]      = Field(..., description="Resource yang dibutuhkan (anggaran, SDM, waktu)")
    kpi_saran:            List[str]        = Field(..., description="KPI yang disarankan untuk mengukur keberhasilan")
    catatan_konsultan:    str              = Field(..., description="Catatan tambahan dari perspektif konsultan")


# ============================================================
# SCHEMA: Consultation Response
# Data konsultasi yang dikembalikan ke client
# ============================================================

class ConsultationResponse(BaseModel):
    """Response lengkap setelah konsultasi berhasil diproses."""
    id:                  int
    business_profile_id: int
    problem_statement:   str
    ai_response_json:    Optional[Dict[str, Any]]  # JSON dari AI
    ai_model_used:       Optional[str]
    status:              str
    processing_time_ms:  Optional[int]
    error_message:       Optional[str]
    created_at:          datetime

    model_config = {"from_attributes": True}


class ConsultationListItem(BaseModel):
    """Versi ringkas untuk tampilan daftar di Dashboard."""
    id:                  int
    business_name:       str   # Dari relasi business_profile
    industry:            str
    problem_statement:   str
    status:              str
    ai_model_used:       Optional[str]
    processing_time_ms:  Optional[int]
    created_at:          datetime

    model_config = {"from_attributes": True}


# ============================================================
# SCHEMA: API Response Wrapper
# Standarisasi format respons API
# ============================================================

class APIResponse(BaseModel):
    """Wrapper standar untuk semua respons API."""
    success: bool                  = True
    message: str                   = "OK"
    data:    Optional[Any]         = None


class PaginatedResponse(BaseModel):
    """Response untuk endpoint yang mengembalikan daftar dengan paginasi."""
    success:     bool              = True
    message:     str               = "OK"
    data:        List[Any]         = []
    total:       int               = 0
    page:        int               = 1
    per_page:    int               = 10
    total_pages: int               = 1
