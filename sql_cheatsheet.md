# SQL CRUD Cheatsheet — Patterns Matter Database

Your database has these main tables:

| Table | Purpose |
|---|---|
| `properties` | Materials property cards (Band Gap, Melting Point, …) |
| `uploads_log` | Files attached to each property (datasets & results) |
| `resources` | Guitar resource cards (Tabs Collection, Instructional, …) |
| `resource_files` | Files attached to each resource |

---

## 1. CREATE (INSERT) — Adding new rows

**Concept:** INSERT puts a new row into a table. You list which columns to fill and what values to give them.

```sql
INSERT INTO table_name (column1, column2, ...) VALUES (value1, value2, ...);
```

### Add a new materials property card

```sql
INSERT INTO properties (slug, display_name, description, visible)
VALUES ('thermal_conductivity', 'Thermal Conductivity', 'Thermal conductivity datasets', 1);
```

- `slug` — the URL-safe key (lowercase, underscores, no spaces)
- `display_name` — what shows on the card
- `description` — short text below the title
- `visible` — 1 = shown, 0 = hidden

### Add a new guitar resource card

```sql
INSERT INTO resources (slug, display_name, description, visible)
VALUES ('fingerstyle', 'Fingerstyle Studies', 'Fingerpicking exercises and pieces', 1);
```

### Add a file entry to a materials property

```sql
INSERT INTO uploads_log (property, tab, filename, uploaded_at, storage, drive_id, preview_url, download_url, source, description)
VALUES (
  'bandgap',
  'dataset',
  'band_gap_featurized.csv',
  CURRENT_TIMESTAMP,
  'drive',
  'YOUR_DRIVE_FILE_ID',
  'https://drive.google.com/file/d/YOUR_DRIVE_FILE_ID/preview',
  'https://drive.google.com/uc?export=download&id=YOUR_DRIVE_FILE_ID',
  'Materials Project',
  'Featurized band gap data from MP'
);
```

- `tab` — either `'dataset'` or `'results'`
- `storage` — always `'drive'` for Drive-backed files

### Add a file to a guitar resource

```sql
INSERT INTO resource_files (resource, filename, path, uploaded_at, drive_id, preview_url, download_url)
VALUES (
  'covers',
  'Blackbird.gp5',
  'Beatles/Blackbird.gp5',
  CURRENT_TIMESTAMP,
  'YOUR_DRIVE_FILE_ID',
  'https://drive.google.com/file/d/YOUR_DRIVE_FILE_ID/preview',
  'https://drive.google.com/uc?export=download&id=YOUR_DRIVE_FILE_ID'
);
```

- `path` — the folder structure shown in the accordion (e.g. `Beatles/Blackbird.gp5`)
- If the file is at root level, `path` = `filename`

### Avoid duplicates with INSERT OR IGNORE

If the row might already exist and you don't want an error:

```sql
INSERT OR IGNORE INTO resources (slug, display_name, description, visible)
VALUES ('fingerstyle', 'Fingerstyle Studies', 'Exercises', 1);
```

This silently skips if the unique constraint (slug) conflicts.

---

## 2. READ (SELECT) — Viewing data

**Concept:** SELECT retrieves rows. You choose which columns to see and which rows to filter.

### See everything in a table

```sql
SELECT * FROM properties;
SELECT * FROM resources;
SELECT * FROM uploads_log;
SELECT * FROM resource_files;
```

`*` means "all columns."

### See specific columns only

```sql
SELECT slug, display_name FROM properties;
```

### Filter rows with WHERE

```sql
-- All files for the bandgap property
SELECT filename, tab, source FROM uploads_log WHERE property = 'bandgap';

-- Only dataset files (not results)
SELECT filename FROM uploads_log WHERE property = 'bandgap' AND tab = 'dataset';

-- All files in a guitar resource
SELECT filename, path FROM resource_files WHERE resource = 'covers';
```

### Pattern matching with LIKE

`%` matches any sequence of characters.

```sql
-- Find files with 'featurized' anywhere in the name
SELECT * FROM uploads_log WHERE filename LIKE '%featurized%';

-- Find all .gp5 files
SELECT * FROM resource_files WHERE filename LIKE '%.gp5';

-- Find resources with paths containing 'Beatles'
SELECT * FROM resource_files WHERE path LIKE '%Beatles%';
```

### Count rows

```sql
-- How many files per property?
SELECT property, COUNT(*) AS file_count FROM uploads_log GROUP BY property;

-- How many files per resource?
SELECT resource, COUNT(*) AS file_count FROM resource_files GROUP BY resource;

-- Total files across everything
SELECT COUNT(*) FROM uploads_log;
```

### Sort results

```sql
-- Newest files first
SELECT filename, uploaded_at FROM uploads_log ORDER BY uploaded_at DESC;

-- Alphabetical
SELECT display_name FROM properties ORDER BY display_name ASC;
```

### Limit results

```sql
-- Just the first 10 rows
SELECT * FROM resource_files LIMIT 10;
```

### See all tables in the database

```sql
SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%';
```

### See a table's columns

```sql
PRAGMA table_info(resource_files);
```

---

## 3. UPDATE — Changing existing rows

**Concept:** UPDATE modifies columns in rows that match a WHERE condition. **Always include WHERE** — without it, every row in the table gets changed.

```sql
UPDATE table_name SET column1 = value1, column2 = value2 WHERE condition;
```

### Rename a property card

```sql
UPDATE properties SET display_name = 'Band Gap Energy' WHERE slug = 'bandgap';
```

### Change a property description

```sql
UPDATE properties SET description = 'Updated description here' WHERE slug = 'bandgap';
```

### Rename a guitar resource card

```sql
UPDATE resources SET display_name = 'Tabs Collection' WHERE slug = 'covers';
```

### Update description too

```sql
UPDATE resources
SET display_name = 'Tabs Collection',
    description = 'Guitar pro tabs for some of my favourite songs'
WHERE slug = 'covers';
```

### Hide a property without deleting it

```sql
UPDATE properties SET visible = 0 WHERE slug = 'oxidation_state';
```

To show it again:

```sql
UPDATE properties SET visible = 1 WHERE slug = 'oxidation_state';
```

### Fix a file's source or description

```sql
UPDATE uploads_log
SET source = 'AFLOW', description = 'Corrected source attribution'
WHERE property = 'bandgap' AND filename = 'band_gap_raw.csv';
```

### Fix a resource file's path (move it into a subfolder)

```sql
UPDATE resource_files
SET path = 'Fingerstyle/Blackbird.gp5'
WHERE resource = 'covers' AND filename = 'Blackbird.gp5';
```

### ⚠️ Common mistake — forgetting WHERE

```sql
-- DANGEROUS: changes EVERY row in the table
UPDATE properties SET visible = 0;

-- SAFE: changes only one row
UPDATE properties SET visible = 0 WHERE slug = 'oxidation_state';
```

Your SQL tool requires you to tick a confirmation checkbox for destructive queries, so you'll get a warning — but always double-check your WHERE clause.

---

## 4. DELETE — Removing rows

**Concept:** DELETE removes rows matching a condition. Like UPDATE, **always use WHERE** — without it, every row is deleted.

```sql
DELETE FROM table_name WHERE condition;
```

### Delete a specific file from a property

```sql
DELETE FROM uploads_log
WHERE property = 'bandgap' AND tab = 'dataset' AND filename = 'old_file.csv';
```

### Delete ALL files for a property (keep the card)

```sql
DELETE FROM uploads_log WHERE property = 'bandgap';
```

### Delete a property card AND its files

```sql
DELETE FROM uploads_log WHERE property = 'thermal_conductivity';
DELETE FROM properties WHERE slug = 'thermal_conductivity';
```

Run both statements together (separated by `;`). Order matters — delete files first, then the card.

### Delete a specific resource file

```sql
DELETE FROM resource_files
WHERE resource = 'covers' AND filename = 'Blackbird.gp5';
```

### Delete ALL files for a resource (keep the card)

```sql
DELETE FROM resource_files WHERE resource = 'covers';
```

### Delete a resource card AND its files

```sql
DELETE FROM resource_files WHERE resource = 'fingerstyle';
DELETE FROM resources WHERE slug = 'fingerstyle';
```

### Delete an entire table (irreversible)

```sql
DROP TABLE IF EXISTS old_table_name;
```

### Preview before deleting

Always SELECT first to see what you're about to remove:

```sql
-- Check what will be deleted
SELECT * FROM uploads_log WHERE property = 'bandgap' AND tab = 'results';

-- If that looks right, delete
DELETE FROM uploads_log WHERE property = 'bandgap' AND tab = 'results';
```

---

## Quick Reference

| Task | SQL |
|---|---|
| List all tables | `SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';` |
| Show table columns | `PRAGMA table_info(table_name);` |
| See all rows | `SELECT * FROM table_name;` |
| Count rows | `SELECT COUNT(*) FROM table_name;` |
| Add a row | `INSERT INTO table_name (col1, col2) VALUES (val1, val2);` |
| Change a row | `UPDATE table_name SET col1 = val1 WHERE condition;` |
| Remove a row | `DELETE FROM table_name WHERE condition;` |
| Find by pattern | `SELECT * FROM table_name WHERE col LIKE '%text%';` |
| Sort results | `SELECT * FROM table_name ORDER BY col DESC;` |
| Limit output | `SELECT * FROM table_name LIMIT 10;` |

**Golden rules:**
1. Always preview with SELECT before UPDATE or DELETE.
2. Never run UPDATE or DELETE without WHERE (unless you mean every row).
3. Slugs are lowercase — `'bandgap'` not `'BandGap'`.
4. Strings go in single quotes: `'like this'`.
5. Multiple statements in one go: separate with `;`.
