# NovaRisk Engine 🚀📈

A quantitative risk, pricing, and alerting application built with **Python**, **FastAPI**, **PostgreSQL**, **MongoDB**, and **Redis**. It handles trade booking, multi-asset valuations (Black-Scholes Greeks), stress-test simulations, and portfolio limit monitoring.
---

## 🏛️ System Architecture

```text
+-------------------------------------------------------+
|                    CLIENT / TESTS                     |
+-------------------------------------------------------+
                           |
                           v (HTTP Requests)
+-------------------------------------------------------+
|                  FASTAPI APPLICATION                  |
|             (API Routers & Endpoints)                 |
+-------------------------------------------------------+
             |                               |
             v                               v
+-----------------------+       +-----------------------+
|    PRICING ENGINE     |       |      RISK ENGINE      |
| (Black-Scholes/Greeks)|       | (FX Shocks & VaR 95%) |
+-----------------------+       +-----------------------+
             |                               |
             v                               v
+-----------------------+       +-----------------------+
|         REDIS         |       |      POSTGRESQL       |
|  (Market Data Cache)  |       |   (Trades & Limits)   |
+-----------------------+       +-----------------------+
                                             |
                                             v
                                +-----------------------+
                                |        MONGODB        |
                                |  (Simulation Vault)   |
                                +-----------------------+
```


## 📂 Project Structure

```text
.
├── app/
│   ├── api/
│   │   ├── market.py        # Market data & spot rates endpoints
│   │   ├── pricing.py       # Multi-asset pricing & Greeks routes
│   │   ├── reports.py       # Historical risk reports API
│   │   ├── risk.py          # Risk limits config & active breach alerts
│   │   └── trades.py        # Trade booking & CRUD operations
│   ├── core/
│   │   ├── config.py        # App settings & environment variables
│   │   └── databases.py     # PostgreSQL & MongoDB connection pooling
│   ├── models/
│   │   ├── risk.py          # SQLAlchemy PortfolioRiskLimit model
│   │   └── trade.py         # SQLAlchemy Trade persistence model
│   ├── schemas/
│   │   ├── report.py        # Pydantic report schemas
│   │   └── trade.py         # Pydantic validation for trade payloads
│   ├── services/
│   │   ├── market_data.py   # Market rate provider & Redis caching
│   │   ├── pricing.py       # Black-Scholes pricing model (PV, Delta, Gamma, Vega)
│   │   └── risk_engine.py   # Portfolio stress testing, VaR 95% & alert evaluations
│   ├── __init__.py
│   └── main.py              # FastAPI application entrypoint
├── tests/
│   ├── __init__.py
│   ├── test_engine.py       # Option pricing & core app tests
│   ├── test_pricing.py      # Multi-asset pricing suite (Options & FX Forwards)
│   ├── test_risk.py         # Risk limits, simulation & breach alert tests
│   └── test_trades.py       # Trade booking CRUD & duplicate prevention tests
├── docker-compose.yml       # Docker stack (PostgreSQL, MongoDB, Redis)
├── requirements.txt         # Python dependencies
└── README.md
```

## ⚙️ Tech Stack & Dependencies

- Framework: FastAPI (Python 3.12+)
- Relational Database: PostgreSQL (via SQLAlchemy & Psycopg2)
- Document Database: MongoDB (via Motor - AsyncIO Driver)
- Caching / In-Memory: Redis
- Quantitative Math: SciPy / NumPy (Black-Scholes & Normal Distribution CDF)
- Testing: Pytest & HTTPX (TestClient)

## 🚀 Getting Started & Initialization

#### 1. Prerequisites

- Docker and Docker Compose
- Python 3.12+ & venv

#### 2. Clone and Setup Virtual Environment

```bash
git clone [https://github.com/The-Reborn/novarisk-engine.git](https://github.com/your-username/novarisk-engine.git)
cd novarisk-engine

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. Start Infrastructure Stack (Docker)

Spin up PostgreSQL, MongoDB, and Redis using Docker Compose:

```bash
docker-compose up -d
```

#### 4. Initialize Database Tables

Run the database table creation script to initialize PostgreSQL schemas:

```bash
python -c "from app.core.databases import Base, engine; from app.models.trade import Trade; from app.models.risk import PortfolioRiskLimit; Base.metadata.create_all(bind=engine); print('Database tables created successfully.')"
```

#### 5. Run the Application

Start the FastAPI development server with auto-reload:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API Documentation (Swagger UI): http://localhost:8000/docs
- Interactive Redoc: http://localhost:8000/redoc

## 🔌 Core API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/trades/` | POST | Book a new multi-asset trade (FX Forward, Option). |
| `/api/v1/trades/{id}` | GET | Retrieve trade details by Trade ID. |
| `/api/v1/pricing/trade/{id}` | GET | Compute live Present Value (PV) and Greeks (Delta, Gamma, Vega). |
| `/api/v1/risk/limits/` | POST | Configure or update portfolio risk limits (Max Loss, Delta). |
| `/api/v1/risk/simulate/{portfolio_id}` | POST | Run FX stress tests, calculate VaR at 95% confidence, check limits, and log results to MongoDB. |
| `/api/v1/risk/alerts/active` | GET | Retrieve active portfolio limit-breach alerts from MongoDB. |

## 🧪 Running the Test Suite

The engine features a comprehensive automated test suite covering CRUD operations, multi-asset quantitative pricing, risk limits, and async simulation reporting.

Run tests using pytest:

```bash
pytest -v
```

## 📄 License

Distributed under the MIT License. See LICENSE for more information.
