# Staylio Production Deployment Guide

This guide walks you through deploying the Staylio full-stack application to production using **Render** (for persistent Flask API + WebSocket backend + PostgreSQL) and **Vercel** (for the fast React frontend).

---

## 1. Database Setup (Render PostgreSQL)
The backend requires a persistent relational database. Render offers managed PostgreSQL instances.
1.  Go to [Render](https://render.com/) and sign in.
2.  Click **New +** and select **PostgreSQL**.
3.  Fill in the database configuration:
    *   **Name**: `staylio-db`
    *   **Database**: `staylio`
    *   **User**: `staylio_user`
    *   **Region**: Select a region close to you.
4.  Click **Create Database**.
5.  Wait for it to provision. Once active, copy the **Internal Database URL** or **External Database URL**. It will look similar to:
    `postgresql://staylio_user:your_password@dpg-xxxxxx.oregon-postgres.render.com/staylio`

---

## 2. Backend Setup (Render Web Service)
Because WebSockets require persistent TCP connections (Flask-SocketIO), serverless environments (like Vercel or AWS Lambda) will not work. Render Web Services provide persistent containers suited for WebSockets.
1.  On the Render Dashboard, click **New +** and select **Web Service**.
2.  Connect your GitHub repository.
3.  Configure the service details:
    *   **Name**: `staylio-backend`
    *   **Root Directory**: `backend`
    *   **Environment**: `Python`
    *   **Branch**: `main`
    *   **Build Command**:
        ```bash
        pip install -r requirements.txt
        ```
    *   **Start Command**:
        ```bash
        gunicorn --worker-class eventlet -w 1 app:app
        ```
4.  Open the **Advanced** section to add the required **Environment Variables**:
    *   `DATABASE_URL`: Set to the PostgreSQL Connection URL copied in Step 1.
    *   `SECRET_KEY`: Set to a long random session string.
    *   `JWT_SECRET_KEY`: Set to a long random encryption string.
    *   `OPENAI_API_KEY`: Set to your OpenAI API key (or omit/leave blank to use the deterministic rules fallback matching engine).
    *   `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_DEFAULT_SENDER`: Your SMTP server settings (e.g. Mailtrap or SendGrid) for sending matching emails.
5.  Click **Create Web Service**. 
6.  Once deployed, Render will provide a live public URL (e.g., `https://staylio-backend.onrender.com`). Copy this URL.

---

## 3. Frontend Setup (Vercel)
The React client is built with Vite. It compiles to static files, making Vercel the ideal global hosting platform.
1.  Go to [Vercel](https://vercel.com/) and sign in.
2.  Click **Add New...** and select **Project**.
3.  Import your GitHub repository.
4.  Configure the deployment:
    *   **Framework Preset**: `Vite`
    *   **Root Directory**: `frontend`
    *   **Build Command**: `npm run build`
    *   **Output Directory**: `dist`
5.  Open the **Environment Variables** section and add the target API url:
    *   **Key**: `VITE_API_URL`
    *   **Value**: Your Render live backend URL (e.g., `https://staylio-backend.onrender.com`)
6.  Click **Deploy**. Vercel will compile the React code and serve it at a public URL (e.g. `https://staylio.vercel.app`).
