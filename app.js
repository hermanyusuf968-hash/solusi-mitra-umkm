// ============================================================
// app.js — Solusi Mitra UMKM
// SPA ringan tanpa framework: hash-router + fetch ke FastAPI.
// ============================================================

const BACKEND_URL = (() => {
  // Otomatis pakai host yang sama jika di-deploy, fallback ke localhost:8000 untuk dev.
  if (window.__BACKEND_URL__) return window.__BACKEND_URL__;
  return "http://localhost:8000";
})();

const state = {
  page: 1,
  statusFilter: "",
  lastConsultation: null,
};

// ============================================================
// UTIL
// ============================================================
function qs(sel, root = document) { return root.querySelector(sel); }
function qsa(sel, root = document) { return Array.from(root.querySelectorAll(sel)); }

function escapeHtml(str) {
  if (str === null || str === undefined) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function formatDate(iso) {
  if (!iso) return "-";
  try {
    const d = new Date(iso);
    return d.toLocaleDateString("id-ID", { day: "2-digit", month: "short", year: "numeric" }) +
      ", " + d.toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit" });
  } catch { return iso; }
}

function priorityTag(p) {
  const v = (p || "").toLowerCase();
  if (v.includes("tinggi") || v.includes("high")) return "tag-tinggi";
  if (v.includes("sedang") || v.includes("medium")) return "tag-sedang";
  return "tag-rendah";
}

function statusLabel(s) {
  return { success: "Selesai", failed: "Gagal", pending: "Diproses" }[s] || s;
}

async function api(path, opts = {}) {
  const res = await fetch(`${BACKEND_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try { const j = await res.json(); detail = j.detail || detail; } catch {}
    const err = new Error(detail);
    err.status = res.status;
    throw err;
  }
  return res.json();
}

// ============================================================
// TOAST
// ============================================================
function toast(msg, type = "info", ttl = 4200) {
  const stack = qs("#toast-stack");
  const el = document.createElement("div");
  el.className = `toast ${type === "error" ? "toast-error" : type === "success" ? "toast-success" : ""}`;
  el.textContent = msg;
  stack.appendChild(el);
  setTimeout(() => {
    el.classList.add("is-leaving");
    setTimeout(() => el.remove(), 320);
  }, ttl);
}

// ============================================================
// TOP PROGRESS BAR (indikator navigasi/fetch)
// ============================================================
const progressBar = qs("#route-progress");
let progressTimer = null;
function progressStart() {
  clearTimeout(progressTimer);
  progressBar.classList.remove("is-done");
  progressBar.style.width = "0%";
  requestAnimationFrame(() => {
    progressBar.classList.add("is-active");
    progressBar.style.width = "78%";
  });
}
function progressDone() {
  progressBar.classList.remove("is-active");
  progressBar.classList.add("is-done");
  progressBar.style.width = "100%";
  progressTimer = setTimeout(() => { progressBar.style.width = "0%"; }, 350);
}

// ============================================================
// SCROLL REVEAL
// ============================================================
const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add("is-visible"); });
}, { threshold: 0.15 });

function observeReveals(root = document) {
  qsa(".reveal", root).forEach(el => revealObserver.observe(el));
}

// ============================================================
// BACKEND HEALTH CHECK
// ============================================================
async function checkHealth() {
  const navStatus = qs("#nav-status");
  const footerStatus = qs("#footer-status");
  try {
    await api("/health");
    navStatus.classList.add("is-ok");
    navStatus.classList.remove("is-down");
    navStatus.querySelector(".label").textContent = "Sistem Aktif";
    footerStatus.textContent = "Sistem aktif dan siap digunakan";
    return true;
  } catch {
    navStatus.classList.add("is-down");
    navStatus.classList.remove("is-ok");
    navStatus.querySelector(".label").textContent = "Server Tidak Aktif";
    footerStatus.textContent = `Tidak terhubung ke ${BACKEND_URL}`;
    return false;
  }
}

async function loadHeroStats() {
  try {
    const s = await api("/api/stats/");
    qs("#stat-total").textContent = s.total_consultations ?? "0";
    qs("#stat-rate").textContent = `${s.success_rate ?? 0}%`;
    qs("#stat-time").textContent = `${Math.round((s.avg_processing_ms ?? 0) / 1000)}s`;
  } catch {
    qs("#stat-total").textContent = "—";
    qs("#stat-rate").textContent = "—";
    qs("#stat-time").textContent = "—";
  }
}

// ============================================================
// ROUTER
// ============================================================
const routes = {
  "/": "home",
  "/konsultasi": "konsultasi",
  "/riwayat": "riwayat",
  "/detail": "detail",
};

function currentRoute() {
  const hash = window.location.hash.replace(/^#/, "") || "/";
  return hash.split("?")[0];
}

function setActiveNav(route) {
  qsa(".nav-link").forEach(a => {
    a.classList.toggle("is-active", a.dataset.route === route);
  });
}

function showView(viewName) {
  qsa(".view").forEach(v => v.classList.remove("is-active"));
  const target = qs(`.view[data-view="${viewName}"]`);
  if (target) target.classList.add("is-active");
  window.scrollTo({ top: 0, behavior: "instant" in window ? "instant" : "auto" });
  observeReveals(target || document);
}

async function router() {
  progressStart();
  const route = currentRoute();
  const viewName = routes[route] || "home";
  setActiveNav(route);
  showView(viewName);
  qs("#nav-links").classList.remove("is-open");

  if (viewName === "home") {
    await loadHeroStats();
  } else if (viewName === "konsultasi") {
    resetConsultationView();
  } else if (viewName === "riwayat") {
    await loadDashboard();
  } else if (viewName === "detail") {
    const params = new URLSearchParams(window.location.hash.split("?")[1] || "");
    await loadDetail(params.get("id"));
  }

  progressDone();
}

window.addEventListener("hashchange", router);

document.addEventListener("click", (e) => {
  const link = e.target.closest("[data-link]");
  if (link) {
    // let default hash navigation happen; just close mobile menu
    qs("#nav-links").classList.remove("is-open");
  }
});

qs("#nav-burger").addEventListener("click", () => {
  qs("#nav-links").classList.toggle("is-open");
});

// ============================================================
// VIEW: KONSULTASI BARU
// ============================================================
function resetConsultationView() {
  qs("#konsultasi-form-wrap").style.display = "";
  qs("#processing-card").style.display = "none";
  qs("#result-wrap").style.display = "none";
  qs("#result-wrap").innerHTML = "";
}

const problemField = qs("#f-problem");
const charCountEl = qs("#char-count");
problemField.addEventListener("input", () => {
  charCountEl.textContent = problemField.value.trim().length;
});

function clearFieldErrors() {
  qsa(".field[data-field]").forEach(f => f.classList.remove("has-error"));
}

function setFieldError(name) {
  const f = qs(`.field[data-field="${name}"]`);
  if (f) f.classList.add("has-error");
}

function validateForm() {
  clearFieldErrors();
  const businessName = qs("#f-business-name").value.trim();
  const industry = qs("#f-industry").value.trim();
  const location = qs("#f-location").value.trim();
  const problem = qs("#f-problem").value.trim();

  let errors = [];
  if (!businessName) { setFieldError("business_name"); errors.push("Nama bisnis wajib diisi."); }
  if (!industry) { setFieldError("industry"); errors.push("Industri wajib diisi."); }
  if (!location) { setFieldError("location"); errors.push("Lokasi wajib diisi."); }
  if (!problem || problem.length < 20) { setFieldError("problem_statement"); errors.push("Uraian masalah minimal 20 karakter."); }

  return { valid: errors.length === 0, errors };
}

qs("#consultation-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const { valid, errors } = validateForm();
  if (!valid) {
    toast(errors[0], "error");
    const firstError = qs(".field.has-error");
    if (firstError) firstError.scrollIntoView({ behavior: "smooth", block: "center" });
    return;
  }

  const payload = {
    user_name: qs("#f-name").value.trim() || null,
    user_email: qs("#f-email").value.trim() || null,
    business_name: qs("#f-business-name").value.trim(),
    industry: qs("#f-industry").value.trim(),
    business_scale: qs("#f-scale").value,
    location: qs("#f-location").value.trim(),
    business_description: qs("#f-desc").value.trim() || null,
    problem_statement: qs("#f-problem").value.trim(),
  };

  await runConsultation(payload);
});

async function runConsultation(payload) {
  qs("#konsultasi-form-wrap").style.display = "none";
  qs("#result-wrap").style.display = "none";
  const card = qs("#processing-card");
  card.style.display = "";
  const stepEl = qs("#processing-step");
  const fillEl = qs("#processing-fill");

  const steps = [
    [10, "Memvalidasi data profil bisnis…"],
    [28, "Menganalisis skala dan sektor industri…"],
    [50, "Menelaah dan memproses uraian masalah…"],
    [72, "Menyusun rekomendasi dan rencana tindak lanjut… (estimasi 10–30 detik)"],
  ];

  let cancelled = false;
  (async () => {
    for (const [pct, msg] of steps) {
      if (cancelled) return;
      fillEl.style.width = pct + "%";
      stepEl.textContent = msg;
      await new Promise(r => setTimeout(r, 650));
    }
  })();

  try {
    const result = await api("/api/consultations/", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    cancelled = true;
    fillEl.style.width = "100%";
    stepEl.textContent = "Selesai.";

    if (result.success && result.data) {
      state.lastConsultation = result.data;
      await new Promise(r => setTimeout(r, 300));
      card.style.display = "none";
      renderResult(result.data, payload);
      toast("Analisis konsultasi berhasil diselesaikan.", "success");
    } else {
      throw new Error("Respons tidak valid dari server.");
    }
  } catch (err) {
    cancelled = true;
    card.style.display = "none";
    qs("#konsultasi-form-wrap").style.display = "";
    const msg = err.message?.includes("Failed to fetch")
      ? `Tidak dapat terhubung ke server backend di ${BACKEND_URL}. Pastikan FastAPI sedang berjalan (uvicorn backend:app --reload).`
      : err.message;
    toast(msg, "error", 6500);
  }
}

function renderResult(data, payload) {
  const wrap = qs("#result-wrap");
  wrap.style.display = "";
  const ai = data.ai_response_json || {};
  const processingSec = Math.round((data.processing_time_ms || 0) / 100) / 10;

  wrap.innerHTML = `
    <div class="result-banner">✓ Analisis selesai dalam ${processingSec} detik.</div>

    <div class="page-head" style="margin-bottom:24px;">
      <div class="eyebrow">Hasil Analisis Konsultasi</div>
      <h1 style="font-size:1.5rem;">${escapeHtml(payload.business_name)}</h1>
      <p>${escapeHtml(payload.industry)} · ${escapeHtml(payload.location)} · ${escapeHtml(payload.business_scale)}</p>
    </div>

    <div class="section-label">Ringkasan Analisis Masalah</div>
    <div class="info-box">${escapeHtml(ai.ringkasan_masalah)}</div>

    <div class="panel-grid" style="margin-top:24px;">
      <div>
        <div class="section-label" style="margin-top:0;">Identifikasi Akar Masalah</div>
        <div class="panel"><ul>${(ai.analisis_akar_masalah || []).map(i => `<li>${escapeHtml(i)}</li>`).join("")}</ul></div>
      </div>
      <div>
        <div class="section-label" style="margin-top:0;">Rekomendasi Solusi Utama</div>
        <div class="panel accent-azure"><p>${escapeHtml(ai.solusi_utama)}</p></div>
      </div>
    </div>

    <div class="section-label">Rencana Tindak Lanjut</div>
    <div class="steps">
      ${(ai.langkah_aksi || []).map(step => `
        <div class="step-card">
          <div class="step-num">${escapeHtml(step.langkah)}</div>
          <div class="step-body">
            <h4>${escapeHtml(step.judul)}</h4>
            <p>${escapeHtml(step.deskripsi)}</p>
            <div class="step-tags">
              <span class="tag ${priorityTag(step.prioritas)}">${escapeHtml(step.prioritas)}</span>
              <span class="tag tag-time">${escapeHtml(step.timeline)}</span>
            </div>
          </div>
        </div>
      `).join("")}
    </div>

    <div class="panel-grid" style="margin-top:24px;">
      <div>
        <div class="section-label" style="margin-top:0;">Estimasi Dampak Bisnis</div>
        <div class="panel"><p>${escapeHtml(ai.estimasi_dampak)}</p></div>
        <div class="section-label">Risiko dan Mitigasi</div>
        <div class="panel"><ul>${(ai.risiko_dan_mitigasi || []).map(i => `<li>${escapeHtml(i)}</li>`).join("")}</ul></div>
      </div>
      <div>
        <div class="section-label" style="margin-top:0;">Sumber Daya yang Dibutuhkan</div>
        <div class="panel"><ul>${(ai.sumber_daya_dibutuhkan || []).map(i => `<li>${escapeHtml(i)}</li>`).join("")}</ul></div>
        <div class="section-label">Indikator Kinerja (KPI)</div>
        <div class="panel"><ul>${(ai.kpi_saran || []).map(i => `<li>${escapeHtml(i)}</li>`).join("")}</ul></div>
      </div>
    </div>

    <div class="section-label">Catatan dari Tim Konsultan</div>
    <div class="info-box">${escapeHtml(ai.catatan_konsultan)}</div>

    <div class="result-actions">
      <a class="btn btn-ghost" data-link href="#/riwayat">Lihat Riwayat Konsultasi</a>
      <button class="btn btn-primary" id="btn-new-consultation">Ajukan Konsultasi Baru</button>
    </div>
  `;

  qs("#btn-new-consultation").addEventListener("click", () => {
    qs("#consultation-form").reset();
    charCountEl.textContent = "0";
    resetConsultationView();
    window.scrollTo({ top: 0, behavior: "smooth" });
  });

  wrap.scrollIntoView({ behavior: "smooth", block: "start" });
}

// ============================================================
// VIEW: RIWAYAT / DASHBOARD
// ============================================================
async function loadDashboard() {
  await Promise.all([loadDashStats(), loadConsultList()]);
}

async function loadDashStats() {
  const wrap = qs("#dash-stats");
  try {
    const s = await api("/api/stats/");
    wrap.innerHTML = `
      <div class="stat-card c-gold"><div class="stat-value">${s.total_consultations ?? 0}</div><div class="stat-label">Total Konsultasi</div></div>
      <div class="stat-card c-ok"><div class="stat-value">${s.success_count ?? 0}</div><div class="stat-label">Berhasil Diproses</div></div>
      <div class="stat-card c-azure"><div class="stat-value">${s.success_rate ?? 0}%</div><div class="stat-label">Tingkat Keberhasilan</div></div>
      <div class="stat-card c-mix"><div class="stat-value">${Math.round((s.avg_processing_ms ?? 0) / 1000)}s</div><div class="stat-label">Rata-rata Waktu Analisis</div></div>
    `;
  } catch {
    wrap.innerHTML = `<div class="alert alert-error" style="grid-column:1/-1;">Gagal memuat statistik dashboard.</div>`;
  }
}

qs("#status-filter").addEventListener("change", (e) => {
  state.statusFilter = e.target.value;
  state.page = 1;
  loadConsultList();
});

qs("#refresh-btn").addEventListener("click", () => loadDashboard());

async function loadConsultList() {
  const listEl = qs("#consult-list");
  const countEl = qs("#dash-result-count");
  const pagEl = qs("#pagination");
  listEl.innerHTML = `<div class="skeleton skel-card"></div><div class="skeleton skel-card"></div><div class="skeleton skel-card"></div>`;
  countEl.textContent = "";
  pagEl.innerHTML = "";

  try {
    const params = new URLSearchParams({ page: state.page, per_page: 8 });
    if (state.statusFilter) params.set("status", state.statusFilter);
    const res = await api(`/api/consultations/?${params.toString()}`);

    if (!res.success) throw new Error("Gagal memuat riwayat konsultasi.");

    const { items, total, total_pages } = res.data;

    if (!items.length) {
      listEl.innerHTML = `
        <div class="empty-state">
          <div class="icon-wrap">
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none"><path d="M4 19V5a1 1 0 0 1 1-1h11l4 4v11a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1Z" stroke="currentColor" stroke-width="1.4"/></svg>
          </div>
          <h3>Belum ada riwayat konsultasi</h3>
          <p>Mulai konsultasi pertama Anda untuk melihatnya di sini.</p>
          <a class="btn btn-primary" data-link href="#/konsultasi">Mulai Konsultasi</a>
        </div>`;
      return;
    }

    countEl.textContent = `Menampilkan ${items.length} dari ${total} konsultasi`;

    listEl.innerHTML = items.map(item => {
      const preview = (item.problem_statement || "").slice(0, 160);
      const sec = item.processing_time_ms ? Math.round(item.processing_time_ms / 100) / 10 : "-";
      return `
        <div class="consult-card" data-id="${item.id}">
          <div class="consult-top">
            <div><span class="consult-name">${escapeHtml(item.business_name)}</span><span class="consult-industry">${escapeHtml(item.industry)}</span></div>
            <div class="consult-meta-right">
              <span class="status-badge status-${item.status}">${statusLabel(item.status)}</span>
              <span class="consult-date">${formatDate(item.created_at)}</span>
            </div>
          </div>
          <div class="consult-preview">${escapeHtml(preview)}${preview.length === 160 ? "…" : ""}</div>
          <div class="consult-meta">${escapeHtml(item.location)} &bull; ${escapeHtml(item.business_scale)} &bull; Durasi analisis: ${sec}s</div>
        </div>`;
    }).join("");

    qsa(".consult-card", listEl).forEach(card => {
      card.addEventListener("click", () => {
        window.location.hash = `#/detail?id=${card.dataset.id}`;
      });
    });

    if (total_pages > 1) {
      let html = "";
      for (let i = 1; i <= total_pages; i++) {
        html += `<button class="page-btn ${i === state.page ? "is-active" : ""}" data-page="${i}">${i}</button>`;
      }
      pagEl.innerHTML = html;
      qsa(".page-btn", pagEl).forEach(btn => {
        btn.addEventListener("click", () => {
          state.page = parseInt(btn.dataset.page, 10);
          loadConsultList();
          window.scrollTo({ top: 0, behavior: "smooth" });
        });
      });
    }
  } catch (err) {
    const down = err.message?.includes("Failed to fetch");
    listEl.innerHTML = `<div class="alert alert-error">${
      down
        ? `Tidak dapat terhubung ke server backend di ${BACKEND_URL}. Pastikan server FastAPI sudah berjalan.`
        : escapeHtml(err.message)
    }</div>`;
  }
}

// ============================================================
// VIEW: DETAIL
// ============================================================
qs("#back-to-riwayat").addEventListener("click", () => {
  window.location.hash = "#/riwayat";
});

async function loadDetail(id) {
  const content = qs("#detail-content");
  if (!id) {
    content.innerHTML = `<div class="alert alert-warn">Tidak ada konsultasi yang dipilih.</div>`;
    return;
  }
  content.innerHTML = `<div class="skeleton" style="height:90px; margin-bottom:28px;"></div><div class="skeleton" style="height:240px;"></div>`;

  try {
    const res = await api(`/api/consultations/${id}`);
    if (!res.success) throw new Error("Data konsultasi tidak ditemukan.");
    const data = res.data;
    const profile = data.business_profile || {};
    const sec = data.processing_time_ms ? Math.round(data.processing_time_ms / 100) / 10 : "-";

    let bodyHtml = "";
    if (data.status === "success" && data.ai_response_json) {
      const ai = data.ai_response_json;
      bodyHtml = `
        <div class="section-label" style="margin-top:0;">Hasil Analisis dan Rekomendasi</div>
        <p style="color:var(--text-soft); font-size:0.82rem; margin-top:-6px;">Data ini dimuat langsung dari basis data tanpa memproses ulang.</p>
        <div class="info-box">${escapeHtml(ai.ringkasan_masalah)}</div>

        <div class="panel-grid" style="margin-top:20px;">
          <div>
            <div class="section-label" style="margin-top:0;">Identifikasi Akar Masalah</div>
            <div class="panel"><ul>${(ai.analisis_akar_masalah || []).map(i => `<li>${escapeHtml(i)}</li>`).join("")}</ul></div>
          </div>
          <div>
            <div class="section-label" style="margin-top:0;">Rekomendasi Solusi Utama</div>
            <div class="panel accent-azure"><p>${escapeHtml(ai.solusi_utama)}</p></div>
          </div>
        </div>

        <div class="section-label">Rencana Tindak Lanjut</div>
        <div class="steps">
          ${(ai.langkah_aksi || []).map(step => `
            <div class="step-card">
              <div class="step-num">${escapeHtml(step.langkah)}</div>
              <div class="step-body">
                <h4>${escapeHtml(step.judul)}</h4>
                <p>${escapeHtml(step.deskripsi)}</p>
                <div class="step-tags">
                  <span class="tag ${priorityTag(step.prioritas)}">${escapeHtml(step.prioritas)}</span>
                  <span class="tag tag-time">${escapeHtml(step.timeline)}</span>
                </div>
              </div>
            </div>
          `).join("")}
        </div>

        <div class="panel-grid" style="margin-top:24px;">
          <div>
            <div class="section-label" style="margin-top:0;">Estimasi Dampak Bisnis</div>
            <div class="panel"><p>${escapeHtml(ai.estimasi_dampak)}</p></div>
            <div class="section-label">Risiko dan Mitigasi</div>
            <div class="panel"><ul>${(ai.risiko_dan_mitigasi || []).map(i => `<li>${escapeHtml(i)}</li>`).join("")}</ul></div>
          </div>
          <div>
            <div class="section-label" style="margin-top:0;">Sumber Daya yang Dibutuhkan</div>
            <div class="panel"><ul>${(ai.sumber_daya_dibutuhkan || []).map(i => `<li>${escapeHtml(i)}</li>`).join("")}</ul></div>
            <div class="section-label">Indikator Kinerja (KPI)</div>
            <div class="panel"><ul>${(ai.kpi_saran || []).map(i => `<li>${escapeHtml(i)}</li>`).join("")}</ul></div>
          </div>
        </div>

        <div class="section-label">Catatan dari Tim Konsultan</div>
        <div class="info-box">${escapeHtml(ai.catatan_konsultan)}</div>
      `;
    } else if (data.status === "failed") {
      bodyHtml = `<div class="alert alert-error"><strong>Konsultasi ini gagal diproses.</strong><br>Detail: ${escapeHtml(data.error_message || "Tidak ada informasi error.")}</div>`;
    } else {
      bodyHtml = `<div class="alert alert-warn">Konsultasi masih dalam proses atau data hasil analisis belum tersedia.</div>`;
    }

    content.innerHTML = `
      <div class="page-head">
        <div class="eyebrow">Konsultasi #${data.id}</div>
        <h1 style="font-size:1.5rem;">${escapeHtml(profile.business_name)}</h1>
        <p>${escapeHtml(profile.industry)} · ${escapeHtml(profile.location)}</p>
      </div>

      <div class="detail-meta-row">
        <div><div class="meta-key">Skala Bisnis</div><div class="meta-val">${escapeHtml(profile.business_scale)}</div></div>
        <div><div class="meta-key">Status</div><div class="meta-val"><span class="status-badge status-${data.status}">${statusLabel(data.status)}</span></div></div>
        <div><div class="meta-key">Durasi Analisis</div><div class="meta-val mono">${sec}s</div></div>
        <div><div class="meta-key">Tanggal</div><div class="meta-val">${formatDate(data.created_at)}</div></div>
      </div>

      <div class="section-label" style="margin-top:0;">Uraian Masalah yang Dikonsultasikan</div>
      <div class="info-box">${escapeHtml(data.problem_statement)}</div>

      <div style="height:1px; background:var(--ink-border-soft); margin:28px 0;"></div>

      ${bodyHtml}
    `;
  } catch (err) {
    content.innerHTML = `<div class="alert alert-error">Gagal memuat detail: ${escapeHtml(err.message)}</div>`;
  }
}

// ============================================================
// INIT
// ============================================================
function initSplash() {
  window.addEventListener("load", () => {
    setTimeout(() => qs("#splash").classList.add("is-hidden"), 280);
  });
  // fallback jika 'load' lambat/sudah lewat
  setTimeout(() => qs("#splash").classList.add("is-hidden"), 1800);
}

qs("#year").textContent = new Date().getFullYear();

initSplash();
checkHealth();
setInterval(checkHealth, 30000);
router();
