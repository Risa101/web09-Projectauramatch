# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AuraMatch is a full-stack AI-powered beauty/cosmetics recommendation platform. It analyzes facial structure and personal color to recommend makeup products. Features include face shape detection, skin tone/undertone analysis, personal color season classification (Spring/Summer/Autumn/Winter), AI chat via Gemini, and a photo editor.

## Tech Stack

- **Frontend**: React 19 + Vite 8, Tailwind CSS 4, React Router DOM 7, Axios, plain JavaScript (no TypeScript)
- **Backend**: Python FastAPI, SQLAlchemy 2.0 ORM, MySQL (PyMySQL driver)
- **AI/ML**: OpenCV, MediaPipe (face detection), dlib (face landmarks), TensorFlow/Keras (face shape CNN), Google Generative AI (Gemini), colour-science (CIELAB/CIEDE2000)
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
- `services/` — Business logic layer. `ai_service.py` orchestrates the single-pass face analysis pipeline, `color_analysis_service.py` handles CIELAB color science and CIEDE2000 matching, `recommendation_service.py` handles product matching, `gemini_service.py` wraps the Gemini API.
- `config/database.py` — SQLAlchemy engine and session setup.

**Frontend structure:**
- `src/pages/` — Route-level page components
- `src/components/` — Shared components (Navbar)
- `src/context/AuthContext.jsx` — Auth state via React Context API (stores JWT in localStorage)
- `src/api/axios.js` — Configured Axios instance with auth interceptor
- `src/services/tracker.js` — User behavior analytics

**Routes** (defined in `src/App.jsx`): `/` (Home), `/login`, `/register`, `/analyze`, `/products`, `/gemini`, `/editor`, `/profile`, `/admin`

## Face Analysis Pipeline (Single-Pass Architecture)

`analyze_face()` in `ai_service.py` runs one MediaPipe FaceMesh session via `_run_facemesh()`, which returns landmarks (468 points), a face bounding box, and a face crop. This data is reused for both face shape detection and skin extraction — never initialize FaceMesh twice per call.

**Face shape detection** (`detect_face_shape()`) has two paths:
1. **CNN path** (primary): Uses the face crop from `_run_facemesh()` with the model at `models_ai/face_shape_cnn.h5`. Produces all 7 shapes including triangle.
2. **Geometry fallback**: When CNN is unavailable, uses MediaPipe landmark ratios. Produces 6 of 7 shapes (triangle is CNN-only).

**Geometry decision tree thresholds** (locked by `tests/test_face_shape_decision_tree.py`):
```
ratio = face_height / cheekbone_width    (landmarks: 152↔10 / 234↔454)
jaw_ratio = jaw_width / cheekbone_width  (landmarks: 172↔397 / 234↔454)
temple_ratio = temple_width / cheekbone  (landmarks: 127↔356 / 234↔454)

ratio > 1.5                           → oblong
1.3 < ratio ≤ 1.5:
  jaw_ratio < 0.75                    → heart
  temple_ratio < 0.85                 → diamond
  else                                → oval
1.0 < ratio ≤ 1.3:
  jaw_ratio > 0.9                     → square
  jaw_ratio < 0.75                    → heart
  temple_ratio < 0.85                 → diamond
  else                                → oval
ratio ≤ 1.0:
  jaw_ratio > 0.9                     → square
  else                                → round
no face detected                      → oval (default)
```
If you change these thresholds, update `tests/test_face_shape_decision_tree.py` (39 characterization tests).

**Skin extraction** uses the face bounding box to sample the cheek region (`extract_skin_lab_from_bbox()` in `color_analysis_service.py`) instead of a naive center-crop. Falls back to `extract_skin_lab()` when no face is detected.

**Enriched API response**: `POST /analysis/` returns analysis results, palette data, face shape tips, and product recommendations in a single response. The frontend uses this with a fallback to separate `/recommendations/` calls. `generate_recs_for_analysis()` in `routes/recommendations.py` is the shared function used by both paths.

## Key Patterns

- All backend routes are registered in `main.py` via `app.include_router()`
- `Base.metadata.create_all(bind=engine)` auto-creates tables on startup
- CORS is configured for local dev ports: 5173, 5175, 5177, 3000
- File uploads go to `uploads/` directory, served as static files at `/uploads`
- `personal_color` enum stays at 4 seasons (spring/summer/autumn/winter) for backward compatibility; 12-sub-season detail is accessed via `palette_id → ColorPalette.sub_type`

## Color Science Rules (MANDATORY)

These rules are non-negotiable for any code touching skin tone analysis or personal color matching:

1. **Always use CIELAB (L\*a\*b\*) color space** for skin tone extraction and comparison. Never use raw RGB values for color analysis — RGB is device-dependent and perceptually non-uniform.
2. **Use CIEDE2000 (ΔE00) formula** for all color distance calculations. Do not use CIE76 or CIE94 — CIEDE2000 is the current standard with blue-region correction and perceptual accuracy.
3. **Skin tone classification must use L\* (lightness)**, not RGB brightness `(r+g+b)/3`.
4. **Undertone classification must use a\* and b\* axes**, not the `r - b` difference.
5. **Season matching must use Delta E distance** against `color_palettes.best_colors.skin_reference` centroids. Do not use hardcoded lookup dicts for personal color assignment.
6. **All color palette reference data must be stored in CIELAB** with `{"L", "a", "b"}` format in the `color_palettes` JSON columns.
7. **The `colour-science` library** (`import colour`) is the canonical dependency for color space conversions and CIEDE2000 calculations. RGB→CIELAB conversion path: `sRGB → XYZ (D65) → L*a*b*`.
8. **Legacy fallback**: `get_personal_color()` in `ai_service.py` retains the old lookup dict as a fallback when palette data or db session is unavailable. New code should always pass `skin_lab` and `db_session` to use the CIEDE2000 path.
