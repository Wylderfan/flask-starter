# flask-starter

A clean, reusable Flask project template. Batteries included: app factory pattern, MySQL via SQLAlchemy, multi-profile support, Tailwind dark theme, Tailscale binding, backup/restore CLI, and systemd/OpenRC deploy templates.

Forked and stripped from [game-journal](https://github.com/Wylderfan/game-journal).

---

## What's included

- **App factory** pattern in `app/__init__.py`
- **Blueprint structure** — `main` (dashboard + profile switcher) and `items` (example CRUD)
- **Multi-profile support** — session-based, zero auth, profiles set via env var
- **MySQL + SQLAlchemy** with a single example `Item` model to copy-paste from
- **Dark Tailwind UI** — nav, flash messages, form pages — all consistent
- **`flask seed`** — wipes and re-seeds example data
- **`flask db-backup` / `flask db-restore`** — mysqldump wrappers
- **Tailscale binding** — `run.py` binds to `TAILSCALE_IP`, never `0.0.0.0`
- **Deploy templates** — systemd and OpenRC in `deploy/`

---

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy and fill in `.env`:

```bash
cp .env.example .env
```

| Variable | Description |
|---|---|
| `FLASK_SECRET_KEY` | Any random string |
| `DATABASE_URL` | `mysql+pymysql://user:password@host/dbname` |
| `FLASK_ENV` | `development` locally, `production` on server |
| `APP_NAME` | Displayed in nav and page titles (default: `My App`) |
| `TAILSCALE_IP` | Your Tailscale IP (`tailscale ip -4`) |
| `PORT` | Port to bind to (default: `5000`) |
| `PROFILES` | Comma-separated profile names (default: `Player 1`) |

Create tables:

```bash
flask shell
>>> from app import db, models
>>> db.create_all()
```

Seed with example items:

```bash
flask seed
```

Run (binds to `TAILSCALE_IP` if set, otherwise `127.0.0.1`):

```bash
python run.py
```

---

## Adding a blueprint

1. Create `app/blueprints/myfeature.py` with a `Blueprint`:

```python
from flask import Blueprint, render_template
from app.utils.helpers import current_profile

myfeature_bp = Blueprint("myfeature", __name__)

@myfeature_bp.route("/")
def index():
    profile = current_profile()
    return render_template("myfeature/index.html")
```

2. Register it in `app/__init__.py`:

```python
from app.blueprints.myfeature import myfeature_bp
app.register_blueprint(myfeature_bp, url_prefix="/myfeature")
```

3. Add a nav link in `app/templates/base.html`.

4. Create templates in `app/templates/myfeature/`.

---

## Adding a model

Add your model class to `app/models.py`. Always include `profile_id` to scope data per profile:

```python
class Widget(db.Model):
    __tablename__ = "widgets"

    id         = db.Column(db.Integer,     primary_key=True, autoincrement=True)
    profile_id = db.Column(db.String(100), nullable=False)
    name       = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime,    nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime,    nullable=False, default=datetime.utcnow,
                           onupdate=datetime.utcnow)
```

Then recreate tables (`db.create_all()` is safe to re-run — it skips existing tables) or use a migration.

---

## Profile system

Profiles are set in `.env` as a comma-separated list:

```
PROFILES=Alice,Bob
```

The active profile is stored in the Flask session. `current_profile()` from `app/utils/helpers.py` returns it:

```python
from app.utils.helpers import current_profile
profile = current_profile()  # "Alice"
```

All data queries should filter by `profile_id=profile`. The profile switcher in the nav is rendered automatically when more than one profile is configured.

---

## Backup and restore

```bash
# Dump to backups/<dbname>_<timestamp>.sql
flask db-backup

# Dump to a custom directory
flask db-backup --output-dir /path/to/backups

# Restore (prompts for confirmation)
flask db-restore backups/mydb_20260101_120000.sql

# Restore without prompt
flask db-restore backups/mydb_20260101_120000.sql --yes
```

Requires `mysqldump` / `mysql` client tools installed on the system.

---

## Tailscale binding

`run.py` reads `TAILSCALE_IP` from `.env` and binds gunicorn to that address. This means the app is only reachable from your Tailnet — no login system needed.

Get your Tailscale IP: `tailscale ip -4`

**Always use `python run.py` for dev, not `flask run`** — `flask run` ignores `TAILSCALE_IP` and binds to `127.0.0.1`.

---

## Production deployment

Edit `deploy/flask-starter.service` (systemd) or `deploy/flask-starter.openrc` (OpenRC), filling in your paths, username, Tailscale IP, and port. Then:

**systemd:**
```bash
sudo cp deploy/flask-starter.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now flask-starter
```

**OpenRC:**
```bash
sudo cp deploy/flask-starter.openrc /etc/init.d/flask-starter
sudo chmod +x /etc/init.d/flask-starter
sudo rc-update add flask-starter default
sudo rc-service flask-starter start
```

---

## Gotchas

- **`db.create_all()` creates no tables** if models haven't been imported first. The app factory handles this at runtime with `from app import models`. In a raw shell, do `from app import db, models` before `db.create_all()`.
- **`flask seed` wipes all data** before re-inserting. Do not run against a database with real data you want to keep.
- **MySQL lock wait timeout** in `flask shell` if a previous session left an open transaction. Exit all shells, wait a moment, retry.
