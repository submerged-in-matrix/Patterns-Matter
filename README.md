<div align="center">

# 🎸 Patterns Matter

**A personal RDBMS proof-of-concept database for  documenting own work in a custom mapping.**

[![Live App](https://img.shields.io/badge/Live-patterns--matter.fly.dev-blueviolet)](https://patterns-matter.fly.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*Data-driven insights in Materials Science and Music are both patterns — hence the name.*

[**Explore the Database →**](https://patterns-matter.fly.dev/)

</div>

---

## Why This Exists

Every ML project in materials science follows the same arc: **raw data → featurization → model → results**. But datasets scatter across Jupyter notebooks, Google Drive folders, and local directories. Results lose their link to the exact feature matrix that produced them. 

**Patterns Matter** is a toy-scale but architecturally deliberate relational database that solves this by mapping the full pipeline — `Raw Data → Featurized Data → Results` — as first-class, queryable records. Every dataset entry links to its source, featurization method, and downstream results. Every result links back to the model and feature matrix that produced it.

And because patterns aren't exclusive to crystal structures — there's a music section too, housing original guitar clips and recordings. Different file types, same relational schema, one searchable interface.

## What's Inside

### Materials Database

Five material properties, each with dedicated **Dataset** and **Results** views tracking the full ML pipeline:

| Property | What's Tracked |
|---|---|
| **Band Gap** | Raw MP-API data, Matminer composition/structure featurization, RF/XGB/LGBM tuning results, SHAP analysis, Bayesian optimization comparisons, NL→SPARQL knowledge graph experiments |
| **Formation Energy** | Materials Project scrapes, Magpie-preset featurization, curated model-ready datasets |
| **Linear Elasticity** | Fabricated 2D dataset via Latin Hypercube Sampling, simulation results |
| **Melting Point** | Property-centric datasets with featurization pipeline artifacts |
| **Oxidation State** | Classification-ready datasets and model outputs |

Each record stores: filename, source, description, upload timestamp, storage backend (Google Drive), and direct view/download links.

### Music & Guitar Clips

Original recordings and covers — session playing, solo guitar pieces, spontaneous tributes — served from the same relational backend. Included partly for fun, partly to stress-test the schema with heterogeneous file types (audio vs. CSV vs. PNG).

## Architecture

This is intentionally a **proof-of-concept RDBMS**, not a production data platform. The point is to demonstrate:

- **Relational modeling** of the ML pipeline lifecycle (raw → featurized → results) with proper foreign-key-like linkage between stages
- **Search by key** across both materials properties and clip metadata from a single interface
- **Admin-gated uploads** with metadata capture at ingest time and SQL query to the database.
- **Hybrid storage** — metadata lives in the database, heavy files live on Google Drive, the app stitches them together at query time
- **Deployment on Fly.io** as a lightweight, always-on web service

```
patterns-matter.fly.dev
├── /materials
│   ├── /bandgap           ── dataset | results    (22 files)
│   ├── /formation_energy  ── dataset | results     (9 files)
│   ├── /linear_elasticity ── dataset | results    (16 files)
│   ├── /melting_point     ── dataset | results    (14 files)
│   └── /oxidation_state   ── dataset | results    (14 files)
├── /clips                 ── audio previews & downloads
├── /keys                  ── searchable index of all entries
└── /login                 ── admin interface for uploads
```

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python (Flask / similar lightweight framework) |
| **Database** | Relational DB (SQLite) |
| **File Storage** | Google Drive API (view + download links) |
| **Deployment** | Fly.io |
| **Frontend** | Server-rendered HTML with search |

## Usage

**Browse:** Visit [patterns-matter.fly.dev](https://patterns-matter.fly.dev/) and explore by material property or search by key.

**Download data:** Every file has direct Google Drive download links — use them for your own ML experiments. Please credit original sources (Materials Project, etc.) for raw data.

**Music:** For fun and personal listening. Non-commercial. Redistribution is okay, but don't reuse originals in your own compositions.

## What This Demonstrates

If you're here from a portfolio review, this project shows:

- Ability to **design a relational schema** that mirrors a real scientific workflow
- Understanding of **data provenance** — every result traces back to its feature matrix and raw source
- Practical **full-stack deployment** (database + file storage + web UI + cloud hosting)
- Thoughtful **metadata design** — not just dumping files, but capturing source, description, and temporal ordering

It's deliberately small. The architecture is what matters.

---

<div align="center">

**[patterns-matter.fly.dev](https://patterns-matter.fly.dev/)**

📬 sayeed.shahriar@gmail.com · [GitHub](https://github.com/submerged-in-matrix)

</div>
