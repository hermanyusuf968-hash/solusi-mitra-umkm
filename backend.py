# ============================================================
# backend.py
# Aplikasi FastAPI — Server Backend untuk Platform Konsultasi AI
# Menangani: Konsultasi AI, CRUD data, Riwayat Dashboard
# ============================================================

import os
import json
import time
import logging
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# ─── Import Modul Lokal ─────────────────────────────────────────────────────
from database import get_db, init_db
from models import User, BusinessProfile, Consultation, ConsultationStatus, BusinessScale
from schemas import (
    ConsultationRequest, ConsultationResponse, ConsultationListItem,
    AIConsultationResult, APIResponse, UserCreate, UserResponse
)

# ─── Load Environment Variables ─────────────────────────────────────────────
load_dotenv()

# ─── Setup Logging ───────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# ─── Konfigurasi AI ──────────────────────────────────────────────────────────
AI_PROVIDER   = os.getenv("AI_PROVIDER", "gemini").lower()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


# ============================================================
# INISIALISASI FASTAPI APP
# ============================================================
app = FastAPI(
    title="AI Business Consultation API",
    description="Platform Konsultasi Bisnis Berbasis AI — FastAPI Backend",
    version="1.0.0",
    docs_url="/docs",      # Swagger UI: http://localhost:8000/docs
    redoc_url="/redoc",    # ReDoc: http://localhost:8000/redoc
)

# ─── CORS Middleware ─────────────────────────────────────────────────────────
# Izinkan origin frontend Vercel serta localhost untuk development.
# Di production, pastikan domain frontend Anda tetap terdaftar.
allowed_origins = [
    origin.strip().rstrip("/")
    for origin in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "https://solusimitraumkm.vercel.app"
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Inisialisasi Database saat Startup ──────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    """Jalankan inisialisasi saat aplikasi pertama kali start."""
    logger.info("Starting AI Business Consultation API...")
    init_db()  # Buat tabel jika belum ada
    logger.info(f"AI Provider: {AI_PROVIDER.upper()}")


# ============================================================
# AI SERVICE LAYER
# Fungsi untuk berinteraksi dengan Gemini atau OpenAI
# ============================================================

def build_master_prompt(request: ConsultationRequest) -> str:
    """
    Membangun 'Master Prompt' yang ketat dan terstruktur untuk AI.
    
    Prompt ini dirancang agar AI SELALU mengembalikan respons dalam format
    JSON yang valid dan terstruktur, bukan teks biasa.
    
    Args:
        request: Data konsultasi dari user
    
    Returns:
        String prompt lengkap yang siap dikirim ke AI
    """
    prompt = f"""Anda adalah konsultan bisnis senior berpengalaman 20+ tahun di Indonesia dengan keahlian di bidang strategi bisnis, manajemen operasional, pemasaran digital, dan transformasi UMKM.

PROFIL BISNIS KLIEN:
- Nama Bisnis    : {request.business_name}
- Industri       : {request.industry}
- Skala Bisnis   : {request.business_scale.value}
- Lokasi         : {request.location}
- Deskripsi      : {request.business_description or "Tidak tersedia"}

MASALAH YANG DIKONSULTASIKAN:
{request.problem_statement}

INSTRUKSI PENTING — WAJIB DIIKUTI:
1. Analisis masalah di atas secara mendalam dan komprehensif.
2. Berikan solusi yang PRAKTIS, SPESIFIK untuk konteks bisnis Indonesia, dan DAPAT DIIMPLEMENTASIKAN.
3. Sesuaikan solusi dengan skala bisnis klien (jangan rekomendasikan solusi enterprise untuk bisnis mikro).
4. Pertimbangkan kondisi pasar lokal, regulasi Indonesia, dan keterbatasan sumber daya UMKM.
5. Respons Anda HARUS berupa PURE JSON VALID — tidak boleh ada teks di luar JSON, tidak ada markdown, tidak ada penjelasan tambahan.
6. Gunakan bahasa Indonesia yang profesional namun mudah dipahami.

FORMAT JSON YANG HARUS DIKEMBALIKAN (ikuti PERSIS struktur ini):
{{
    "ringkasan_masalah": "string — ringkasan masalah dalam 2-3 kalimat dari perspektif analis bisnis",
    "analisis_akar_masalah": ["string akar masalah 1", "string akar masalah 2", "..."],
    "solusi_utama": "string — solusi rekomendasi utama dalam 2-4 kalimat",
    "langkah_aksi": [
        {{
            "langkah": 1,
            "judul": "string — judul singkat langkah",
            "deskripsi": "string — penjelasan detail dan cara implementasinya",
            "timeline": "string — estimasi waktu, contoh: '1-2 Minggu'",
            "prioritas": "string — salah satu dari: Tinggi / Sedang / Rendah"
        }}
    ],
    "estimasi_dampak": "string — prediksi dampak positif jika solusi diterapkan dengan baik",
    "risiko_dan_mitigasi": ["string risiko beserta cara mitigasinya 1", "..."],
    "sumber_daya_dibutuhkan": ["string sumber daya 1", "..."],
    "kpi_saran": ["string KPI 1", "string KPI 2", "..."],
    "catatan_konsultan": "string — catatan tambahan, insight, atau peringatan khusus dari konsultan"
}}

Berikan minimal 4 langkah aksi yang konkret dan minimal 3 item untuk setiap array.
INGAT: Respons HANYA berupa JSON murni, tidak ada teks lain."""

    return prompt


def call_gemini_api(prompt: str) -> dict:
    """
    Panggil Google Gemini API dan kembalikan hasil parsing JSON.
    
    Args:
        prompt: Master prompt yang sudah dibangun
    
    Returns:
        Tuple (Dictionary hasil parsing JSON dari respons AI, nama model)
    
    Raises:
        Exception jika API gagal atau respons bukan JSON valid
    """
    try:
        import google.generativeai as genai
        
        # Konfigurasi API key
        genai.configure(api_key=GOOGLE_API_KEY)
        
        logger.info("Sending request to Gemini API...")
        
        # Gunakan Gemini Pro dengan text generation
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.4,
                top_p=0.9,
                max_output_tokens=4096,
                response_mime_type="application/json",
            )
        )
        
        # Ambil teks respons
        raw_text = response.text.strip() if response.text else ""
        logger.info(f"Gemini API responded ({len(raw_text)} chars)")
        
        # Bersihkan jika ada markdown code fence (```json ... ```)
        if raw_text.startswith("```"):
            lines = raw_text.split("\n")
            # Hapus baris pertama (```json) dan terakhir (```)
            raw_text = "\n".join(lines[1:-1]).strip()
        
        # Parse JSON
        return json.loads(raw_text), "gemini-1.5-flash"

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini response as JSON: {e}")
        raise ValueError(f"AI mengembalikan format yang tidak valid: {str(e)}")
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        raise


def call_openai_api(prompt: str) -> dict:
    """
    Panggil OpenAI API sebagai alternatif Gemini.
    Menggunakan mode JSON untuk memastikan output selalu valid JSON.
    
    Args:
        prompt: Master prompt yang sudah dibangun
    
    Returns:
        Tuple (Dictionary hasil parsing JSON, nama model)
    """
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        logger.info("Sending request to OpenAI API...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",           # Model hemat biaya untuk MVP
            response_format={"type": "json_object"},  # Mode JSON: SELALU kembalikan JSON
            messages=[
                {
                    "role": "system",
                    "content": "Anda adalah konsultan bisnis senior Indonesia. Selalu respons dengan JSON murni yang valid sesuai format yang diminta."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4,
            max_tokens=4096,
        )
        
        raw_text = response.choices[0].message.content.strip()
        logger.info(f"OpenAI API responded ({len(raw_text)} chars)")
        
        return json.loads(raw_text), "gpt-4o-mini"

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse OpenAI response as JSON: {e}")
        raise ValueError(f"AI mengembalikan format yang tidak valid: {str(e)}")
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        raise


def call_ai_api(prompt: str) -> tuple:
    """
    Router: memanggil AI yang sesuai berdasarkan konfigurasi AI_PROVIDER.
    
    Returns:
        Tuple (dict hasil AI, string nama model)
    """
    if AI_PROVIDER == "openai":
        return call_openai_api(prompt)
    else:
        # Default ke Gemini
        return call_gemini_api(prompt)


# ============================================================
# ENDPOINTS
# ============================================================

# ─── Health Check ────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    """Endpoint health check — pastikan server berjalan."""
    return {
        "status": "online",
        "service": "AI Business Consultation API",
        "version": "1.0.0",
        "ai_provider": AI_PROVIDER,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health", tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    """Health check termasuk koneksi database."""
    try:
        # Test query sederhana untuk cek koneksi DB
        db.execute(__import__('sqlalchemy').text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "ai_provider": AI_PROVIDER,
    }


# ─── ENDPOINT UTAMA: Proses Konsultasi AI ────────────────────────────────────
@app.post("/api/consultations/", response_model=APIResponse, tags=["Consultations"])
async def create_consultation(
    request: ConsultationRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint utama: Terima data bisnis + masalah, proses ke AI, simpan ke DB.
    
    Flow:
    1. Validasi input (Pydantic otomatis)
    2. Cari atau buat User (jika email diberikan)
    3. Simpan BusinessProfile ke DB
    4. Bangun Master Prompt
    5. Panggil AI API
    6. Validasi respons JSON dari AI
    7. Simpan Consultation + hasil AI ke DB
    8. Kembalikan data konsultasi ke frontend
    """
    
    # Catat waktu mulai untuk mengukur durasi pemrosesan
    start_time = time.time()
    
    # ─── Step 1: Cari atau Buat User (opsional) ──────────────────────────
    user_id = None
    if request.user_email:
        existing_user = db.query(User).filter(User.email == request.user_email).first()
        if existing_user:
            user_id = existing_user.id
            logger.info(f"Found existing user: {existing_user.name} (id={user_id})")
        elif request.user_name:
            # Buat user baru jika belum ada
            new_user = User(
                name=request.user_name,
                email=request.user_email,
            )
            db.add(new_user)
            db.flush()  # flush untuk mendapat ID tanpa commit final
            user_id = new_user.id
            logger.info(f"Created new user: {new_user.name} (id={user_id})")
    
    # ─── Step 2: Simpan Business Profile ke Database ─────────────────────
    business_profile = BusinessProfile(
        user_id=user_id,
        business_name=request.business_name,
        industry=request.industry,
        business_scale=BusinessScale(request.business_scale.value),
        location=request.location,
        description=request.business_description,
    )
    db.add(business_profile)
    db.flush()  # Dapat ID profile sebelum commit
    logger.info(f"BusinessProfile created: {business_profile.business_name} (id={business_profile.id})")
    
    # ─── Step 3: Bangun Master Prompt ────────────────────────────────────
    master_prompt = build_master_prompt(request)
    
    # ─── Step 4: Buat Record Konsultasi dengan Status PENDING ────────────
    consultation = Consultation(
        business_profile_id=business_profile.id,
        problem_statement=request.problem_statement,
        prompt_used=master_prompt,  # Simpan prompt untuk audit trail
        status=ConsultationStatus.PENDING,
    )
    db.add(consultation)
    db.flush()
    logger.info(f"Consultation record created (id={consultation.id}), calling AI...")
    
    # ─── Step 5: Panggil AI API ──────────────────────────────────────────
    try:
        ai_result_dict, model_name = call_ai_api(master_prompt)
        
        # Hitung durasi pemrosesan
        processing_time = int((time.time() - start_time) * 1000)  # dalam ms
        
        # ─── Step 6: Update consultation dengan hasil AI ─────────────────
        consultation.ai_response_json   = ai_result_dict
        consultation.ai_model_used      = model_name
        consultation.status             = ConsultationStatus.SUCCESS
        consultation.processing_time_ms = processing_time
        
        # Commit semua perubahan ke database dalam satu transaksi
        db.commit()
        db.refresh(consultation)
        
        logger.info(
            f"Consultation {consultation.id} completed in {processing_time}ms "
            f"using {model_name}"
        )
        
        # ─── Siapkan data response ────────────────────────────────────────
        response_data = {
            "id":                  consultation.id,
            "business_profile_id": consultation.business_profile_id,
            "business_name":       request.business_name,
            "industry":            request.industry,
            "problem_statement":   consultation.problem_statement,
            "ai_response_json":    consultation.ai_response_json,
            "ai_model_used":       consultation.ai_model_used,
            "status":              consultation.status.value,
            "processing_time_ms":  consultation.processing_time_ms,
            "created_at":          consultation.created_at.isoformat(),
        }
        
        return APIResponse(
            success=True,
            message=f"Konsultasi berhasil diproses oleh {model_name} dalam {processing_time}ms",
            data=response_data
        )
    
    except Exception as e:
        # ─── Tangani Error: Update status ke FAILED ───────────────────────
        processing_time = int((time.time() - start_time) * 1000)
        consultation.status             = ConsultationStatus.FAILED
        consultation.error_message      = str(e)
        consultation.processing_time_ms = processing_time
        
        db.commit()  # Tetap commit agar record error tersimpan
        
        logger.error(f"Consultation {consultation.id} failed: {e}")
        
        raise HTTPException(
            status_code=500,
            detail=f"AI processing failed: {str(e)}"
        )


# ─── ENDPOINT: Ambil Semua Riwayat Konsultasi (untuk Dashboard) ──────────────
@app.get("/api/consultations/", response_model=APIResponse, tags=["Consultations"])
async def get_consultations(
    page:       int = Query(1, ge=1, description="Nomor halaman"),
    per_page:   int = Query(10, ge=1, le=50, description="Jumlah item per halaman"),
    status:     Optional[str] = Query(None, description="Filter by status: success, failed, pending"),
    db:         Session = Depends(get_db)
):
    """
    Ambil daftar semua riwayat konsultasi untuk ditampilkan di Dashboard.
    Mendukung paginasi dan filter by status.
    """
    # Query dengan JOIN untuk mendapat nama bisnis dari relasi
    query = db.query(Consultation).join(
        BusinessProfile,
        Consultation.business_profile_id == BusinessProfile.id
    )
    
    # Filter by status jika diminta
    if status:
        try:
            status_enum = ConsultationStatus(status)
            query = query.filter(Consultation.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Status tidak valid: {status}")
    
    # Hitung total untuk paginasi
    total = query.count()
    
    # Ambil data dengan paginasi dan urutan terbaru dulu
    consultations = (
        query
        .order_by(Consultation.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    
    # Susun data response
    items = []
    for c in consultations:
        items.append({
            "id":                  c.id,
            "business_name":       c.business_profile.business_name,
            "industry":            c.business_profile.industry,
            "business_scale":      c.business_profile.business_scale.value,
            "location":            c.business_profile.location,
            "problem_statement":   c.problem_statement[:200] + "..." if len(c.problem_statement) > 200 else c.problem_statement,
            "status":              c.status.value,
            "ai_model_used":       c.ai_model_used,
            "processing_time_ms":  c.processing_time_ms,
            "created_at":          c.created_at.isoformat(),
        })
    
    return APIResponse(
        success=True,
        message=f"Ditemukan {total} konsultasi",
        data={
            "items":       items,
            "total":       total,
            "page":        page,
            "per_page":    per_page,
            "total_pages": (total + per_page - 1) // per_page,
        }
    )


# ─── ENDPOINT: Ambil Detail Satu Konsultasi ──────────────────────────────────
@app.get("/api/consultations/{consultation_id}", response_model=APIResponse, tags=["Consultations"])
async def get_consultation_detail(
    consultation_id: int,
    db: Session = Depends(get_db)
):
    """
    Ambil detail lengkap satu konsultasi berdasarkan ID.
    Dipakai saat user klik 'Lihat Detail' di dashboard.
    Tidak memanggil AI ulang — data diambil langsung dari database.
    """
    consultation = db.query(Consultation).filter(
        Consultation.id == consultation_id
    ).first()
    
    if not consultation:
        raise HTTPException(
            status_code=404,
            detail=f"Konsultasi dengan ID {consultation_id} tidak ditemukan."
        )
    
    profile = consultation.business_profile
    
    return APIResponse(
        success=True,
        message="Detail konsultasi berhasil diambil",
        data={
            "id":                    consultation.id,
            "business_profile": {
                "id":             profile.id,
                "business_name":  profile.business_name,
                "industry":       profile.industry,
                "business_scale": profile.business_scale.value,
                "location":       profile.location,
                "description":    profile.description,
            },
            "problem_statement":     consultation.problem_statement,
            "ai_response_json":      consultation.ai_response_json,
            "ai_model_used":         consultation.ai_model_used,
            "status":                consultation.status.value,
            "processing_time_ms":    consultation.processing_time_ms,
            "error_message":         consultation.error_message,
            "created_at":            consultation.created_at.isoformat(),
        }
    )


# ─── ENDPOINT: Statistik Dashboard ───────────────────────────────────────────
@app.get("/api/stats/", tags=["Dashboard"])
async def get_stats(db: Session = Depends(get_db)):
    """Statistik agregat untuk header dashboard."""
    from sqlalchemy import func
    
    total_consultations = db.query(Consultation).count()
    success_count = db.query(Consultation).filter(
        Consultation.status == ConsultationStatus.SUCCESS
    ).count()
    failed_count = db.query(Consultation).filter(
        Consultation.status == ConsultationStatus.FAILED
    ).count()
    
    # Rata-rata waktu pemrosesan (hanya yang success)
    avg_time = db.query(func.avg(Consultation.processing_time_ms)).filter(
        Consultation.status == ConsultationStatus.SUCCESS
    ).scalar()
    
    return {
        "total_consultations": total_consultations,
        "success_count":       success_count,
        "failed_count":        failed_count,
        "success_rate":        round((success_count / total_consultations * 100), 1) if total_consultations > 0 else 0,
        "avg_processing_ms":   round(avg_time, 0) if avg_time else 0,
    }


# ─── ENDPOINT: Hapus Semua Riwayat Konsultasi ─────────────────────────────
@app.delete("/api/consultations/clear", tags=["Consultations"])
async def clear_consultations(db: Session = Depends(get_db)):
    """Hapus semua riwayat konsultasi dari database."""
    deleted_count = db.query(Consultation).count()

    if deleted_count == 0:
        return APIResponse(
            success=True,
            message="Tidak ada riwayat konsultasi untuk dihapus."
        )

    db.query(Consultation).delete(synchronize_session=False)
    db.commit()

    return APIResponse(
        success=True,
        message=f"Berhasil menghapus {deleted_count} riwayat konsultasi."
    )


# ─── ENDPOINT: Hapus Konsultasi ───────────────────────────────────────────────
@app.delete("/api/consultations/{consultation_id}", tags=["Consultations"])
async def delete_consultation(
    consultation_id: int,
    db: Session = Depends(get_db)
):
    """Hapus satu record konsultasi dari database."""
    consultation = db.query(Consultation).filter(
        Consultation.id == consultation_id
    ).first()
    
    if not consultation:
        raise HTTPException(status_code=404, detail="Konsultasi tidak ditemukan.")
    
    db.delete(consultation)
    db.commit()
    
    return APIResponse(
        success=True,
        message=f"Konsultasi ID {consultation_id} berhasil dihapus."
    )


# ─── Entry Point ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True,       # Auto-reload saat file berubah (development only)
        log_level="info"
    )