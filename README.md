## 🔧 Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![HTML](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)



# Patterns Matter — Materials Database (Flask + Google Drive + SQLite) 🧪

## 1) Overview (Implementation Perspective)

**Patterns Matter** is a lightweight materials database web app built with **Flask** and **Jinja**, deployed on **Fly.io**.  
It renders datasets and result artifacts *directly from Google Drive* (service account), while keeping a small **SQLite** catalog (`uploads_log`) and an **audit trail** (`uploads_audit`) on a persistent Fly volume mounted at `/data`. No large files live in the VM—Drive is the source of truth for files.

### High-level
- **Frontend:** HTML + Jinja templates + a thin CSS theme.  
- **Backend:** Flask (Gunicorn worker), SQLite for metadata, Google Drive API for file storage, and a few background-style “run once” tasks guarded by a lock.
- **Persistence:** A Fly volume mounted at **`/data`** holds the SQLite DB and small assets (e.g., music clips and logs). Large datasets/results are kept on **Google Drive**.
- **Auth:** Simple admin session with password (env-configurable in app code). Public routes are read-only.
- **Health checks:** `/healthz` responds `200 OK` for Fly health probes.
- **Secrets:** `GDRIVE_SA_JSON_BASE64` (or `GDRIVE_SA_JSON`) and `GDRIVE_ROOT_FOLDER_ID` are stored as **Fly secrets**.

### What changed during the migration
- Was originally **Git-backed + local uploads folder**; now the app uses **Google Drive** as the primary data store for *materials datasets/results*.  
- The SQLite catalog (`uploads_log`) is **metadata only** (filename, Drive IDs, preview/download URLs, descriptions).  
- Admin **uploads** (ZIP or folder link) write files to Drive and **upsert** metadata into the catalog.  
- Public **views** read from Drive (or from local DB tables for legacy CSV/NPY still shipped in the repo).

---

## 2) Key Takeaways (Learner Perspective)

I tried to  touch almost every layer of a modern web service. Here’s a recap by technology and the concrete techniques used.

### HTML / CSS / Jinja (Templating)
- **HTML structure**: semantic tags (`<table>`, `<form>`, `<input>`, `<a>`, `<button>`) and responsive wrappers.
- **CSS**: simple layout, table styling, “pills”, hover states, small screen tweaks (`@media`).
- **Jinja**: 
  - Control flow and filters: `{% if %}`, `{% for %}`, `|title`, `|length`, `|safe`.
  - Template variables from Flask: `render_template("view.html", uploads=uploads, admin=is_admin, ...)`.
  - URL building: `url_for('property_detail', property_name=p, tab='results')` – avoids hardcoding links.
  - Defensive rendering: `row.get('storage', 'local')`, `COALESCE()` at SQL-layer to keep templates robust.
- performing CRUD using SQL with my sql_query tool.

**Mental Model:** Jinja renders **server-side**. I pass Python objects, Jinja turns them into HTML. Keep logic light in templates; do data prep in views.

---

### Flask (Backend)
- **Routes**: `@app.route('/materials/<property_name>/<tab>', methods=['GET', 'POST'])` with guards and branching:
  - Admin POST handlers: add Drive file, link Drive folder (recursive listing), ZIP upload → Drive, inline edits.
  - Public GET: query `uploads_log`, compute `table_map` for legacy local CSV/NPY tables.
- **Helpers**: 
  - `get_drive_service()` (lazy import, env-driven), 
  - `_drive_extract_id()`, `drive_list_folder_files(..., recursive=True)`,
  - `drive_ensure_property_tab_folder()` (ensures `<root>/<property>/<tab>`), 
  - `drive_upload_bytes()`, `_drive_urls()`,
  - `file_to_table_name()` (canonicalizes filenames to SQLite-safe table names).
- **Sessions**: `session['admin'] = True` on login; guards like `if not session.get('admin')` for admin routes.
- **Rendering**: `render_template()`, `redirect()`, `url_for()`, `jsonify()`.
- **Startup safety**: a run-once initialization guarded by a **`Lock`** and a module-level boolean to avoid duplicate schema work:
  - `ensure_uploads_log_schema()` ensures tables & triggers.
  - `ensure_uploads_log_columns()` backfills columns on older DBs.
- **Error handling**: wrap critical steps in `try/except` and log warnings instead of crashing public pages.

**How to build a route (minimum):**
```python
@app.route("/path", methods=["GET","POST"])
def view_func():
    # 1) read from request (form/args/session)
    # 2) domain work (query/drive/api)
    # 3) render_template(...) or redirect/url_for(...)
```

---

### SQLite (SQL, Indices, Triggers)
- **Schema**:
  - `uploads_log(property, tab, filename, uploaded_at, storage, drive_id, preview_url, download_url, source, description)`
  - `uploads_audit(property, tab, filename, action, at)`
- **Triggers** keep a **history** automatically:
  - On INSERT → action `add`
  - On UPDATE → action `update`
  - On DELETE → action `delete`
- **Upserts** evolved for compatibility: safe `UPDATE...; if rowcount==0 INSERT...` pattern to avoid `ON CONFLICT` errors on older SQLite or missing indices.
- **Dedupe tools**: optional admin endpoint to delete duplicates and re-create a unique index on `(property, tab, filename)`.
- **Queries**: COALESCE defensive selection; pagination unnecessary due to table size but can be added.

**Mental Model:** Treat SQLite as a **metadata ledger**. Big binaries live elsewhere (Drive).

---

### Google Drive API (Service Account)
- **Service account** credentials come from `GDRIVE_SA_JSON_BASE64` *(or `GDRIVE_SA_JSON` path)*.
- **Root folder** for the app is `GDRIVE_ROOT_FOLDER_ID`. Under it the app creates/uses the hierarchy:
  - `<root>/<property>/<tab>` where `tab ∈ {dataset, results}`.
- **Listing**: `drive_list_folder_files(..., recursive=True)` walks folders; filters by allowed extensions per tab.
- **Upload**: `drive_upload_bytes(service, folder_id, filename, bytes)`.
- **Sharing**: Best-effort `permissions().create(fileId, body={"role": "reader", "type": "anyone"})` for public links.
- **URLs**: preview and download links are computed and stored in the catalog.

**Mental Model:** Drive is your **blob store**. SQLite stores **pointers and descriptive metadata**.

---

### Containers & Dockerfile (Deployment Mechanics)
- The app runs behind **Gunicorn** in a **Firecracker VM** on Fly.
- **Dockerfile** defines your Python environment (packages like `google-api-python-client`, `pandas`, etc.).
- The container exposes port **8080**; Fly proxies 80/443 to it.
- **Health check**: `/healthz` must be very fast and never fail.
- **Volume**: `/data` mount stores the SQLite DB and small local assets. Fly restarts won’t erase your DB.
- **fly.toml** highlights:
  - `internal_port = 8080`
  - `[[http_service.checks]] path="/healthz"`
  - `[[mounts]] destination = "/data"`

**Mental Model:** Image (code + deps) → Machine (VM) → Volume for persistence → Health checks to keep it alive.

---

## 3) Architecture & Data Flow

- **Public user** visits `/materials/<property>/<tab>`
  - Flask queries `uploads_log` → Jinja renders a table of files
  - For **Drive** rows: show **Preview** and **Download** links directly to Drive
  - For legacy **local CSV/NPY**: map to an SQLite table name and render with `public_view`
- **Admin**:
  - **Add Drive file** (link/ID) → write row in `uploads_log`
  - **Link a Drive folder** → enumerate files and upsert rows
  - **ZIP upload → Drive** → (optional) expand in memory, upload each file to Drive, upsert rows
  - **Inline edit** → updates source/description
  - Triggers populate `uploads_audit` for the **Admin Dashboard**
- **Startup**:
  - `ensure_uploads_log_schema()` creates tables + triggers (idempotent).
  - `ensure_uploads_log_columns()` backfills missing columns on old DBs.

See diagram: **[architecture_diagram.png](./architecture_diagram.png)**

---

## 4) Environment & Secrets

Set on Fly (examples):
- `GDRIVE_SA_JSON_BASE64` — base64 of the service account JSON
- `GDRIVE_ROOT_FOLDER_ID` — ID of the shared folder where the app writes `<property>/<tab>` subfolders

Check with:
```bash
fly secrets list -a <app-name>
```

---

## 5) Local Development

```bash
python -m venv .venv
source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
export FLASK_APP=app.py
flask run
```

To simulate Drive locally, you can keep a small `uploads/` tree and use the “legacy” local CSV/NPY view routes, or configure real Drive secrets in your shell environment.

---

## 6) Operations Cheat Sheet

- **Health**: open `/healthz`
- **Admin login**: `/login` → set `session['admin']`
- **Admin home**: `/admin`
- **Repair duplicates**: optional endpoint that deletes dupes and re-creates index (if present in your code)
- **Logs**: `fly logs -a <app>`
- **Secrets**: `fly secrets set KEY=VALUE -a <app>`

---

## 7) Troubleshooting Nuggets

- `ON CONFLICT does not match any PRIMARY KEY or UNIQUE`  
  → Use the **UPDATE→INSERT** upsert pattern or ensure the unique index on `(property, tab, filename)` exists.
- `storageQuotaExceeded` for service accounts  
  → Use **Shared Drive** with delegated permissions, or link existing files/folders instead of uploading large binaries.
- 503/BuildError on `url_for('public_view', table=...)`  
  → Ensure `table_map.get(filename)` returns a non-empty value before rendering the link.
- Duplicates in lists  
  → Deduplicate in SQL and/or by using `DISTINCT`/proper unique index; also avoid adding local rows for Drive-backed items.

---

## 8) probable extensions

- OAuth user uploads (end-user Drive).
- Server-side previews for large CSVs (streamed, chunked).
- Role-based admin, audit export, and better search/filter UI.
- Background jobs for Drive sync.

---


### Appendix: Function Index (quick map)
- **Drive**: `get_drive_service`, `_drive_extract_id`, `drive_find_or_create_folder`, `drive_ensure_property_tab_folder`, `drive_list_folder_files`, `drive_upload_bytes`, `_drive_urls`
- **DB**: `ensure_uploads_log_schema`, `ensure_uploads_log_columns`, `dedupe_uploads_log`
- **Public/Admin**: `/materials/<property>/<tab>`, `/admin`, `/healthz`, optional `/admin/repair_uploads`
- **Legacy import**: `auto_import_uploads`, `auto_log_material_files`
- **Utilities**: `file_to_table_name`, `tableize_basename`

---



![Architecture Diagram](architecture_diagram.png)
