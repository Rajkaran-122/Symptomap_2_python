#!/bin/bash

echo "🚀 Setting up SymptoMap Python Backend..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python -m venv venv

# Activate virtual environment
if [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Copy .env.example to .env if not exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from example..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your configuration"
fi

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your configuration (DATABASE_URL, OPENAI_API_KEY, etc.)"
echo "2. Ensure PostgreSQL and Redis are running"
echo "3. Run: python -m app.main"
echo "4. Visit http://localhost:8000/api/docs for API documentation"
