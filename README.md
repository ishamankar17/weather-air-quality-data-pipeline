# 🌦️ Weather & Air Quality Data Pipeline

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![PySpark](https://img.shields.io/badge/PySpark-E25A1C?logo=apachespark&logoColor=white)
![BigQuery](https://img.shields.io/badge/BigQuery-4285F4?logo=googlebigquery&logoColor=white)
![dbt](https://img.shields.io/badge/dbt-FF694B?logo=dbt&logoColor=white)
![Airflow](https://img.shields.io/badge/Airflow-017CEE?logo=apacheairflow&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)

An end-to-end data engineering project that ingests hourly weather and air-quality data for **Pune** from the Open-Meteo API, cleans and validates it with **PySpark**, loads it into **Google BigQuery**, models it with **dbt**, orchestrates everything with **Apache Airflow**, and serves insights through an interactive **Streamlit** dashboard.

---


## Architecture

```mermaid
flowchart LR
    A["Open-Meteo API"] --> B["Python Ingestion"]
    B --> C[("Raw JSON")]
    C --> D["PySpark Cleaning"]
    D --> E["Data Validation"]
    E --> F[("BigQuery")]
    F --> G["dbt Models & Tests"]
    G --> H["Daily Analytics"]
    H --> I["Streamlit Dashboard"]

    J["Apache Airflow"] -. Orchestrates .-> B
    J -.-> D
    J -.-> E
    J -. Runs dbt .-> G

    style A fill:#DCEAFE,stroke:#2563EB,color:#111827
    style B fill:#DCEAFE,stroke:#2563EB,color:#111827
    style C fill:#DCEAFE,stroke:#2563EB,color:#111827
    style D fill:#D1FAE5,stroke:#059669,color:#111827
    style E fill:#D1FAE5,stroke:#059669,color:#111827
    style F fill:#FEF3C7,stroke:#D97706,color:#111827
    style G fill:#FEF3C7,stroke:#D97706,color:#111827
    style H fill:#FEF3C7,stroke:#D97706,color:#111827
    style I fill:#FCE7F3,stroke:#DB2777,color:#111827
    style J fill:#EDE9FE,stroke:#7C3AED,color:#111827
```

---

##  Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Ingestion | Python | API calls and pipeline logic |
| Processing | PySpark | Cleaning, deduplication, validation |
| Warehouse | Google BigQuery | Cloud data storage |
| Transformation | dbt | SQL models and data tests |
| Orchestration | Apache Airflow | Scheduling and dependency management |
| Environment | Docker | Containerized, reproducible setup |
| Visualization | Streamlit & Plotly | Interactive dashboard |

---

## 📊 Key Features

-  **Hourly data** for weather and air quality in Pune
-  **Robust cleaning**: duplicate removal and schema validation with PySpark
-  **BigQuery warehouse** with analytical models
-  **dbt staging and daily aggregation models**, backed by data tests
-  **Airflow DAG** that automates the full workflow end to end
-  **Interactive dashboard** with KPI cards, trend charts, AQI categories, date filters, and cross-filtering

---

##  Pipeline Stages

| # | Stage | Description |
|---|---|---|
| 1 | **Ingest** | Fetch hourly weather and air-quality data from Open-Meteo and store as raw JSON |
| 2 | **Clean** | Standardize types, handle nulls, and remove duplicates using PySpark |
| 3 | **Validate** | Run quality checks before anything is loaded |
| 4 | **Load** | Write validated data to BigQuery |
| 5 | **Transform** | Build dbt staging and daily aggregate models, and run dbt tests |
| 6 | **Visualize** | Explore results in the Streamlit dashboard |

---



### Prerequisites

- Python 3.10+
- Docker and Docker Compose
- A Google Cloud project with BigQuery enabled
- Google Cloud authentication configured for BigQuery access



##  Future Improvements

- Add more cities and a city selector in the dashboard
- Introduce incremental loading in BigQuery
- Add alerting for pipeline failures and poor AQI levels
- Deploy the dashboard to Streamlit Community Cloud or Cloud Run

---

## 🌐 Data Source

Weather and air-quality data is provided by the [Open-Meteo API](https://open-meteo.com/).

