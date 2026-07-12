# Staylio System Design Document

This document outlines the high-level system architecture and data flows of the Staylio room rental and flatmate matchmaking application.

---

## 1. API Architecture & Request Handling
Staylio follows a decoupled Client-Server architecture utilizing a **Flask REST API** backend and a **Vite React** frontend. 
*   **Access Control**: All private REST endpoints are protected with Role-Based Access Control (RBAC) via stateless JSON Web Tokens (JWT). Short-lived Access Tokens are transmitted via HTTP header Bearer parameters, while silent token refreshing is handled via automatic Axios request interceptors on the frontend.
*   **State Management**: Dynamic filters are persisted in `localStorage` in the browser, ensuring page navigations carry the active tenant preferences into all listing detail views seamlessly.

---

## 2. Real-Time Chat & WebSockets
Staylio uses a stateful WebSocket engine powered by `Flask-SocketIO` to support instant, interactive conversations:
*   **Channel Isolation**: Accepted interest requests unlock a unique conversation ID. Users connect to specific SocketIO rooms prefixed as `chat_{id}` to isolate chat traffic.
*   **Instant Events**: Supports real-time text delivery, message read receipts (syncing double-check ticks on-screen), active typing state indicators, and global user-online presence changes.

---

## 3. Real-Time Compatibility Engine & LLM Fallback
Matchmaking scores are evaluated dynamically against search filters or tenant profile records:
```
           +---------------------------------+
           |      Request Compatibility      |
           +---------------------------------+
                            |
             { Is OPENAI_API_KEY supplied? }
               /                         \
            [Yes]                        [No]
             /                             \
  +---------------------+         +---------------------+
  | OpenAI Completions  |         | Deterministic Rule  |
  | Structured JSON Map |         | Local Python Engine |
  +---------------------+         +---------------------+
```
*   **Local Rule-Based Fallback**: If no OpenAI API Key is configured or the completion endpoint fails, a local fallback engine parses matching rules (budget, location city names, amenities array overlap, lifestyle text tags) to guarantee reliability.
*   **Weights Layout**: Scores are calculated out of 100 points: Location Match (30 pts), Budget Match (25 pts), Room Type Match (15 pts), Gender (10 pts), Amenities (10 pts), and Lifestyle (10 pts).

---

## 4. Notifications & SMTP Email Service
Important events trigger structured notification cycles:
*   **Auto-Booking Notification**: Accepting a tenant's request flags the listing as Booked, rejects other pending requests in the database, and issues in-app database notifications to all candidates.
*   **Email Deliverability**: The backend connects to an SMTP server. When a room is booked, SMTP sends HTML-formatted emails to candidates. If connection failures occur, the service fails-safe by writing the output to the server logs, avoiding request failures.

---

## 5. Database Schema & Persistence
Data is stored using a relational SQLite/PostgreSQL schema managed via SQLAlchemy:
*   **Cascading Deletions**: Listings map to `owner_profiles`, `messages`, `chats`, `interest_requests`, and `notifications` tables. Deleting a listing triggers atomic cascades, deleting associated files from the local storage disk, clearing chats, and clean-dropping database keys safely.
