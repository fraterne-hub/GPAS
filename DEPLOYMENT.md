# GARL – Render Deployment Guide

## Why uploaded files disappeared

Render's filesystem is **ephemeral** — every time your service restarts or
redeploys, any files written to disk (uploaded images, documents, etc.) are
wiped. The PostgreSQL database persists, but local `media/` uploads do not.

The fix is to store media files in **Cloudinary** (free tier). Files are
uploaded directly from Django to Cloudinary and served from Cloudinary's CDN,
so they survive restarts forever.

---

## Step 1 – Create a free Cloudinary account

1. Go to <https://cloudinary.com> and sign up (free, no credit card).
2. Open your **Dashboard** → copy the **API Environment variable**. It looks like:
   ```
   cloudinary://<API_KEY>:<API_SECRET>@<CLOUD_NAME>
   ```

---

## Step 2 – Set environment variables on Render

In your Render service → **Environment** tab, add / confirm these variables:

| Variable | Value |
|---|---|
| `SECRET_KEY` | a long random string |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `yourapp.onrender.com` |
| `CSRF_TRUSTED_ORIGINS` | `https://yourapp.onrender.com` |
| `DATABASE_URL` | set automatically by Render when PostgreSQL is attached |
| `CLOUDINARY_URL` | `cloudinary://<key>:<secret>@<cloud>` ← paste from step 1 |
| `SITE_URL` | `https://yourapp.onrender.com` |

> **DATABASE_URL** is injected automatically by Render when you attach a
> PostgreSQL database to the service. You don't need to set it manually.

---

## Step 3 – Attach a PostgreSQL database (if not done yet)

1. Render Dashboard → **New** → **PostgreSQL**.
2. After it's created, go to your web service → **Environment** →
   **Add from Database** → select the database.  
   Render will inject `DATABASE_URL` automatically.

---

## Step 4 – Deploy

Push your changes to the connected Git branch. Render will run `build.sh`
automatically:

```bash
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
```

---

## Local development (SQLite3, no Cloudinary)

Just copy `.env.example` to `.env` and leave `DATABASE_URL` and
`CLOUDINARY_URL` empty:

```bash
cp .env.example .env
python manage.py runserver
```

- **Database** → `db.sqlite3` (local SQLite3)
- **Media files** → `media/` folder, served by Django dev server

No Cloudinary account needed for local work.

---

## How the logic works (summary)

```
CLOUDINARY_URL set?
  YES  →  DEFAULT_FILE_STORAGE = Cloudinary  (production)
  NO   →  DEFAULT_FILE_STORAGE = local disk  (development)

DATABASE_URL set?
  YES  →  PostgreSQL                          (production / Render)
  NO   →  SQLite3                             (local development)
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Images not showing on Render | `CLOUDINARY_URL` not set | Add it in Render Environment tab |
| 500 error on Render | `DATABASE_URL` missing | Attach a PostgreSQL DB in Render |
| CSRF / 403 on POST forms | `CSRF_TRUSTED_ORIGINS` wrong | Set it to `https://yourapp.onrender.com` |
| Static CSS/JS missing | `collectstatic` not run | Render runs `build.sh` automatically |
| Old images gone after re-deploy | Was using local storage | Set `CLOUDINARY_URL` and re-upload |
