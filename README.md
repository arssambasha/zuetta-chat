# Zuetta Chat

A real-time group chat app built with **Django Channels**, **Redis**, and **MySQL**. Create or join **Z-Groups** and chat instantly over WebSockets.

## Features

- User registration, login, and logout
- Create a Z-Group with a unique Z-ID (lowercase letters, numbers, and underscores)
- Search and join groups by Z-Name or Z-ID
- Real-time messaging over WebSockets
- Message history saved in MySQL, loaded 25 at a time with infinite scroll
- Per-user rate limiting backed by Redis (20 messages per 10 seconds)
- Paginated home page listing your groups
- Responsive UI with Bootstrap 5

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Django 5, Django Channels, Daphne (ASGI) |
| Real-time | WebSockets, Redis channel layer |
| Database | MySQL |
| Cache / Rate limit | Redis (`django-redis`) |
| Frontend | Django templates, Bootstrap 5, vanilla JavaScript |

## Prerequisites

- Python 3.10+
- MySQL server
- Redis server (on Windows, use WSL or Docker)

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
# Windows
copy .env.example .env
# macOS / Linux
cp .env.example .env
```

Edit `.env`:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=zuetta
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
```

Generate a secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
```

### 4. Create the database

```sql
CREATE DATABASE zuetta CHARACTER SET utf8mb4;
```

### 5. Start Redis

```bash
redis-server
```

### 6. Run migrations and start the server

```bash
python manage.py migrate
python manage.py runserver
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000), register an account, and create your first Z-Group.

## How It Works

1. A user opens a group at `/chat/<z_id>/`, and the browser opens a WebSocket to `/ws/chat/<z_id>/`.
2. `ChatConsumer` adds the connection to a Redis-backed channel group for that room.
3. On each message, the consumer checks the rate limit, saves the message to MySQL, and broadcasts it to everyone in the room.
4. Older messages are fetched from `/messages?start=&end=&group=` as the user scrolls down.

## Project Structure

```
.
├── chat/
│   ├── migrations/
│   ├── static/chat/styles.css
│   ├── templates/chat/      # HTML templates
│   ├── consumers.py         # WebSocket consumer + rate limiting
│   ├── models.py            # User, Group, Messages
│   ├── routing.py           # WebSocket routes
│   ├── urls.py
│   └── views.py
├── zuetta/
│   ├── asgi.py              # HTTP + WebSocket routing
│   ├── settings.py
│   └── urls.py
├── .env.example
├── manage.py
└── requirements.txt
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` for development |
| `ALLOWED_HOSTS` | Comma-separated hostnames |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD` | MySQL credentials |
| `DB_HOST`, `DB_PORT` | MySQL host and port |