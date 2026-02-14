# SmartBiz Backend

## Setup

1. Navigate to `backend/` directory.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   - Copy `.env.example` to `.env` (create one if needed).
   - Configure `DATABASE_URL`.

## Running

```bash
uvicorn app.main:app --reload
```

## API Documentation

Once running, visit:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Database

The app is configured to create tables automatically on startup (`app/main.py`). For production, use Alembic.
