# Staylio

Staylio is a production-ready, full-stack web application designed to connect property owners with tenants, and calculate compatibility matching scores based on preferences (budget, locations, dates, furnishing levels). It supports real-time chat via WebSockets, in-app notifications, SMTP email alerts, and an administration dashboard.

---

## Technical Architecture

### Backend
- **Framework**: Python Flask (REST APIs + SocketIO Namespace)
- **Database**: PostgreSQL (Neon database ready, defaults to SQLite local database file `rent_flatmate.db`)
- **ORM**: SQLAlchemy ORM
- **Auth**: JWT Authentication (Access & Refresh tokens) with bcrypt password hashing
- **Sockets**: Flask-SocketIO (Online indicators, typing status, read receipts)
- **AI Matchmaking**: OpenAI Chat Completions API with a structured rule-based deterministic fallback engine
- **Email notifications**: Python standard SMTP sender with MIME templates (Mailtrap/SendGrid ready, fallback prints output to server logs on connect failures)

### Frontend
- **Framework**: React.js (built on Vite bundler)
- **Styling**: Tailwind CSS with Curated Dark/Light theme toggles and glassmorphic designs
- **Icons**: Lucide React
- **Forms**: React Hook Form
- **API Client**: Axios with automatic JWT interceptors and silent token refreshers
- **Sockets**: socket.io-client binding

---

## Directory Layout

```text
rent-flatmate-finder/
├── backend/
│   ├── app.py            # Flask entry point & SocketIO initialization
│   ├── config.py         # Loads and checks environment variables
│   ├── models/           # SQLAlchemy database tables
│   ├── routes/           # REST endpoints blueprints
│   ├── controllers/      # Route logic handlers
│   ├── middleware/       # Role-Based Access Control filters
│   ├── services/         # OpenAI matchmaking & SMTP email notification services
│   ├── sockets/          # Chat WebSocket event listeners
│   ├── utils/            # Image uploading and saving helpers
│   ├── prompts/          # OpenAI completion templates
│   ├── uploads/          # Saved properties photos
│   └── requirements.txt  # Python package requirements
│
└── frontend/
    ├── src/
    │   ├── context/      # Auth, Theme, and Socket contexts
    │   ├── layouts/      # Main layout wrappers
    │   ├── components/   # Protected routes, loading cards, property cards
    │   ├── pages/        # Login, Signup, Profiles, Dashboards, Chat panels
    │   ├── services/     # Axios api config
    │   ├── App.jsx       # Routing configurations
    │   ├── index.css     # Tailwind directives and fonts imports
    │   └── main.jsx      # React DOM bootstrap
    ├── tailwind.config.js
    ├── vite.config.js
    └── package.json
```

---

## Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js v18+ and npm

### 1. Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install package dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables. Duplicate `.env.example` as `.env` and fill details:
   ```bash
   cp .env.example .env
   ```
5. Run the backend server:
   ```bash
   python app.py
   ```
   *The database schema tables and directories will be generated automatically. A default administrative account will be seeded on startup:*
   - **Email**: `admin@staylio.com`
   - **Password**: `admin123`

### 2. Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install package dependencies:
   ```bash
   npm install
   ```
3. Run the Vite development compiler:
   ```bash
   npm run dev
   ```
   *The application will launch on `http://localhost:5173`.*

---

## API Endpoints List

### Authentication
- `POST /auth/register` - Create account (Tenant / Owner roles)
- `POST /auth/login` - Obtain Access & Refresh tokens
- `POST /auth/refresh` - Swap expired access tokens
- `GET /auth/me` - Fetch authenticated account details

### Listings
- `GET /listings` - Filtered search query index with compatibility ratings
- `POST /listings` - Post room (Owners only, supports photo files upload)
- `GET /listings/<id>` - Retrieve detailed property and match explanation
- `PUT /listings/<id>` - Edit listing parameters
- `DELETE /listings/<id>` - Delete listing
- `POST /listings/<id>/fill` - Mark room as filled/occupied
- `POST /listings/<id>/interest` - Express interest in room (Tenants only)

### Profiles & Dashboards
- `GET /tenant/profile` - Fetch tenant preferences
- `POST /tenant/profile` - Edit preferences (invalidates compatibility cache)
- `GET /tenant/requests` - Sent request logs
- `GET /owner/listings` - Owner listings
- `GET /owner/requests` - Incoming interest requests
- `POST /owner/requests/<id>/accept` - Accept tenant interest request (unlocks chat)
- `POST /owner/requests/<id>/reject` - Decline tenant request

### Chat Messaging
- `GET /chat/list` - Fetch all threads for current user
- `GET /chat/history/<chat_id>` - Load complete thread conversation history

### Admin Panel
- `GET /admin/analytics` - System metrics summary
- `GET /admin/users` - Directory of registered accounts
- `DELETE /admin/users/<id>` - Remove account
- `GET /admin/listings` - Directory of all properties
- `DELETE /admin/listings/<id>` - Remove property

---

## WebSocket Messaging Architecture

WebSocket events are mapped directly under Flask-SocketIO. Connections require JWT Bearer headers:
- `connect` - Verifies token, flags user online, and broadcasts status changes to active loops.
- `join_chat` - Joins room prefix `chat_{chat_id}`.
- `send_message` - Saves message in the database, broadcasts it to the room, and triggers popups.
- `typing` / `stop_typing` - Signals that a user is editing.
- `mark_read` - Flags messages as read, syncing double ticks.
