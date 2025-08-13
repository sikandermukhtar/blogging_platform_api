# Blog Platform API

A FastAPI-based blog platform API with JWT authentication, Alembic migrations, and PostgreSQL support.  
Package management is handled with **Poetry**.

---

## 📦 Requirements

- Python **3.12+**
- [Poetry](https://python-poetry.org/) (dependency management)
- PostgreSQL (or compatible database)

---

## 🚀 Getting Started

### 1️⃣ Clone the repository
```bash
git clone https://github.com/yourusername/blog-platform-api.git
cd blog-platform-api
```

### 2️⃣ Install dependencies

- Without dev tools (production-like)

```
poetry install
```
-With dev tools (ruff for formatting)
```
poetry install --with dev
```

### 3️⃣ Setup environment variables

- Create .env file in the project root
- Edit .env with your own values.

Example .env:
```
DATABASE_URL=postgresql://username:password@localhost:5432/blog_db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRES_MINUTES=60
```

### 4️⃣ Run database migrations

Alembic is used for database migrations.

- Generate a migration after making model changes:
```
poetry run alembic revision --autogenerate -m "description of changes"
```
- Apply migrations:
```
poetry run alembic upgrade head
```
- Downgrade migration (optional):
```
poetry run alembic downgrade -1
```

### 5️⃣ Start the development server

```
poetry run uvicorn app.main:app --reload
```

- The API will be available at:

```
http://127.0.0.1:8000
```

- Swagger Docs
```
http://127.0.0.1:8000/docs
```

## 🛠 Project Structure

```
.
├── alembic/               # Database migration scripts
├── config/                # Config, security, auth
├── models/                # SQLAlchemy models
├── routes/                # Routes and endpoints
├── schemas/               # Pydantic schemas
├── main.py                # FastAPI entry point
├── utils/                 # hashing and dependencies
├── alembic.ini            # Alembic configuration
├── pyproject.toml         # Poetry dependencies
├── poetry.lock            # Locked dependency versions
├── .env.example           # Environment variable template
├── README.md              # This file
└── .gitignore             # Ignored files

```