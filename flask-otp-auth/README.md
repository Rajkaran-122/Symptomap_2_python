# Enterprise OTP Authentication System (Flask + PostgreSQL)

A production-ready, secure, and scalable OTP-based 2-factor authentication system built with Python Flask and PostgreSQL. Designed for deployment on Render.

## 🚀 Features

- **Multi-Factor Authentication**: Password + OTP (Email & SMS).
- **Secure Storage**: Argon2 for passwords, SHA-256 for OTPs (never stored plain-text).
- **Role-Based Access**: Admin, Doctor, User roles.
- **Enterprise Security**:
    - Rate Limiting (Sliding Window).
    - Session Management (JWT Access + Refresh Tokens).
    - Account Locking after failed attempts.
    - Audit Logging.
- **Integration Ready**: Deployment descriptors for Render.

## 🛠️ Quick Start (Windows)

1.  **Run Setup**:
    Double-click `setup.bat`. This will:
    - Create a virtual environment.
    - Install dependencies.
    - Initialize the database (SQLite by default for local dev).
    - Run migrations.

2.  **Start Server**:
    Double-click `run.bat`.
    Server will start at `http://localhost:5000`.

## 📚 Documentation

- **[Integration Guide](integration_guide.md)**: How to connect this auth service with your main FastAPI backend.
- **[Deployment Guide](deployment_guide.md)**: Steps to deploy to Render Free Tier to a live URL.
- **[API Schema/Database](schema.sql)**: Full PostgreSQL schema reference.

## 🔑 Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Register new user (triggers OTP) |
| POST | `/api/auth/verify-otp` | Verify email/phone OTP |
| POST | `/api/auth/login` | Login step 1 (Password -> triggers OTP) |
| POST | `/api/auth/login/verify` | Login step 2 (OTP -> returns tokens) |
| POST | `/api/auth/forgot-password` | Request password reset OTP |
| POST | `/api/auth/reset-password` | Reset password using OTP |
| GET | `/api/auth/me` | Get current user info (Requires Bearer Token) |

## ⚙️ Configuration

Check `.env` for configuration.

- **FastAPI Integration**: Ensure `JWT_SECRET_KEY` matches your main backend.
- **Email/SMS**: Configure SMTP and Twilio credentials in `.env` for production delivery.
