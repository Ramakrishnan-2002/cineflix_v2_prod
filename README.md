# CineFlix API

A robust, production-ready backend for a movie and review platform built with **FastAPI**.

## 🚀 Features

* **FastAPI Framework**: High performance, asynchronous Python web framework.
* **Authentication**: JWT-based user authentication and authorization.
* **Email Services**: Background task email sending for Password Reset (via Google SMTP).
* **Database**: MongoDB integration using Beanie ODM and Motor (Asynchronous).
* **Caching & Rate Limiting**: Redis integration (using SlowAPI) to prevent API abuse.
* **External APIs**: YouTube Data API v3 integration for fetching movie trailers.
* **Dockerized**: Multi-stage Dockerfile and Docker Compose for seamless deployment of the API, MongoDB, Mongo-Express, and Redis.

---

## 📁 Project Structure

```text
.
├── app/
│   ├── databases/       # Database connection and Beanie initialization
│   ├── middlewares/     # Custom middlewares (e.g., Redis Idempotency)
│   ├── models/          # Beanie ODM database models (User, Review, etc.)
│   ├── routers/         # API Route definitions (users, auth, movies, mail, etc.)
│   ├── schemas/         # Pydantic models for request/response validation
│   ├── services/        # Business logic (e.g., email_service.py)
│   └── main.py          # FastAPI application entry point & lifespan events
├── .env.example         # Template for environment variables
├── docker-compose.yml   # Infrastructure orchestration
├── Dockerfile           # Multi-stage container build instructions
└── requirements.txt     # Python dependencies
```

---

## 🛠️ Prerequisites

* [Docker](https://docs.docker.com/get-docker/) and Docker Compose
* *Optional (for local development)*: Python 3.11+, local MongoDB, local Redis.

---

## ⚙️ Environment Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and fill in your specific credentials (especially your Gmail App Password and YouTube API Key).

---

## 🐳 Running with Docker (Recommended)

The easiest way to run the entire stack (API, MongoDB, Mongo-Express UI, and Redis) is using Docker Compose.

1. Build and start the containers:
   ```bash
   docker-compose up --build -d
   ```
2. **Access the application:**
   * **API Docs (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
   * **Mongo-Express (DB Admin)**: [http://localhost:8081](http://localhost:8081) *(Login: admin / admin123)*

3. To stop the containers:
   ```bash
   docker-compose down
   ```

---

## 💻 Running Locally (Without Docker)

1. **Create a virtual environment & install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Ensure your `.env` points to local databases:**
   Change `mongodb` and `redis` in your `.env` URLs back to `localhost`.

3. **Start the FastAPI server:**
   ```bash
   uvicorn app.main:app --reload
   ```

---

## 🔑 Note on Gmail App Passwords
To use the email service (Password Reset), you must generate a 16-character App Password from your Google Account. Regular account passwords will result in a `535 Authentication Error`. Do not include spaces in the App Password inside your `.env` file.
