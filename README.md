# Mike Smart Match

Mike Smart Match is an AI-powered candidate matching app that ranks candidates against a job description using a FastAPI backend, LangChain/OpenAI-based extraction and scoring, PostgreSQL with `pgvector`, and a React/Vite frontend.

## Features

- Match candidates by full job description or quick inputs such as title, skills, location, and experience.
- Rank candidates with match scores, rationale, and location fit.
- Export results to CSV from the UI.
- Store and query embeddings in PostgreSQL with `pgvector`.

## Tech Stack

- Backend: FastAPI, Uvicorn, LangChain, OpenAI, psycopg2
- Database: PostgreSQL + `pgvector`
- Frontend: React, Vite

## Project Structure

```text
HireIQ/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/
│   │   │   └── match.py
│   │   ├── schemas/
│   │   │   └── match_schema.py
│   │   └── services/
│   │       └── langchain_service.py
│   ├── migration.sql
│   ├── populate_embeddings.py
│   └── run.py
├── frontend/
│   ├── index.html
│   ├── package.json
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       ├── styles.css
│       └── components/
│           ├── FindMatches.jsx
│           ├── FindMatches.css
│           ├── JobCard.jsx
│           └── ResultsPanel.jsx
├── candidates_rows.csv
└── README.md
```

### What each folder does

- `backend/app/main.py`: FastAPI app setup, CORS, and health endpoints.
- `backend/app/routes/`: API routes. Right now `match.py` handles the match endpoint.
- `backend/app/schemas/`: Pydantic request/response models.
- `backend/app/services/`: Matching logic, LLM extraction, embedding lookup, scoring, and rationale generation.
- `backend/migration.sql`: Database migration for `pgvector` and candidate embeddings.
- `backend/populate_embeddings.py`: Backfills embeddings for existing candidate rows.
- `frontend/src/`: React UI entry point, pages, and reusable components.
- `frontend/src/components/`: Job card preview, search action, and results UI.
- `candidates_rows.csv`: Sample candidate dataset used to seed the database.

## How It Works

1. The recruiter enters a job title, skills, location, experience, or a full job description in the frontend.
2. `frontend/src/components/FindMatches.jsx` sends that data to `POST /api/mike/match`.
3. `backend/app/routes/match.py` validates the request and builds a fallback job description when only quick inputs are provided.
4. `backend/app/services/langchain_service.py` extracts JD details, generates embeddings, filters candidates from PostgreSQL, and scores them.
5. The backend returns the ranked candidates with match scores, location fit, matched skills, and rationale.
6. `frontend/src/components/ResultsPanel.jsx` renders the results and lets the user sort or export them to CSV.

## Prerequisites

- Python 3.10 or newer
- Node.js 16 or newer
- PostgreSQL database with the `vector` extension enabled
- OpenAI-compatible API key and base URL

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-org/mike-smart-match.git
cd mike-smart-match
```

### 2. Configure the backend

Create a `backend/.env` file with the following variables:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1
DATABASE_URL=postgresql://user:password@host:5432/database
```

Install backend dependencies:

```bash
cd backend
pip install -r requirements.txt
```

### 3. Prepare the database

Run the SQL migration to enable `pgvector` and add the embedding column:

```bash
psql "$DATABASE_URL" -f migration.sql
```

If your shell does not support that form, run the file with your preferred PostgreSQL client or paste the contents into your database console.

If candidate records already exist, populate their embeddings:

```bash
python populate_embeddings.py
```

### 4. Configure the frontend

Install frontend dependencies:

```bash
cd ../frontend
npm install
```

## Running the App

Open two terminals and run the backend and frontend separately.

### Backend

```bash
cd backend
python run.py
```

The API will be available at `http://127.0.0.1:8000`, and interactive docs will be available at `http://127.0.0.1:8000/docs`.

### Frontend

```bash
cd frontend
npm run dev
```

The Vite app will run at `http://127.0.0.1:5173`.

## API Endpoint

- `POST /api/mike/match`

Example request body:

```json
{
  "job_title": "Senior React Developer",
  "location": "Remote",
  "skills": ["React", "TypeScript", "PostgreSQL"],
  "experience_years": 5,
  "job_description": "Build and maintain modern frontend applications..."
}
```

## Notes

- The backend accepts either a full job description or quick inputs such as skills and experience.
- The frontend exports matched candidates to CSV.
- Matching depends on a reachable PostgreSQL database and a valid OpenAI-compatible model endpoint.
- If you want to keep the codebase cleaner over time, keep all route logic inside `backend/app/routes/`, matching/scoring logic inside `backend/app/services/`, and UI components inside `frontend/src/components/`.

## License

MIT


## Screenshots

<div align="center">

### Flow Images
<img src="Images/Flow%20Images.png" alt="HireIQ workflow overview" width="900" />

<br /><br />

### Frontend UI
<img src="Images/Screenshot%202026-05-10%20100333.png" alt="HireIQ candidate matching screen" width="900" />

<br /><br />

<img src="Images/Screenshot%202026-05-10%20100519.png" alt="HireIQ results screen" width="900" />

</div>
