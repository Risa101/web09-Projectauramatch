# AuraMatch — AI-Powered Beauty Recommendation Platform

AuraMatch is a full-stack web application that analyzes facial structure and personal color to recommend makeup products tailored to each user.

## Features

- **Face Analysis** — Detects face shape (7 types) using CNN + MediaPipe geometry fallback, classifies skin tone via ITA angle, undertone via CIELAB hue angle, and personal color season (Spring/Summer/Autumn/Winter) via CIEDE2000 matching
- **Gemini RAG Beauty Consultant** — AI chatbot powered by Google Gemini with RAG (Retrieval-Augmented Generation) grounded in the product database via ChromaDB vector search
- **Product Recommendations** — Multi-signal scoring engine (S1–S6) combining color proximity, seasonal match, avoid-color penalty, feedback, and popularity
- **Product Comparison** — Side-by-side comparison of up to 3 products with Color Match % and face shape tips
- **Photo Editor** — Virtual makeup try-on with face landmark detection
- **Blog & Content** — Beauty tips and articles with category filtering
- **User Profiles** — Analysis history, favorites, reviews, and skin concern tracking
- **Admin Dashboard** — Product management, banner management, blog editor, analytics, and commission tracking

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | React 19, Vite 8, Tailwind CSS 4, React Router DOM 7, Axios |
| **Backend** | Python FastAPI, SQLAlchemy 2.0, MySQL (PyMySQL) |
| **AI/ML** | OpenCV, MediaPipe, dlib, TensorFlow/Keras, Google Gemini |
| **RAG** | ChromaDB, paraphrase-multilingual-MiniLM-L12-v2, Gemini |
| **Color Science** | colour-science (CIELAB, CIEDE2000) |
| **Caching** | Redis (optional, graceful fallback) |
| **Auth** | JWT (python-jose) + bcrypt |

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- MySQL 8.0+
- CMake (for dlib)

### Database Setup

```bash
mysql -u root -e "CREATE DATABASE IF NOT EXISTS auramatchnewversion;"
mysql -u root auramatchnewversion < auramatch.sql
mysql -u root auramatchnewversion < seed_makeup_products.sql
mysql -u root auramatchnewversion < seed_product_color_shades.sql
mysql -u root auramatchnewversion < seed_product_concerns.sql
```

### Backend

```bash
cd backendauramatchnewversion
cp .env.example .env          # Edit with your DB credentials and Gemini API key
pip install -r requirements.txt
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

Optional — seed ChromaDB for RAG search:
```bash
python scripts/seed_chromadb.py
```

### Frontend

```bash
cd frontendauramatchnewversion
npm install
npm run dev                    # Dev server on http://localhost:5175
```

### Environment Variables

See `backendauramatchnewversion/.env.example`:

| Variable | Description |
|----------|-------------|
| `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` | MySQL connection |
| `SECRET_KEY` | JWT signing key |
| `GEMINI_API_KEY` | Google Generative AI API key |

## Architecture

```
┌─────────────────┐     /api/*      ┌──────────────────┐
│   React SPA     │ ──── proxy ───> │   FastAPI REST   │
│   (Vite:5175)   │                 │   (Uvicorn:8001) │
└─────────────────┘                 └────────┬─────────┘
                                             │
                          ┌──────────────────┼──────────────────┐
                          │                  │                  │
                    ┌─────▼─────┐    ┌───────▼──────┐   ┌──────▼──────┐
                    │   MySQL   │    │   ChromaDB   │   │   Gemini    │
                    │  (Data)   │    │  (Vectors)   │   │   (AI Gen)  │
                    └───────────┘    └──────────────┘   └─────────────┘
```

## Testing

```bash
cd backendauramatchnewversion
python3 -m pytest tests/ -v       # Run all 197 tests
```

| Test Suite | Count |
|-----------|-------|
| Color science | 73 |
| Scoring service | 40 |
| Face shape decision tree | 39 |
| Cache service | 22 |
| Embedding service | 12 |
| Recommendation service | 11 |

## Project Structure

```
├── backendauramatchnewversion/
│   ├── config/          # Database, ChromaDB, Redis config
│   ├── models/          # SQLAlchemy ORM models
│   ├── routes/          # FastAPI route handlers
│   ├── services/        # Business logic (AI, RAG, scoring, color science)
│   ├── scripts/         # Seeding and utility scripts
│   └── tests/           # Pytest test suites
├── frontendauramatchnewversion/
│   └── src/
│       ├── pages/       # Route-level page components
│       ├── components/  # Shared components
│       ├── context/     # React Context (Auth)
│       └── api/         # Axios client with auth interceptor
├── diagrams/            # ER, class, and sequence diagrams
├── auramatch.sql        # Database schema
└── seed_*.sql           # Seed data
```

## Contributors

- Web Programming 09 — AuraMatch Team
