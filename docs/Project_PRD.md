# 📌 PRD: Agentic Financial Automation Platform (Updated with NLQ + Supabase/Vercel Integration)

## 1. Product Overview

**Vision:**  
AI-powered, agentic platform to parse, analyze, visualize, forecast, and explain financial data.  
Designed to automate and accelerate the core analysis and reporting tasks of analysts, CFOs, controllers, FP&A teams, and consultants.  

**Scope:**  
- **Core:** Upload → Parse → Analyze → Visualize → Report (modular backend + web UI)  
- **Immediate focus:**  
  - Accurate calculation + visualization of metrics, ratios, variance  
  - Interactive charts, tables, dashboards  
  - Export-ready for reporting  
- **Expansion:**  
  - Forecasting, JE automation, scenario analysis  
  - Natural language querying for simplified analysis  
  - Collaborative workflows, mobile app, enterprise features  

---

## 2. User Stories & Use Cases

**Primary Users:** Analysts, CPAs, CFOs, controllers, FP&A, accounting firms, audit teams, business owners.  

**Core Use Cases:**  
1. Upload common financial reports (CSV/Excel/PDF).  
2. Get instant KPIs + ratios (Revenue, Margin, EBITDA, COGS, FCF, ROE, Current Ratio, etc.).  
3. View interactive charts + dashboards.  
4. Perform variance analysis (Budget vs Actual, YoY, QoQ).  
5. Ask natural language questions (NLQ):  
   - “What’s the margin?”  
   - “Why is Q2 net income lower than Q1?”  
6. Export results (CSV, Excel, PDF).  
7. Later:  
   - Forecast metrics (next quarters/years).  
   - Auto-generate journal entries (COGS, revenue, inventory).  
   - Advanced NLQ with multi-metric explanations.  

---

## 3. Core Features & Requirements (By Agent)

### Phase 1 — Backbone (Fast MVP with Modular Hooks)
1. **Doc Processor Agent (MVP)**  
   - Ingest CSV/Excel, minimal PDF (pdfplumber).  
   - Output: Clean pandas DataFrame + JSON.  
   - Error handling + unit tests.  

2. **Metrics Calculator Agent**  
   - Compute core KPIs (margins, ratios, growth).  
   - Modular formulas in `finance_utils.py`.  
   - Output: JSON.  

3. **Chart/Visualization Agent**  
   - Generate bar/line/pie charts with matplotlib/plotly.  
   - Backend saves PNGs locally (frontend later).  

4. **Frontend Upload + Dashboard**  
   - React web app deployed on **Vercel** (Phase 1 deliverable).  
   - File upload → calls FastAPI backend (Docker on AWS Fargate).  
   - Displays metrics + charts.  
   - **Auth/storage local at first** → Supabase optional later.  

---

### Phase 1.5 — Lightweight NLQ
5. **NLQ (Lightweight) Agent**  
   - Input: Metrics JSON (from Metrics Agent).  
   - Process: Forward JSON + user query to GPT → return answer.  
   - Example:  
     User: “What’s revenue?”  
     Backend: `{ "revenue": 50000, "margin": 0.35 }`  
     Output: “Revenue is $50,000.”  
   - Limitations: Basic Q&A only. No variance explanations or multi-metric decomposition.  

---

### Phase 2 — Core (Moat Features + Accuracy)
6. **Journal Entry Automation Agent (Moat)**  
   - Purpose: Automates journal entries (revenue, COGS, inventory).  
   - Core: Configurable rules engine, narrow industry vertical first.  
   - Input: Clean DataFrame from Doc Processor.  
   - Output: Validated debit/credit entries.  

7. **Forecasting Agent (Moat)**  
   - ARIMA/Prophet forecasting for revenue, margins, cash flow.  
   - Backtesting to ensure accuracy.  
   - Outputs forecast tables + charts.  

8. **Variance Analysis Agent**  
   - Budget vs Actual, YoY, QoQ.  
   - Visual + narrative explanations.  

9. **Doc Processor v2**  
   - Multi-parser PDF support.  
   - OCR fallback for scanned docs.  

**Infra Note:**  
- **Supabase** integrated here for:  
  - Auth (multi-user testing).  
  - File storage (CSV/PDF in buckets).  
  - Postgres DB (persist metrics, JE, forecasts).  
- Backend stays on FastAPI/AWS Fargate.  

---

### Phase 3 — Smart Layer (Moat-Grade NLQ)
10. **Chunker Agent**  
    - Split large docs into retrievable, analysis-ready sections.  

11. **Retriever + NLQ Query Agents (Moat-Grade)**  
    - Map natural language → structured queries.  
    - Handle complex multi-part questions (“Compare Q2 vs Q3 margin and explain variance”).  
    - Use retriever, query decomposer, validator.  

12. **Validator Agent**  
    - Catch incorrect/outlier metrics before rendering.  

---

### Phase 4 — Fancy Stuff
13. **Math/Statistical Agent**  
    - NPV, IRR, CAGR, sensitivity, anomaly detection.  

14. **Mobile App + Enterprise Features**  
    - Multi-user, auth, integrations, white-label.  

---

## 4. Technical Stack

- **Backend:** Python (FastAPI, pandas, numpy, statsmodels)  
- **Forecasting:** Prophet, ARIMA  
- **Visualization:** matplotlib, plotly (backend); Recharts (frontend)  
- **Frontend:** React (**Vercel**)  
- **Infra:** Docker, AWS Fargate  
- **Optional Infra (Phase 2+):** Supabase (auth, Postgres, storage)  
- **Testing:** pytest (backend), Playwright/Cypress (frontend)  
- **CI/CD:** GitHub Actions  

---

## 5. Feature Roadmap

| Milestone   | Features/Modules                                | Stack/Tech              |
|-------------|-------------------------------------------------|--------------------------|
| **MVP**     | Doc Processor, Metrics, Charts, Frontend (Vercel)| Python, FastAPI, React   |
| **Phase 1.5**| Lightweight NLQ                                | GPT API, JSON pipeline   |
| **Phase 2** | JE Automation, Forecasting, Variance, DP v2, Supabase infra | ARIMA, Prophet, Rules, Supabase |
| **Phase 3** | Chunker, Moat-Grade NLQ, Validator              | LangChain/LLM APIs       |
| **Phase 4** | Math/Stat Agent, Mobile, Enterprise features    | React Native, SSO/Auth   |

---

## 6. Non-Functional Requirements

- **Security:** Encrypted uploads, secure endpoints, role-based access.  
- **Scalability:** Containerized, modular agents.  
- **Performance:** Metrics/Charts < 5s for normal files. Forecasting < 10s. NLQ response < 5s.  
- **Maintainability:** Unit + integration tests, CI/CD.  
- **Usability:** Simple 2-click access to KPIs, charts, and queries.  

---

## 7. Success Metrics

- MVP: Correct metrics + charts for uploaded files. Frontend live on Vercel.  
- Phase 1.5: NLQ answers basic queries accurately from metrics JSON.  
- Phase 2: Supabase integrated for persistence + auth. JE + Forecasting accurate + validated.  
- Phase 3: Complex NLQ queries mapped correctly + validated outputs.  
- Phase 4: Enterprise scalability.  

---

## 8. Sample Repo Scaffold

```
backend/
├── agents/
│   ├── doc_processor_agent.py   # Phase 1
│   ├── metrics_calculator.py    # Phase 1
│   ├── chart_agent.py           # Phase 1
│   ├── nlq_light_agent.py       # Phase 1.5
│   ├── je_automation_agent.py   # Phase 2
│   ├── forecasting_agent.py     # Phase 2
│   ├── variance_agent.py        # Phase 2
│   ├── retriever_agent.py       # Phase 3
│   ├── validator_agent.py       # Phase 3
│   └── math_stat_agent.py       # Phase 4
├── utils/
│   ├── finance_utils.py
│   ├── chart_utils.py
│   ├── io_adapter.py   # local/supabase/s3 I/O modularity
│   └── config.py
frontend/
├── src/
│   ├── components/
│   │   ├── FileUploader.tsx
│   │   ├── MetricWidget.tsx
│   │   ├── ChartDisplay.tsx
│   │   ├── Dashboard.tsx
│   │   ├── NLQBox.tsx   # for Phase 1.5 NLQ queries
│   │   └── ExportButton.tsx
│   ├── pages/
│   │   ├── Home.tsx
│   │   └── Dashboard.tsx
│   └── api/
│       └── backend.ts
docs/
└── PRD.md
```

---

## 9. Rules

- Independent + containerized agents.  
- No forward progress without unit + integration tests.  
- User feedback loop starts Phase 1.  
- Scale infra only as usage grows.  
