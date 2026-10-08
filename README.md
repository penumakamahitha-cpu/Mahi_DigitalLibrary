# LibreFlow — Digital Library & E-Book Circulation Portal
**Django Full-Stack Capstone Project 3 • Student Assignment**

LibreFlow is a full-stack digital library and e-book circulation portal built using **Python 3 / Django 6.x**, **Bootstrap 5**, **SQLite (db.sqlite3)**, **WhiteNoise**, and **Gunicorn**, ready for zero-downtime deployment on **Render**.

---

## 🌟 Key Features

1. **Book Catalog & E-Book Inventory**:
   - Modern Bootstrap 5 grid with book covers, titles, authors, ISBN badges, and live inventory availability pills (`In Stock (X/Y)` vs `Out of Stock`).
   - Detailed individual book pages showing synopsis, author biography, and currently active borrowers.

2. **Instant Client-Side & Server Search (ES6+ JavaScript)**:
   - Live client-side instant filtering as you type across book title, author, ISBN, and genre.
   - Interactive genre filter pills (*Computer Science, History, Philosophy, Mystery, etc.*).
   - Live item counter showing matching titles in real time.

3. **Circulation Workflow (Book Issue)**:
   - **Strict inventory validation**: Prevents issuing books with zero available copies.
   - **Automated stock tracking**: Automatically decrements available copies upon checkout.
   - **Smart due-date engine**: Automatically calculates the default due date to **14 days** after issue date, with interactive preset buttons (+7, +14, +21, +30 days).

4. **Circulation Workflow (Book Return & Fine Settle)**:
   - Restores book inventory (increments available copies by 1).
   - **Dynamic overdue fine calculation**: Accurately computes overdue days and fines at the policy rate of **$1.00 per calendar day**.
   - Displays real-time status badges (*On Time ($0.00)* vs *Overdue Warning*).

5. **Patron / Member Dashboard**:
   - Directory of registered library members with active loan counters.
   - Individual member dashboards displaying:
     - Currently borrowed books with due dates.
     - **Pulsing Overdue Circulation Alerts** when any loan exceeds its due date.
     - Real-time estimated pending fines.
     - Complete past borrowing history with settled fines and return timestamps.

6. **Interactive Due-Date & Fine Calculator**:
   - Standalone interactive simulation tool.
   - Slide or choose loan duration, select issue date and return date, and view instant fine calculations and policy breakdowns.
   - Pre-configured test scenario buttons for quick demonstration.

7. **Django Admin Management**:
   - Full administration portal at `/admin/` with search, list filters, and autocomplete fields for Authors, Books, Members, and Circulation Records.

---

## 🏗️ Technology Stack

| Component | Technology |
|---|---|
| **Backend Framework** | Django 6.1 (Python 3.11+) |
| **Database** | SQLite (`db.sqlite3`) with Django ORM |
| **Frontend UI** | HTML5, CSS3 (Custom Design System), Bootstrap 5.3, Bootstrap Icons |
| **Frontend Logic** | JavaScript (ES6+) for instant search & reactive date/fine calculators |
| **WSGI Server** | Gunicorn 21.2+ |
| **Static File Serving** | WhiteNoise 6.12+ (`CompressedManifestStaticFilesStorage`) |
| **Cloud Deployment** | Render Blueprint (`render.yaml`) |

---

## 🗄️ Database Architecture

- **`Author`**:
  - `name`: Author's full name.
  - `biography`: Author biography and background.
- **`Book`**:
  - `title`, `author` (ForeignKey to `Author`), `isbn` (unique), `genre`, `description`, `total_copies`, `available_copies`, `cover_url`.
- **`Member`**:
  - `name`, `member_id` (unique, e.g., `MEM-1001`), `email` (unique), `phone`, `joined_date`.
- **`CirculationRecord`**:
  - `book` (ForeignKey to `Book`), `member` (ForeignKey to `Member`), `issue_date`, `due_date`, `return_date`, `fine_amount`, `returned` (boolean), `notes`.

---

## 🚀 Local Development Setup

### 1. Clone & Activate Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Apply Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Seed Initial Demonstration Data
```bash
python manage.py seed_library
```
*(Or run `python create_superuser.py` which sets up an admin user and seeds the data).*

### 5. Run Development Server
```bash
python manage.py runserver
```
Open **`http://127.0.0.1:8000/`** in your browser.

---

## 🔑 Default Credentials

- **Admin Portal**: `http://127.0.0.1:8000/admin/`
- **Username**: `admin`
- **Password**: `admin123`

---

## 🧪 Running Automated Unit Tests

The test suite covers model validation, 0-stock constraint enforcement, 14-day default due date generation, on-time returns, and overdue fine calculations:

```bash
python manage.py test
```

Expected output:
```text
Ran 7 tests in 0.163s
OK
```

---

## ☁️ Deployment to Render

The repository includes the standardized Render deployment configuration:

- **`render.yaml`**: Pre-configured Blueprint service.
- **`requirements.txt`**: Standard dependencies (`Django>=6.0`, `Gunicorn>=21.2.0`, `whitenoise>=6.6.0`).
- **`create_superuser.py`**: Automated script executed during build/start to ensure admin access and demonstration data.

### Exact Deployment Steps:
1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Prepare Digital Library Portal for Render deployment"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo-name>.git
   git push -u origin main
   ```
2. **Log into Render**:
   - Go to [dashboard.render.com](https://dashboard.render.com/).
   - Click **New +** → **Blueprint** (or **Web Service**).
   - Select your GitHub repository.
3. **Verify Settings**:
   - **Runtime**: Python 3.11+
   - **Root Directory**: `.`
   - **Build Command**:
     ```bash
     pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate && python create_superuser.py
     ```
   - **Start Command**:
     ```bash
     python manage.py migrate && python create_superuser.py && gunicorn Mahi.wsgi:application
     ```
4. **Environment Variables**:
   - `PYTHON_VERSION`: `3.11.0`
   - `RENDER`: `True`
   - `SECRET_KEY`: `your-production-secret-key`
   - *(Optional)* `DJANGO_SUPERUSER_USERNAME`: `admin`
   - *(Optional)* `DJANGO_SUPERUSER_PASSWORD`: `YourSecurePassword123!`
5. **Click Create Web Service** and access your live `https://<service-name>.onrender.com` URL once built.

> **Note on SQLite on Render**: SQLite (`db.sqlite3`) is used per the student assignment specifications. Free web services on Render feature an ephemeral filesystem, meaning SQLite records will reset upon service redeploy or restart. This is expected for this classroom demonstration project.
