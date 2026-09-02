# 🛡️ Real-Time Financial Fraud Detection System

An end-to-end, containerized machine learning application designed to detect fraudulent financial transactions in real time using an optimized **XGBoost** classification pipeline. Built with a decoupled **FastAPI** backend inference engine and an interactive **Streamlit** user interface.

---

## 📌 Table of Contents
- [Architecture](#-architecture)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Local Development Setup](#-local-development-setup)
- [Docker Deployment](#-docker-deployment)
- [API Reference](#-api-reference)

---

## 🏗 Architecture

The system follows a microservice architecture packaged into a single container using an orchestration script (`start.sh`):

1. **Frontend (Streamlit):** Collects transaction details, performs client-side feature engineering, and issues asynchronous HTTP POST requests to the backend API.
2. **Backend (FastAPI):** Validates incoming JSON payloads via Pydantic, passes processed features through the loaded `.joblib` XGBoost pipeline, and evaluates risk probability against a pre-calibrated decision threshold.

---

## ✨ Key Features

- **Real-Time Fraud Evaluation:** Computes precise risk probability scores and outputs instant decision verdicts (`FRAUD DETECTED` vs `TRANSACTION CLEAN`).
- **Automated Feature Engineering:** Dynamically generates balance error metrics (`errorBalanceOrig`, `errorBalanceDest`), zero-balance flags, transaction-to-balance ratios, and temporal cyclic features (`hour_of_day`).
- **Dynamic Thresholding:** Utilizes metadata-driven thresholding (`0.9976`) optimized for highly imbalanced transaction datasets.
- **Payload Inspector:** Includes an interactive JSON expansion panel to review transmitted feature payloads and raw API responses.
- **Zero-Cost Deployment Ready:** Pre-configured with a custom `Dockerfile` and `start.sh` launcher ready for zero-cost hosting on platforms like Hugging Face Spaces or Cloud Run.

---

## 🛠 Tech Stack

| Component | Technologies |
| :--- | :--- |
| **Machine Learning** | XGBoost, Scikit-Learn, Joblib, Pandas, NumPy |
| **Backend Engine** | FastAPI, Uvicorn, Pydantic |
| **Frontend UI** | Streamlit, Requests |
| **Containerization** | Docker, Linux Shell (`start.sh`) |

---

## 📂 Project Structure

```text
paysim-fraud-detection/
├── api/
│   └── main.py                   # FastAPI inference routes & lifespan handler
├── frontend/
│   └── app.py                    # Streamlit dashboard & feature engineering
├── artifacts/
│   ├── fraud_detection_pipeline.joblib   # Trained pipeline artifact
│   └── model_metadata.joblib            # Optimal decision threshold metadata
├── Dockerfile                    # Container build configuration
├── start.sh                      # Dual-service startup script
├── requirements.txt              # Dependencies
└── README.md                     # Project documentation
