# Patterns Matter

**A toy-scale relational database documenting computational materials work under a single mapping: raw → featurized/processed → results.**

[![Live App](https://img.shields.io/badge/Live-patterns--matter.fly.dev-blueviolet)](https://patterns-matter.fly.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*Data-driven insight in materials science and in music both come down to finding patterns — hence the name.*

[**Explore the database →**](https://patterns-matter.fly.dev/)

</div>

---

## Purpose

Computational materials work produces artifacts at each stage of a pipeline — raw inputs, processed or featurized intermediates, and final results — but these scatter across notebooks, Drive folders, and local directories, and results lose their link to the exact input that produced them.

Patterns Matter maps that pipeline as queryable records. Each entry organizes its files under a common `raw → featurized/processed → results` structure, whether the underlying method is a machine-learning workflow, a first-principles calculation, or a molecular-dynamics simulation. The database began as an ML project archive and now spans DFT, MD, and a combined DFT-ML-MD pipeline, alongside a section for guitar tablatures and instructional material.

## Contents

### Materials database

Each entry has **Dataset** and **Results** views tracking its pipeline. Entries currently in the database:

| Entry | Method | Notes |
|---|---|---|
| **Band Gap** | ML | Materials Project data, Matminer composition/structure featurization, RF/XGB/LGBM tuning, SHAP analysis, Bayesian optimization |
| **Formation Energy** | ML | Materials Project scrapes, Magpie-preset featurization, curated model-ready datasets |
| **Melting Point** | ML | Property-centric datasets with featurization artifacts, stacking ensemble |
| **Oxidation State** | ML | Classification-ready datasets and model outputs |
| **Linear Elasticity** | PINN | Physics-informed neural network for 2D elasticity |
| **Knowledge Graph** | ML/NLP | Natural-language-to-SPARQL experiments over a band-gap knowledge graph |
| **Binary Alloys Fe-Cr** | DFT → ML → MD | Stress-strain DFT to extract elastic modulus E, surrogate models built on the results, and a nanoindentation study extracting the Oliver-Pharr reduced modulus |
| **Dirac Cone Stability of Graphene** | DFT | Electronic-structure study of the graphene Dirac cone |
| **Electronic Structure of Si** | DFT | First-principles electronic-structure calculation |
| **Mechanical Response of Si Nanowire** | MD | Molecular-dynamics study of nanowire mechanical response |
| **EMA-GNN** | ML | A Gnome inspired GNN to predict stability of materials |
| **Thermal Conductivity of bulk-Si** | MD | Molecular-dynamics thermal-conductivity study |
| **Masterarbeit** | — | Master's thesis materials |

Each record stores filename, source, description, upload timestamp, storage backend, and direct view/download links.

### Guitar resources

Guitar tablatures and instructional material, organized into collections and served from the same backend. Original compositions are not tabbed yet — they are under studio production and will be added once complete. Files are grouped into a folder tree that mirrors their Drive structure.

## Architecture

A proof-of-concept RDBMS rather than a production data platform. It demonstrates:

- **Relational modeling** of the pipeline lifecycle (raw → featurized/processed → results), applied consistently across ML, DFT, and MD entries
- **Search by key** across materials entries and resource collections from a single interface
- **Admin-gated uploads** with metadata capture at ingest, plus a SQL query interface to the database
- **Hybrid storage** — metadata in the database, files on Google Drive, stitched together at query time
- **Deployment on Fly.io** as a lightweight web service

```
patterns-matter.fly.dev
├── /materials
│   ├── /bandgap                        ── dataset | results
│   ├── /formation_energy               ── dataset | results
│   ├── /melting_point                  ── dataset | results
│   ├── /oxidation_state                ── dataset | results
│   ├── /linear_elasticity              ── dataset | results   (PINN)
│   ├── /knowledge_graph                ── dataset | results
│   ├── /binary_alloys_fe_cr            ── dataset | results   (DFT-ML-MD)
│   ├── /dirac_cone_graphene            ── dataset | results   (DFT)
│   ├── /electronic_structure_si        ── dataset | results   (DFT)
│   ├── /si_nanowire_mechanical         ── dataset | results   (MD)
│   ├── /thermal_conductivity_bulk_si   ── dataset | results   (MD)
│   └── /masterarbeit                   ── dataset | results
├── /resources                          ── guitar tablatures & instructional material
├── /keys                               ── searchable index of all entries
└── /login                              ── admin interface for uploads
```

## Tech stack

| Layer | Technology |
|---|---|
| **Backend** | Python (Flask) |
| **Database** | SQLite |
| **File storage** | Google Drive API (view + download links) |
| **Deployment** | Fly.io |
| **Frontend** | Server-rendered HTML with search |

## Usage

**Browse:** Visit [patterns-matter.fly.dev](https://patterns-matter.fly.dev/) and explore by entry or search by key.

**Download data:** Files carry direct Google Drive download links. Please credit original sources (Materials Project and others) for raw data.

**Resources:** Tablatures and instructional material are free to download. Non-commercial; redistribution is fine, but originals are not to be reused in other compositions.

---

<div align="center">

**[patterns-matter.fly.dev](https://patterns-matter.fly.dev/)**

sayeed.shahriar@gmail.com · [GitHub](https://github.com/submerged-in-matrix)

</div>
