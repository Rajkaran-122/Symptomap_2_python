@echo off
echo 🚀 Setting up SymptoMap Python Backend...

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Copy .env.example to .env if not exists
if not exist ".env" (
    echo 📝 Creating .env file from example...
    copy .env.example .env
    echo ⚠️  Please edit .env with your configuration
)

echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Edit .env with your configuration (DATABASE_URL, OPENAI_API_KEY, etc.)
echo 2. Ensure PostgreSQL and Redis are running
echo 3. Run: python -m app.main
echo 4. Visit http://localhost:8000/api/docs for API documentation
