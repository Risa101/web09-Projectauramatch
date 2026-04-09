# CLAUDE.md




This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AuraMatch is a full-stack AI-powered beauty/cosmetics recommendation platform. It analyzes facial structure and personal color to recommend makeup products. Features include face shape detection, skin tone/undertone analysis, personal color season classification (Spring/Summer/Autumn/Winter), AI chat via Gemini, and a photo editor.

## Tech Stack

- **Frontend**: React 19 + Vite 8, Tailwind CSS 4, React Router DOM 7, Axios, plain JavaScript (no TypeScript)
- **Backend**: Python FastAPI, SQLAlchemy 2.0 ORM, MySQL (PyMySQL driver)
- **AI/ML**: OpenCV, MediaPipe (face detection), dlib (face landmarks), TensorFlow/Keras (face shape CNN), Google Generative AI (Gemini), colour-science (CIELAB/CIEDE2000)
- **RAG Pipeline**: ChromaDB (vector store) + `paraphrase-multilingual-MiniLM-L12-v2` (embeddings) + Gemini (generation)
- **Caching**: Redis (optional, graceful fallback)
- **Auth**: JWT (python-jose) with bcrypt password hashing

## Development Commands

### Frontend (`frontendauramatchnewversion/`)
```bash
npm run dev        # Dev server on port 5175
npm run build      # Production build to dist/
npm run lint       # ESLint
npm run preview    # Preview production build
```

### Backend (`backendauramatchnewversion/`)
```bash
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8001
python3 -m pytest tests/ -v                              # Run all tests
python3 -m pytest tests/test_color_analysis_service.py -v # Color science tests (67)
python3 -m pytest tests/test_face_shape_decision_tree.py -v # Face shape threshold tests (39)
```

### Database
```bash
# MySQL database name: auramatchnewversion
# Schema: auramatch.sql (root of repo)
# Seed data: seed_makeup_products.sql, seed_personal_color.sql
# Seed 12-season palettes: python scripts/seed_color_palettes.py
```

Backend requires a `.env` file — see `.env.example` for required variables (DB credentials, SECRET_KEY, GEMINI_API_KEY).

## Architecture

**Monorepo with two independent apps:**
- `frontendauramatchnewversion/` — React SPA (Vite)
- `backendauramatchnewversion/` — FastAPI REST API

**API Proxy**: Vite dev server proxies `/api/*` requests to `http://localhost:8001`, stripping the `/api` prefix. In frontend code, API calls go through the Axios instance at `src/api/axios.js` which prepends `/api` and injects the JWT Bearer token via interceptor.

**Backend structure follows MVC pattern:**
- `models/` — SQLAlchemy ORM models (declarative base). Uses enum fields for categorical data (face_shape, personal_color, season) and JSON columns for color palettes.
- `routes/` — FastAPI APIRouter modules, each prefixed (e.g., `/auth`, `/analysis`, `/products`). Auth-protected routes use `get_current_user` dependency.
- `services/` — Business logic layer. `ai_service.py` orchestrates the single-pass face analysis pipeline, `color_analysis_service.py` handles CIELAB color science and CIEDE2000 matching, `recommendation_service.py` handles product matching, `gemini_service.py` wraps the Gemini API, `rag_service.py` orchestrates the RAG pipeline (retrieval → context building → generation), `scoring_service.py` implements S1–S6 multi-signal scoring, `cache_service.py` provides Redis caching with graceful fallback.
- `config/database.py` — SQLAlchemy engine and session setup.
- `config/chromadb_config.py` — ChromaDB singleton with lazy init and graceful fallback.
- `config/redis_config.py` — Redis connection singleton with graceful fallback.

**Frontend structure:**
- `src/pages/` — Route-level page components
- `src/components/` — Shared components (Navbar)
- `src/context/AuthContext.jsx` — Auth state via React Context API (stores JWT in localStorage)
- `src/api/axios.js` — Configured Axios instance with auth interceptor
- `src/services/tracker.js` — User behavior analytics

**Routes** (defined in `src/App.jsx`): `/` (Home), `/login`, `/register`, `/analyze`, `/products`, `/gemini`, `/editor`, `/profile`, `/admin`, `/blog`, `/blog/:slug`

## Face Analysis Pipeline (Single-Pass Architecture)

`analyze_face()` in `ai_service.py` runs one MediaPipe FaceMesh session via `_run_facemesh()`, which returns landmarks (468 points), a face bounding box, and a face crop. This data is reused for both face shape detection and skin extraction — never initialize FaceMesh twice per call.

**Face shape detection** (`detect_face_shape()`) has two paths:
1. **CNN path** (primary): Uses the face crop from `_run_facemesh()` with the model at `models_ai/face_shape_cnn.h5`. Produces all 7 shapes including triangle.
2. **Geometry fallback**: When CNN is unavailable, uses MediaPipe landmark ratios. Produces 6 of 7 shapes (triangle is CNN-only).

**Geometry decision tree thresholds** — derived from Farkas (1994) facial anthropometry, locked by `tests/test_face_shape_decision_tree.py`:

References:
- Farkas, L. G. (1994). *Anthropometry of the Head and Face* (2nd ed.). Raven Press.
- Farkas, L. G., et al. (1985). Vertical and horizontal proportions of the face. *Plast Reconstr Surg*, 75(3), 328-338.

Farkas normative data: total facial index mean 1.28 (SD ~0.06), mandibular-bizygomatic mean 0.71 (SD ~0.04), frontal-bizygomatic mean 0.87 (SD ~0.03).

```
ratio = face_height / cheekbone_width    (landmarks: 152↔10 / 234↔454)
jaw_ratio = jaw_width / cheekbone_width  (landmarks: 172↔397 / 234↔454)
temple_ratio = temple_width / cheekbone  (landmarks: 127↔356 / 234↔454)

ratio > 1.45                          → oblong  (hyperleptoprosopic)
1.30 < ratio ≤ 1.45:
  jaw_ratio < 0.70                    → heart
  temple_ratio < 0.82                 → diamond
  else                                → oval    (leptoprosopic)
1.15 < ratio ≤ 1.30:
  jaw_ratio > 0.85                    → square
  jaw_ratio < 0.70                    → heart
  temple_ratio < 0.82                 → diamond
  else                                → oval    (mesoprosopic)
ratio ≤ 1.15:
  jaw_ratio > 0.85                    → square
  else                                → round   (euryprosopic)
no face detected                      → oval (default)
```
If you change these thresholds, update `tests/test_face_shape_decision_tree.py` (39 characterization tests).

**Landmarks persistence**: Landmark coordinates must be converted to tuples before exiting the MediaPipe context manager, as the underlying data becomes invalid after the context exits.

**Skin extraction** uses the face bounding box to sample the cheek region (`extract_skin_lab_from_bbox()` in `color_analysis_service.py`) instead of a naive center-crop. Falls back to `extract_skin_lab()` when no face is detected. Uses K-Means Clustering (6 clusters) to extract the representative skin color from the cheek region, filtering out outlier pixels (L\* < 20 or > 95).

**Enriched API response**: `POST /analysis/` returns analysis results, palette data, face shape tips, and product recommendations in a single response. The frontend uses this with a fallback to separate `/recommendations/` calls. `generate_recs_for_analysis()` in `routes/recommendations.py` is the shared function used by both paths.

## Key Patterns

- All backend routes are registered in `main.py` via `app.include_router()`
- `Base.metadata.create_all(bind=engine)` auto-creates tables on startup
- CORS is configured for local dev ports: 5173, 5175, 5177, 3000
- File uploads go to `uploads/` directory, served as static files at `/uploads`
- `personal_color` enum stays at 4 seasons (spring/summer/autumn/winter) for backward compatibility; 12-sub-season detail is accessed via `palette_id → ColorPalette.sub_type`

## Product Similarity Search (ChromaDB)

The `GET /products/similar/{product_id}` endpoint uses ChromaDB vector search with `paraphrase-multilingual-MiniLM-L12-v2` embeddings for Thai+English semantic similarity. Falls back to TF-IDF (in `services/tfidf_fallback.py`) if ChromaDB is unavailable.

- **Config**: `config/chromadb_config.py` (mirrors `redis_config.py` pattern — singleton, lazy init, graceful fallback)
- **Embeddings**: `services/embedding_service.py` (lazy model loading, `build_product_document()` for document construction)
- **Search**: `services/recommendation_service.py` (ChromaDB query + TF-IDF fallback)
- **Seeding**: `python scripts/seed_chromadb.py` (re-run after adding/editing products)
- **Storage**: `data/chroma/` (local persistent, gitignored)

This is separate from the S1–S6 scoring engine in `services/scoring_service.py`.

## Multi-Signal Scoring Engine (S1–S6)

Product recommendations are ranked by a weighted composite score from 6 signals. Any changes to scoring logic must preserve these signal definitions and ranges:

| Signal | Range | Description |
|--------|-------|-------------|
| **S1** | 0–300 | **Rule Match Priority** — base priority from rule-based matching |
| **S2** | 0–300 | **CIEDE2000 Proximity** — closeness of product color to the best-match palette color |
| **S3** | 0–150 | **Seasonal Match** — bonus for matching the user's personal color season |
| **S4** | -100–0 | **Avoid-Color Penalty** — deduction when a product color is close to an avoid-color (via CIEDE2000) |
| **S5** | 0–100 | **Feedback Aggregation** — score from user satisfaction (like/dislike ratio) |
| **S6** | 0–50 | **Popularity** — score from favorites count |

Implementation lives in `services/scoring_service.py`. Tests: `tests/test_scoring_service.py`.

## Color Science Rules (MANDATORY)

These rules are non-negotiable for any code touching skin tone analysis or personal color matching:

1. **Always use CIELAB (L\*a\*b\*) color space** for skin tone extraction and comparison. Never use raw RGB values for color analysis — RGB is device-dependent and perceptually non-uniform.
2. **Use CIEDE2000 (ΔE00) formula** for all color distance calculations. Do not use CIE76 or CIE94 — CIEDE2000 is the current standard with blue-region correction and perceptual accuracy. Reference: Sharma, G., Wu, W., & Dalal, E. N. (2005). *Color Research & Application*, 30(1), 21-30.
3. **Skin tone classification uses ITA (Individual Typology Angle)**: `ITA = arctan((L* - 50) / b*) × 180/π`. Thresholds: >55° fair, >41° light, >28° medium, >10° tan, >-30° dark, ≤-30° deep. Reference: Chardon, A., et al. (1991). *Int J Cosmet Sci*, 13(4), 191-208; Del Bino, S. & Bernerd, F. (2013). *Br J Dermatol*, 169(s3), 33-40. The function signature is `classify_tone_from_lab(L, b)` — both L\* and b\* are required.
4. **Undertone classification uses CIELAB hue angle**: `h_ab = atan2(b*, a*)` in degrees. Thresholds: >65° warm, <50° cool, 50-65° neutral. NEVER use raw a\*/b\* threshold logic (e.g., `if a* > X`) — always compute the hue angle first. Reference: Xiao, K., et al. (2017). *Skin Res Technol*, 23(1), 21-29; Ly, B. C. K., et al. (2020). *J Invest Dermatol*, 140(1), 3-12.
5. **Season matching must use Delta E distance** against `color_palettes.best_colors.skin_reference` centroids. Do not use hardcoded lookup dicts for personal color assignment.
6. **All color palette reference data must be stored in CIELAB** with `{"L", "a", "b"}` format in the `color_palettes` JSON columns.
7. **The `colour-science` library** (`import colour`) is the canonical dependency for color space conversions and CIEDE2000 calculations. RGB→CIELAB conversion path: `sRGB → XYZ (D65) → L*a*b*`.
8. **Legacy fallback**: `get_personal_color()` in `ai_service.py` retains the old lookup dict as a fallback when palette data or db session is unavailable. New code should always pass `skin_lab` and `db_session` to use the CIEDE2000 path.

## Product Comparison Rules

These rules govern the product comparison feature (`POST /recommendations/compare` endpoint + compare table modal in `Products.jsx`):

1. **Maximum 3 products** per comparison. The backend validates via Pydantic (`CompareRequest.product_ids` limited to 1–3 items) and the frontend caps `compareList` at 3.
2. **Color Match % uses S2 and S4 signals**: `match_pct = clamp((S2 + S4) / 300 × 100, 0, 100)`. S2 is CIEDE2000 color proximity (0–300), S4 is avoid-color penalty (−100–0). Do not use the composite final score or any other signals for the match percentage.
3. **All comparison UI labels must be in Thai**. Labels are hardcoded inline (no i18n library). Current labels: ความเข้ากันของสี (Color Match), เคล็ดลับตามรูปหน้า (Face Shape Tips), ชื่อสินค้า, แบรนด์, ราคา, หมวดหมู่, เหมาะกับ, คำอธิบาย, ซื้อได้ที่. Any new comparison rows must follow this pattern.
4. **Face shape tips use Thai translations** from `FACE_SHAPE_TIPS_TH` and `FACE_SHAPE_NAMES_TH` in `Products.jsx`. The English source data is `FACE_SHAPE_TIPS` in `ai_service.py` — keep both in sync if tips change.
5. **No uppercase transforms** (`text-transform: uppercase`) in comparison table CSS. `capitalize` for platform link buttons is acceptable.
6. **Graceful degradation**: The Color Match and Face Shape Tips rows only render when the user has a completed analysis (`latestAnalysisId` is set). Users without an analysis see the standard comparison table without these rows.

## Strict Analysis Rules (Verified & Locked)

These rules have been empirically verified and are **locked**. Do not deviate from them without updating the corresponding tests.

### Skin Tone Classification
- **ALWAYS** use the ITA (Individual Typology Angle) formula: `ITA = arctan((L* - 50) / b*) × 180/π`
- **NEVER** classify skin tone from raw RGB, raw L\* alone, or any formula other than ITA.
- Thresholds: >55° fair, >41° light, >28° medium, >10° tan, >-30° dark, ≤-30° deep.
- Implementation: `classify_tone_from_lab(L, b)` in `color_analysis_service.py`.

### Undertone Classification
- **ALWAYS** compute the CIELAB hue angle: `h_ab = atan2(b*, a*)` converted to degrees.
- **NEVER** use raw a\*/b\* threshold logic (e.g., `if a* > 10 then warm`). The hue angle is the only valid input for undertone decisions.
- Thresholds: >65° warm, <50° cool, 50–65° neutral.
- Implementation: `classify_undertone_from_lab(a, b)` in `color_analysis_service.py`.

### Face Shape Geometry Fallback
- **ALWAYS** use the Farkas (1994) anthropometric thresholds defined in the decision tree above.
- The locked thresholds are: `ratio > 1.45` → oblong, `jaw_ratio < 0.70` → heart, `jaw_ratio > 0.85` → square, `temple_ratio < 0.82` → diamond, `ratio ≤ 1.15` → round (unless square).
- **NEVER** introduce new threshold values or reorder the decision tree branches without updating `tests/test_face_shape_decision_tree.py` (39 characterization tests).
- Implementation: `detect_face_shape()` geometry path in `ai_service.py`.

## Gemini RAG Beauty Consultant

The `/gemini` chat feature uses a RAG (Retrieval-Augmented Generation) pipeline to provide beauty advice grounded in AuraMatch's product database.

**Pipeline** (`services/rag_service.py`):
1. User query → ChromaDB vector search → retrieve top-K relevant product IDs
2. Product IDs → MySQL fetch → full product details (name, brand, category, price, personal_color)
3. Product context + user analysis context → system prompt assembly
4. Chat history + system prompt → Gemini generation

**Guardrails** (enforced in `BEAUTY_CONSULTANT_PERSONA`):
- **Brand restriction**: AI must ONLY mention brands/products present in the RAG-retrieved context. No hallucinated brands.
- **Personal Color fallback**: If no analysis context is attached, AI directs user to the Analyze page or asks their season.
- **No denial of data**: AI must never claim AuraMatch lacks Personal Color data — all products have it.

**Frontend** (`GeminiChat.jsx`):
- Auth guard (requires login)
- Session persistence via `sessionStorage` — survives page refresh
- "New Chat" button clears session state
- Markdown rendering via `react-markdown` + `remark-gfm` (tables, bold, lists)
- Tailwind Typography plugin (`prose prose-purple`) for AI response styling
- Pulsing dots typing indicator
- No multipart FormData sent when no file is attached (prevents 400 error)

## Testing & Quality Gates

- **Test-driven maintenance**: Any change to scoring logic or color science must pass the full test suite before committing. Run `python3 -m pytest tests/ -v` and confirm all tests are green.
- **Test counts**: Color science (73), face shape decision tree (39), scoring service (40), cache service (22), embedding service (12), recommendation service (11) — total 197. See `tests/` for current counts.
- **Domain knowledge documentation**: New rules or domain insights discovered during development should be recorded in this CLAUDE.md to maintain coding standards across sessions.

## Git Workflow

- **Regular commits**: After completing a major feature, bug fix, or significant refactor, always commit the changes to git with a clean, descriptive commit message before moving on to the next task.
- **Commit message style**: Use conventional commit format (`feat:`, `fix:`, `refactor:`, `test:`, `docs:`). Include a concise summary of what changed and why.
- **No secrets**: Never commit `.env` files, API keys, or credentials. Check `.gitignore` before staging.
