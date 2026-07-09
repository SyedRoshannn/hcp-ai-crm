# Setup & Installation Guide

This document provides a step-by-step setup guide for building, running, migrating, and testing the HCP AI CRM Assistant on a clean system.

---

## Prerequisites

Before setting up, ensure your system has:
- **Python**: Version 3.11 or higher (pip package manager must be available).
- **Node.js**: Version 18 or higher (npm package manager must be available).
- **PostgreSQL**: Version 15 or higher (running locally or remotely).
- **pgAdmin**: For PostgreSQL database inspection and management (optional).

---

## 1. Database Setup

### Step A: Create the PostgreSQL Database
Open your SQL console or pgAdmin client, connect to your server, and create the database:
```sql
CREATE DATABASE hcp_crm;
```

---

## 2. Backend Setup

### Step A: Create and Activate Virtual Environment
Open a terminal in the project's `backend/` directory:
```powershell
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate on Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Activate on Linux/macOS
source venv/bin/activate
```

### Step B: Install Python Dependencies
Install required packages from the requirements manifest:
```bash
pip install -r requirements.txt
```

### Step C: Configure Environment Variables
Create a file named `.env` in the `backend/` root directory and define the configuration values:
```env
# Database configuration
DATABASE_URL=postgresql://postgres:Syed01@localhost:5432/hcp_crm

# Groq AI Key and Model configuration
GROQ_API_KEY=your_groq_api_key_here
MODEL_NAME=llama-3.1-8b-instant

# FastAPI Server settings
PORT=8000
HOST=127.0.0.1
```

### Step D: Run Database Migrations
Deploy the database schema tables to your PostgreSQL server:
```bash
alembic upgrade head
```

### Step E: Run Backend Server
Start the FastAPI server:
```bash
python -m uvicorn app.main:app --reload --port 8000 --host 127.0.0.1
```

---

## 3. Frontend Setup

### Step A: Install Node Dependencies
Open a new terminal window in the project's `frontend/` directory:
```bash
cd frontend
npm install
```

### Step B: Start Vite Development Server
Launch the React development server:
```bash
npm run dev
```
*The app is now accessible in your browser at `http://localhost:5173/`.*

---

## 4. Verification & Testing

### Running Automated Test Suite
To execute all backend unit and integration tests (tests compile and run against the active database configuration):
```bash
# In backend directory with virtual environment active
python -m unittest discover -s tests
```

### Verification Outputs
- **API Health Check**: Accessing `http://127.0.0.1:8000/health` should return `{"backend": "healthy"}`.
- **Frontend Production Build**: Test compilation bundle outputs:
  ```bash
  # In frontend directory
  npm run build
  ```
