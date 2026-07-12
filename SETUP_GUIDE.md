# Staylio Setup & Installation Guide

Follow these steps to configure, build, and run the Staylio application locally.

---

## 1. Prerequisites
Ensure you have the following installed on your machine:
*   **Python**: 3.10 or higher
*   **Node.js**: v18.0 or higher
*   **npm**: package manager

---

## 2. Backend Installation & Setup

1.  Navigate to the backend directory:
    ```bash
    cd backend
    ```
2.  Create a virtual environment:
    ```bash
    python -m venv .venv
    ```
3.  Activate the virtual environment:
    *   **Windows**:
        ```powershell
        .venv\Scripts\Activate.ps1
        ```
    *   **macOS/Linux**:
        ```bash
        source .venv/bin/activate
        ```
4.  Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```
5.  Create your local `.env` configuration:
    *   Duplicate `.env.example` as `.env` and fill in your details:
        ```bash
        cp .env.example .env
        ```
6.  Start the backend Flask server:
    ```bash
    python app.py
    ```
    *The database tables will be automatically created on startup, and a default administrative account will be seeded:*
    *   **Email**: `admin@staylio.com`
    *   **Password**: `admin123`

---

## 3. Frontend Installation & Setup

1.  Open a new terminal window and navigate to the frontend directory:
    ```bash
    cd frontend
    ```
2.  Install the npm dependencies:
    ```bash
    npm install
    ```
3.  Start the local Vite development server:
    ```bash
    npm run dev
    ```
4.  Open your browser and navigate to the local client URL:
    *   **URL**: `http://localhost:5173`
