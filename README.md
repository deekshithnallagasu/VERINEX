# VERINEX – AI-Based Identity & Document Screening System

**VERINEX** is an enterprise-grade, defensive identity and document screening web application prototype. Designed for compliance officers, forensic fraud analysts, and risk managers, VERINEX provides automated OCR extraction, multi-layer document consistency checks, image quality forensics, explainable AI-assisted risk scoring (Low, Medium, High), and human-in-the-loop case adjudication.

> [!IMPORTANT]
> **Defensive & Ethical Screening Boundary**:
> VERINEX is strictly an identity and document screening, verification, and defensive detection prototype. The system **never** creates, modifies, forges, or assists in producing fake identities or fraudulent documents. All test materials are purely fictional and sample-based. The AI results are clearly designated as **AI-assisted decision support**, and never make absolute accusations or definitive legal determinations.

---

## Key Features & Capabilities

1. **Enterprise Cybersecurity & AI Aesthetic**:
   - Polished dark navy / slate palette (`#060A12`, `#0B1120`, `#15203B`) with electric blue and purple accents.
   - High-contrast typography (Inter & JetBrains Mono), rounded glassmorphism cards, micro-interactions, and accessible contrast.
   - Responsive on Desktop, Tablet, and Mobile.

2. **Operator Authentication & Persona Switcher**:
   - Secure login with JWT authentication, password reveal toggle, "Remember Me", and forgot/reset password modal workflows.
   - Quick 1-click demo persona switcher:
     - **Sarah Chen** (`analyst@verinex.ai` / `Verinex2026!`) – Compliance Analyst
     - **David Vance** (`reviewer@verinex.ai` / `Verinex2026!`) – Senior Reviewer
     - **Alex Mercer** (`admin@verinex.ai` / `Verinex2026!`) – Risk Administrator
   - Security certification badges: SOC2 Type II, ISO 27001, End-to-End Encryption.

3. **Telemetry Dashboard**:
   - 4 Key metric cards: Total Screenings, Verified Documents, Suspicious Documents, and Pending Reviews.
   - Risk Distribution breakdown: Interactive visual ratio of Low, Medium, and High risk cases.
   - Screening Volume chart: Interactive visual chart tracking verified throughput vs flagged documents over time.
   - Recent Screenings table with live search and status filters.

4. **Multi-Stage Document Screening & Sample Gallery**:
   - Drag-and-drop file upload zone (JPG, PNG, WEBP, PDF up to 10MB) with preview.
   - **1-Click Fictional Test Specimen Gallery** (no external files needed to test immediately):
     - *Clean Fictional Passport* (Low Risk – valid dates, matching MRZ lines, high sharpness)
     - *Expired Driver's License* (Medium Risk – past expiration date)
     - *Tampered MRZ National ID* (High Risk – critical discrepancy between visual name and MRZ track)
     - *Degraded Residence Permit* (Medium/High Risk – blur metric below threshold, optical glare)
   - Live 6-stage animated processing stepper:
     1. Upload & Format Validation
     2. Image Quality & Glare Inspection
     3. Optical Character Recognition (OCR)
     4. Structured Data Extraction
     5. Multi-Layer Consistency & Tamper Analysis
     6. AI-Assisted Risk Scoring

5. **AI Screening Assessment**:
   - Risk score gauge (0–100) and overall risk badge (LOW, MEDIUM, HIGH).
   - Telemetry metrics: AI Model Confidence %, Document Quality Score %, OCR Confidence %.
   - Structured Extracted Fields: Full Name, Document Number, DOB, Expiry Date, Authority, Nationality, Address, and Dual-Line MRZ (ICAO 9303).
   - Multi-layer consistency table (Passed / Warning / Failed).
   - Plain-language suspicious indicators list explaining **why** an item was flagged and recommending next actions.
   - Prominent **AI-Assisted Decision Support Notice** banner.

6. **Forensic Case Adjudication & Review**:
   - Side-by-side inspection: Document specimen preview with zoom alongside extracted structured data.
   - Reviewer notes section: Add investigator rationale to an immutable chronological note thread.
   - Complete screening lifecycle timeline (Ingest → Quality Check → OCR → AI Risk → Adjudication).
   - Authoritative actions: *Verify & Approve*, *Flag for Investigation*, *Request Manual Review*, *Reject Document*.

7. **Compliance Reports & Multi-Format Export**:
   - Multi-faceted filterable report explorer (filter by date, document type, risk level, status).
   - Full forensic report preview modal.
   - Direct download and export in **JSON** and **CSV** formats.

8. **Security & Activity Audit Logs**:
   - Append-only compliance audit trail logging user, event action, case ID, timestamp, client IP, and severity.

9. **System Settings & Risk Threshold Tuning**:
   - Configure Low Risk and Medium Risk boundary cutoffs.
   - Session timeout policies (15, 30, 60 minutes).
   - API Key generator and webhook management.
   - Data retention and automated PII redaction policy settings.
   - Simulated session security timeout test button in the top header.

---

## Technology Stack

- **Frontend**: React 18, TypeScript, Tailwind CSS, Lucide React, Vite.
- **Backend**: Python 3.14, FastAPI, SQLAlchemy ORM, Pydantic v2, Pillow (Image Forensics & Sample Generation), PBKDF2-HMAC-SHA256 Security.
- **Database**: SQLite (default zero-config in `backend/data/verinex.db`, configurable to PostgreSQL via `DATABASE_URL`).

---

## Directory Structure

```
verinex/
├── backend/
│   ├── app/
│   │   ├── config.py              # Configuration & path constants
│   │   ├── database.py            # SQLAlchemy engine & session factory
│   │   ├── models.py              # User, ScreeningCase, CaseNote, AuditLog, SystemSetting
│   │   ├── schemas.py             # Pydantic v2 validation models
│   │   ├── services/
│   │   │   ├── quality_service.py # Image resolution, sharpness & glare analyzer
│   │   │   ├── ocr_service.py     # OCR & structured identity parser
│   │   │   ├── risk_engine.py     # Rule-based explainable risk calculation engine
│   │   │   ├── sample_generator.py# Generates 4 high-fidelity fictional document cards
│   │   │   ├── security.py        # PBKDF2-HMAC password hashing & verification
│   │   │   ├── audit_service.py   # Immutable audit log recording
│   │   │   └── seed_data.py       # Auto-seeds database on startup
│   │   ├── routers/
│   │   │   ├── auth.py            # Authentication, registration & password recovery
│   │   │   ├── screenings.py      # Uploads, sample presets, and AI screening execution
│   │   │   ├── cases.py           # Adjudication, status transitions, reviewer notes
│   │   │   ├── reports.py         # Summary statistics, detailed views & JSON/CSV exports
│   │   │   ├── audit.py           # Query audit trail & record client events
│   │   │   ├── stats.py           # Dashboard metrics & activity charts
│   │   │   └── settings.py        # Operational parameters & risk threshold tuning
│   │   └── main.py                # FastAPI app with CORS and lifespan initialization
│   ├── static/
│   │   ├── samples/               # Generated fictional sample document images
│   │   └── uploads/               # User uploaded test documents
│   ├── data/
│   │   └── verinex.db             # Local SQLite database
│   ├── requirements.txt
│   └── run.py                     # Backend server entrypoint (port 8000)
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/            # Navbar, Sidebar, Badge, StatCard, Modal
│   │   ├── context/
│   │   │   └── AuthContext.tsx    # Authentication state & session timeout management
│   │   ├── pages/
│   │   │   ├── LoginPage.tsx      # Sign In, Demo Switcher, Forgot Password
│   │   │   ├── DashboardPage.tsx  # Metrics, risk breakdown, activity chart, recent cases
│   │   │   ├── ScreeningPage.tsx  # Drag & drop upload, sample picker, processing stepper
│   │   │   ├── ScreeningResultPage.tsx # Risk score gauge, OCR fields, flags, AI disclaimer
│   │   │   ├── CaseReviewPage.tsx # Side-by-side inspector, notes thread, decision actions
│   │   │   ├── ReportsPage.tsx    # Multi-filter reports explorer & JSON/CSV export
│   │   │   ├── AuditLogPage.tsx   # Security log stream
│   │   │   └── SettingsPage.tsx   # Risk thresholds, profile, API keys, retention
│   │   ├── services/
│   │   │   ├── api.ts             # REST client communicating with FastAPI
│   │   │   └── types.ts           # Shared TypeScript interfaces
│   │   ├── App.tsx                # Master routing and layout
│   │   └── index.css              # Glassmorphism and cybersecurity utilities
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
└── README.md
```

---

## Installation & Running the Application

### 1. Prerequisites
- Python 3.10+ (Python 3.14 tested)
- Node.js 18+ and npm (Node.js 20 LTS tested)

### 2. Start the Backend Server
```bash
cd backend
python -m pip install -r requirements.txt
python run.py
```
- The backend will automatically create SQLite database tables, generate the 4 fictional test documents in `backend/static/samples/`, and seed initial cases and audit logs.
- API is accessible at: `http://localhost:8000`
- Interactive Swagger documentation: `http://localhost:8000/docs`

### 3. Start the Frontend Server
Open a second terminal window:
```bash
cd frontend
npm install
npm run dev
```
- Open your browser to: `http://localhost:5173`

---

## Step-by-Step Demo Walkthrough

1. **Login**:
   - Navigate to `http://localhost:5173`.
   - Use the **Quick Demo Accounts** buttons (e.g. click **Sarah Chen (Analyst)**) or enter credentials (`analyst` / `Verinex2026!`).
2. **Dashboard Overview**:
   - Observe live metric cards (Total Screenings, Verified, Suspicious, In Review).
   - Review the segmented **Risk Distribution** bar and **Screening Volume** chart.
   - Browse the **Recent Identity Screenings** table.
3. **Launch a Document Screening**:
   - Click **Launch Screening** or navigate to **Document Screening** in the sidebar.
   - Click on the **Fictional National ID (Tampered MRZ)** card in the 1-click sample gallery.
   - Notice the document preview card loading the test specimen image.
   - Click **Start AI Screening Pipeline**.
   - Watch the animated 6-stage workflow stepper execute in real time.
4. **Inspect AI Screening Assessment**:
   - Observe the **HIGH RISK (Score 75-88)** gauge with crimson alert glow.
   - Notice the extracted data fields: Name (*Marcus Reid*), ID Number, DOB, and dual MRZ lines.
   - Review the **Consistency Checks** table: notice that *Visual vs MRZ Name Match* is marked **FAIL**.
   - Read the explainable **Suspicious Indicators** alert: clearly explaining that printed name *Marcus Reid* does not match machine-readable name *JONES DEVON*.
   - Read the prominent **AI-Assisted Decision Support Notice** disclaimer.
   - Click **Open Case Review**.
5. **Adjudicate Case**:
   - Examine the side-by-side visual inspection zone and extracted subject profile.
   - Under **Reviewer Notes & Rationale**, type an investigator observation and click **Record Note**.
   - Click the **Flag** or **Approve** button to record an authoritative decision.
6. **Reports & Export**:
   - Navigate to **Reports & Export** in the sidebar.
   - Search or filter cases by risk or status.
   - Click the eye icon to view the formatted **Forensic Screening Report** modal.
   - Click **Export JSON** or **Export CSV** to download compliance files.
7. **Audit Trail**:
   - Navigate to **Audit / Activity Log** in the sidebar.
   - Verify that your recent login, screening run, reviewer note, and status update are recorded with timestamps, operator name, and IP address.
8. **System Settings & Timeout Simulation**:
   - Navigate to **System Settings** in the sidebar.
   - Adjust the **Risk Engine Sensitivity Thresholds** (Low and Medium risk boundaries).
   - In the top navigation bar, click the **Test Timeout** button to simulate the compliance session timeout modal.
   - Click **Re-Authenticate Session** to return smoothly to the Login page.

---

## Defensive Security Architecture & Integrity Guarantees

- **No Synthesis / Forgery Pipeline**: All OCR and screening models in VERINEX are built strictly as passive ingestion parsers. The platform lacks any text overlay generation or counterfeit generation capabilities.
- **Audit Immutability**: All decisions and configuration changes are recorded into the `audit_logs` table.
- **Explainability**: Rather than providing a black-box probability, the risk engine produces human-readable diagnostic reasons and recommendations for compliance officers.
