# 🔬 TelePharm Insights

**An End-to-End Data Product: From Raw Telegram Data to an Analytical API**

---

## 📌 Project Overview

**TelePharm Insights** is a robust data platform designed to extract, transform, and expose insights about **Ethiopian medical businesses** by scraping public Telegram channels.

This project answers critical questions for stakeholders:
- 🧪 **What are the top mentioned medical products and drugs?**
- 💰 **How does price and availability vary by channel?**
- 🖼️ **Which channels share the most visual content (images)?**
- 📈 **What are the daily & weekly trends in health-related posts?**

---

## ⚙️ Tech Stack

| 🔗 Layer | 📚 Tools |
|----------|----------------|
| **Orchestration** | [Dagster](https://dagster.io/) |
| **ELT & Data Modeling** | [dbt](https://www.getdbt.com/) |
| **Database** | PostgreSQL |
| **Scraping** | [Telethon](https://docs.telethon.dev/) |
| **Data Enrichment** | [YOLOv8](https://docs.ultralytics.com/) |
| **API** | [FastAPI](https://fastapi.tiangolo.com/) |
| **Containerization** | Docker, Docker Compose |
| **Secrets Management** | python-dotenv |

---

## ✅ Current Progress

| 🗂️ Task | ✅ Status | 📌 Description |
|----------------------|-----------|----------------------------|
| **Task 0** | ✔️ Completed | 📁 **Project structure**, environment management, Docker setup, secure `.env` secrets. |
| **Task 1** | ✔️ Completed | Telegram scraping with raw JSON, images, partitioned by date & channel, robust logging. |
| **Task 2** | ⏳ Upcoming | dbt star schema models, staging and marts |
| **Task 3** | ⏳ Upcoming | Data enrichment with YOLOv8 |
| **Task 4** | ⏳ Upcoming | Exposing insights via FastAPI |
| **Task 5** | ⏳ Upcoming | Orchestration with Dagster |

---

## 🗃️ Project Structure

```
telepharm_insights/
├── data/
│   ├── raw/            # Data lake: raw Telegram JSONs
│   ├── staging/
│   └── marts/
├── dbt/                # dbt transformation project
├── dags/               # Dagster pipeline definitions
├── api/                # FastAPI source code
├── scripts/            # Telegram scraper, YOLO enrichment, loaders
├── .env                # Secrets & credentials (GIT IGNORED!)
├── .gitignore
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── README.md
```

---

## 🚀 Local Development

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/telepharm_insights.git
cd telepharm_insights
```

### 2️⃣ Create your `.env`

```dotenv
TELEGRAM_API_ID=xxxxxx
TELEGRAM_API_HASH=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
POSTGRES_USER=postgres
POSTGRES_PASSWORD=yourpassword
POSTGRES_DB=telepharm_db
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

**Note:** `.env` is **never committed**. Manage secrets safely!

---

### 3️⃣ Run with Docker

```bash
docker-compose -f docker/docker-compose.yml up --build
```

This spins up:
- 🐘 **PostgreSQL** database
- ⚡ **FastAPI** app (API scaffolding — future tasks)
- 📦 Python environment with all dependencies installed

---

## 📌 Task 0: Project Setup & Environment

✅ **Highlights**
- Professional structure for a reproducible, production-grade pipeline.
- Managed all secrets with `.env` + `python-dotenv`.
- Dockerized environment guarantees portability.
- PostgreSQL container for robust ELT development.
- Version control ready with `.gitignore` hygiene.

---

## 📌 Task 1 — Data Scraping & Collection

**Status:** ✔️ Completed

**Description:**
- Developed a robust **Telegram Scraper** using **Telethon**.
- Extracted messages from multiple Ethiopian medical channels:
  - `Chemed123`
  - `lobelia4cosmetics`
  - `tikvahpharma`
- Collected **text messages** and **downloaded images** where available.
- Stored **raw JSON data** in a clear, **partitioned Data Lake** structure:

```data/raw/telegram_messages/YYYY-MM-DD/channel_name/channel_name.json```

- Implemented **logging** with:
- Channel name & scrape date.
- Errors & rate limit handling.
- Download status for images.
- Ensured data format is **dbt-ready** for next steps:
- Flat JSON records.
- Clean fields for fact & dimension modeling.


## ✨ Upcoming Tasks

✅ **Next:**
- **Task 2** Data Modeling and Transformation (Transform)
  - Raw JSON will be loaded to PostgreSQL
  - transformed with **dbt** star schema models

---

## 💡 Key Learning Areas

> This repo demonstrates practical skills in:
> - Cloud-native ELT
> - dbt transformations & testing
> - Computer Vision integration (YOLOv8)
> - API design with FastAPI
> - Orchestration with Dagster
> - Secure, reproducible Docker workflows

---
