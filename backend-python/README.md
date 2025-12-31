# SymptoMap Python FastAPI Backend

Python backend for SymptoMap disease surveillance platform.

## Features

- ✅ **AI Doctor Chatbot** - GPT-4 powered medical conversation
- ✅ **Authentication** - JWT-based auth with role-based access
- ✅ **Database** - PostgreSQL with SQLAlchemy async
- ✅ **Redis caching** - For conversation history
- 🔄 **Outbreak management** - Coming soon
- 🔄 **Predictions** - Integration with ML service
- 🔄 **Alert system** - SendGrid email alerts

## Quick Start

### 1. Install Dependencies

```bash
cd backend-python
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

Required environment variables:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string  
- `OPENAI_API_KEY` - Your OpenAI API key
- `JWT_SECRET_KEY` - Secret key for JWT tokens

### 3. Run the Server

```bash
# Development
python -m app.main

# Or with uvicorn
uvicorn app.main:app --reload --port 8000
```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## Project Structure

```
backend-python/
├── app/
│   ├── main.py              # FastAPI application
│   ├── core/
│   │   ├── config.py        # Configuration
│   │   ├── database.py      # Database setup
│   │   └── redis.py         # Redis client
│   ├── models/
│   │   ├── user.py          # User model
│   │   └── chatbot.py       # Chatbot models
│   ├── services/
│   │   └── chatbot_service.py  # AI chatbot service
│   └── api/
│       └── v1/
│           ├── auth.py       # Authentication routes
│           ├── chatbot.py    # Chatbot routes
│           ├── outbreaks.py  # Outbreak routes
│           ├── predictions.py # Prediction routes
│           └── alerts.py     # Alert routes
├── requirements.txt
└── .env.example
```

## API Endpoints

### Chatbot

- `POST /api/v1/chatbot/start` - Start new conversation
- `POST /api/v1/chatbot/message` - Send message
- `POST /api/v1/chatbot/end` - End conversation with assessment
- `POST /api/v1/chatbot/feedback` - Submit feedback
- `GET /api/v1/chatbot/conversation/{session_id}` - Get conversation history

### Authentication

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get token
- `GET /api/v1/auth/me` - Get current user info

## Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app
```

## Example Usage

### Start Chatbot Conversation

```python
import httpx

async with httpx.AsyncClient() as client:
    # Start conversation
    response = await client.post(
        "http://localhost:8000/api/v1/chatbot/start",
        json={
            "user_info": {"age": 28, "gender": "male"},
            "location": {"city": "Mumbai", "country": "India"}
        }
    )
    
    session_id = response.json()["session_id"]
    
    # Send message
    response = await client.post(
        "http://localhost:8000/api/v1/chatbot/message",
        json={
            "session_id": session_id,
            "message": "I have fever and body ache for 2 days"
        }
    )
    
    print(response.json())
```

## License

MIT
