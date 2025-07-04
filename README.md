# Financial Automation Platform

Modern, modular, agent-powered analytics and reporting for finance professionals.

> **Automate financial metrics, charts, variance analysis, forecasting, and executive-ready insights with a single platform.**

---

## 🚀 Features

- Upload P&L, Balance Sheet, Cash Flow, Budget/Actuals (PDF, Excel, CSV)
- Instant calculation and display of all essential financial metrics & ratios
- Automated variance analysis (budget vs. actual, YoY, QoQ, MoM, etc.)
- Interactive, exportable charts and tables (trend, bar, line, pie, waterfall)
- Natural language queries for rapid answers
- Time series forecasting and advanced scenario analysis
- Board/executive-ready exports (CSV, Excel, PDF)
- Modular, agentic backend for easy scaling and feature expansion
- Ready for cloud, team collaboration, and mobile app (future)

---

## 🛠️ Quick Start

### 1. Clone the Repository

```bash
git clone <YOUR_REPO_URL>
cd financial-automation/backend
```

### 2. Create and Activate a Virtual Environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure Environment Variables

- Copy `.env.example` to `.env`
- Fill in required keys (API keys, AWS, etc.)

---

### 5. Run the Backend (FastAPI)

```bash
uvicorn app.main:app --reload
```
Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) to see the API docs (Swagger/OpenAPI).

---

## 🐍 Google Colab / Jupyter Quickstart

- Skip venv setup.
- Use `!pip install -r requirements.txt` at the top of your notebook.
- File upload and path management may differ in notebook environments.

---

## 🐳 Docker (Optional)

```bash
docker build -t financial-backend .
docker run -p 8000:8000 --env-file .env financial-backend
```

---

## 📁 Project Structure

```
backend/
│
├── agents/
│   ├── doc_processor_agent.py
│   ├── chunker_agent.py
│   ├── metrics_calculator_agent.py
│   ├── variance_analysis_agent.py
│   ├── chart_agent.py
│   ├── forecasting_agent.py
│   ├── math_tools_agent.py
│   ├── stat_analysis_agent.py
│   ├── retriever_agent.py
│   ├── query_decomposer_agent.py
│   ├── context_stitcher_agent.py
│   ├── llm_answer_agent.py
│   └── validator_agent.py
├── utils/
│   ├── finance_utils.py
│   ├── chart_utils.py
│   ├── file_utils.py
│   ├── html_utils.py
│   └── config.py
├── orchestrator/
│   └── orchestrator.py
├── data/
│   └── sample_reports/
├── app/
│   └── main.py
├── tests/
├── requirements.txt
├── .env
└── README.md
```

---

## 🌍 Cross-Platform & Cloud

- Works on Windows, macOS, Linux.
- All code uses Python’s `os.path` or `pathlib` for maximum portability.
- For cloud/Colab, see [Quick Start](#quick-start).

---

## 🧑‍💻 Contributing

- Fork the repo and use feature branches.
- All code should include docstrings and type hints.
- PRs must include or update relevant unit tests.

---

## 📈 Core Technologies

- **Backend:** Python 3.10+, FastAPI, modular agent pattern
- **LLM/AI:** OpenAI GPT-4o, LangChain
- **Financial Math:** pandas, numpy, statsmodels, Prophet, numpy-financial
- **Visualization:** matplotlib, plotly, seaborn
- **Frontend (planned):** React, shadcn/ui, Recharts/Chart.js

---

## 📖 Documentation

- [Backend setup guide](backend/README.md)
- [Product PRD](PROJECT_PRD.md)

---

## ❓ Troubleshooting

- If virtual environment issues: delete `.venv` and recreate.
- For Windows path issues: use Python `os.path` functions, not hard-coded slashes.
- For dependency errors: upgrade `pip`, then re-install.

---

## ✉️ Contact / Support

For issues, feature requests, or to contribute:  
- [GitHub Issues](https://github.com/YOUR_ORG/YOUR_REPO/issues)
- [Contact us](mailto:your@email.com)

---

> Built for CPAs, financial analysts, and CFOs.  
> “Automate your insight—focus on strategy, not spreadsheets.”
