Here's the **complete README in English** only, fully cleaned and organized:

---

<div align="center">

# 🚀 Modular Django Backend

A production-ready, modular Django 5 backend built for **real-world scalability**.  
Designed with **clean architecture**, **async processing**, **WebSockets**, and **Docker** —  
because large codebases should stay maintainable.

⚠️ **Active Development** — APIs and structure may evolve.

---

## 📌 About This Project

This backend is built for **real-world, growing projects** with:

- ✅ **Domain-based modular architecture** — each feature lives in its own app
- ✅ **REST + WebSockets** — real-time communication ready
- ✅ **Async task queue** via Celery + Redis
- ✅ **Docker-first** — run anywhere with one command
- ✅ **Clean, maintainable, scalable** code patterns

Whether you're building an e-commerce platform, learning management system, or real-time chat app — this structure keeps things organized as you scale.

---

## 🧱 Architecture at a Glance

```
project
│
├── config          # Global settings, WSGI/ASGI config
├── common          # Shared utilities, base classes, mixins
│
├── core            # Auth & user management
├── address         # Location data
│
├── product         # Product catalog
├── cart            # Shopping cart
├── order           # Order processing
├── invoice         # Billing & invoices
├── transaction     # Payment transactions
│
├── blog            # Blog system
├── notifications   # Push/in-app notifications
│
├── chat            # Real-time WebSocket chat
├── tickets         # Support tickets
│
├── dashboard       # Admin analytics
```

---

## 🛠 Tech Stack

| Category | Technologies |
|----------|--------------|
| **Core** | Django 5, Django REST Framework, PostgreSQL |
| **Async & Realtime** | Celery, Redis, Django Channels, Daphne |
| **Auth** | SimpleJWT (JWT), Djoser |
| **Storage** | MinIO / S3 (django-storages) |
| **Monitoring** | django-celery-beat, Flower |
| **API Docs** | drf-spectacular (OpenAPI) |
| **Utils** | pandas, openpyxl, persiantools, jdatetime |
| **Deployment** | Docker, Gunicorn, Uvicorn |

---

## 🐳 Running with Docker (Recommended)

**One command — full stack (DB, Redis, app, workers):**

```bash
# Clone the repo
git clone https://github.com/your-username/project.git
cd project

# Build and start
docker compose up --build

# Apply migrations (new terminal)
docker compose exec web python manage.py migrate

# Create superuser
docker compose exec web python manage.py createsuperuser
```

That's it. Your backend is live.

---

## ⚡ Docker: Using a Pip Mirror (Faster Installs)

For faster package installation, you can use a **custom pip mirror** — especially useful in regions with slow PyPI access or behind restricted networks.

### 🔧 Build with a mirror from the CLI

```bash
docker build \
  --build-arg PIP_INDEX_URL=https://pypi.iranrepo.ir/simple \
  -t my-django-backend .
```

### 🚀 Or in `docker-compose.yml`

```yaml
services:
  web:
    build:
      context: .
      args:
        PIP_INDEX_URL: https://pypi.iranrepo.ir/simple
```

### ✅ How it works

| If you... | Result |
|-----------|--------|
| Don't set `PIP_INDEX_URL` | Falls back to default PyPI |
| Set a custom mirror URL | All `pip install` commands use your mirror → **much faster** ✅ |

> 💡 **Pro tip:** You can use any pip-compatible mirror — domestic mirrors, Tsinghua, Aliyun, IranRepo, etc. This dramatically speeds up Docker builds in restricted network environments.

---

## 💻 Running Without Docker

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up .env file
cat > .env << EOF
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://user:password@localhost:5432/db_name
REDIS_URL=redis://localhost:6379/0
EOF

# Migrate and run
python manage.py migrate
python manage.py runserver
```

---

## 🔄 Background Workers (Celery)

```bash
# Worker
celery -A config worker -l info

# Scheduler (beat)
celery -A config beat -l info

# Monitoring (Flower)
celery -A config flower
```

---

## 🔌 WebSockets & Realtime

Powered by **Django Channels** + ASGI. Features include:

- 💬 Live chat messaging
- 🎫 Real-time ticket updates
- 🔔 Instant notifications

Production uses **Daphne/Uvicorn** behind Nginx.

---

## 🧪 Testing

```bash
pytest
```

Tests are organized per app in `tests/` directories.

---

## 📦 Fixtures (Sample Data)

Load pre-defined data for local development:

```bash
python manage.py loaddata address/fixtures/address.json
python manage.py loaddata product/fixtures/products.json
python manage.py loaddata blog/fixtures/posts.json
```

Available fixtures for most domains.

---

## 🧠 Design Philosophy

| Principle | Implementation |
|-----------|----------------|
| **Business logic** | Lives in `services/` or `tasks/`, not views |
| **Type safety** | `types/` for enums & constants |
| **Reusability** | `common/` for shared utilities (pagination, base views, permissions) |
| **Environment config** | Settings split by environment (dev/prod/local) |

---

## 📌 Project Status

| Area | Status |
|------|--------|
| Core structure | ✅ Complete |
| Main apps | ✅ In place |
| Feature development | 🛠 Active |
| Stability | 🔄 Breaking changes possible |

---

## 🤝 About the Developer

<div align="center">
  <img src="https://img.shields.io/badge/Backend-Django%20%26%20FastAPI-blue?style=flat-square" />
  <img src="https://img.shields.io/badge/Realtime-WebSockets%20%7C%20Chat-brightgreen?style=flat-square" />
  <img src="https://img.shields.io/badge/Auth-JWT%20%7C%20OTP-orange?style=flat-square" />
</div>

**Backend developer** specializing in:

- 🚀 **Django & FastAPI** — scalable APIs
- 💬 **Realtime systems** — WebSockets, chat, live communication
- 🔐 **Authentication** — OTP, JWT, token-based security
- 💰 **Financial modules** — billing, invoicing, wallet systems
- 🐳 **DevOps** — Docker, Linux, production deployments
- 🤖 **AI & LLM** — collaboration on intelligent systems

> **Passionate about clean, maintainable, and scalable code.**

---

## 📄 License

This project is open source and available under the MIT License.

---

## 🤝 Contributing

Issues and pull requests are welcome! Feel free to open an issue to discuss features or bugs.

---

<div align="center">

⭐ **Star this repo** if you find it useful — it helps a lot!

🐛 **Issues & PRs** welcome — let's build better backends together.

</div>

---

That's the complete README in English, clean and ready to use!
