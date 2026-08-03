# RetentionPulse Risk Intelligence — Frontend + Backend Design

## Overview

Build a customer churn risk intelligence dashboard with React + FastAPI.
Three screens: Dashboard Overview, Customer Priority List, Customer Detail Analysis.

## Screens

### 1. Dashboard Overview (`/dashboard`)
- 4 KPI cards: Total Customers, Churn Rate, At-Risk Count, Avg Risk Score
- Churn trend line chart (30-day)
- Risk distribution pie chart (Low/Medium/High)
- Top-10 priority customers preview table

### 2. Customer List (`/customers`)
- Full table: ID, Tenure, Contract, Monthly Spend, Risk Score, Status, Action
- Filter bar: risk status, contract type, tenure range
- Sort, pagination, CSV export
- Each row links to detail page

### 3. Customer Detail (`/customers/:id`)
- Profile card: demographics, financials, payment method
- Active service subscriptions map (8 services)
- Risk score gauge + status badge
- Behavioral KPIs: satisfaction, complaints, late payments, service calls, data usage, days since interaction
- SHAP explanation drivers (top 4 features with impact %)
- Metadata: inference latency, model version, feature store freshness

## Backend API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/dashboard/summary` | Aggregate KPIs |
| GET | `/api/dashboard/trend` | Churn rate over time |
| GET | `/api/dashboard/risk-distribution` | Low/Medium/High counts |
| GET | `/api/customers` | Paginated list with filters |
| GET | `/api/customers/{id}` | Single customer detail |
| GET | `/api/customers/{id}/risk` | Risk score + SHAP values |
| GET | `/api/customers/{id}/services` | Active service subscriptions |
| GET | `/api/customers/{id}/kpis` | Behavioral indicators |
| POST | `/api/customers/export` | CSV export |

## Tech Stack

- Frontend: React 18 + TypeScript + Vite + Tailwind CSS + Recharts + React Router
- Backend: FastAPI + SQLAlchemy + Pydantic
- Font: Inter (Google Fonts)
- Icons: Lucide React

## Design System

- Colors: Primary #3B82F6, Background #F8FAFC, Surface white, Text #0F172A
- Risk: High #EF4444, Medium #F59E0B, Low #10B981
- Border radius: cards 16px, buttons 8px
- Cards: white bg + 1px slate-200 border + 24px padding
- Typography: Inter, display metrics 36px bold, headline 24px semibold, body 14px