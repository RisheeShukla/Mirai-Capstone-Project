# 💸 RoastMySpend: The Brutal AI Expense Auditor

[![Streamlit](https://img.shields.io/badge/Streamlit-1.35.0-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-1.5%20Flash-4E79A7?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive%20Charts-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com/)
[![gTTS](https://img.shields.io/badge/gTTS-Audio_Engine-blue?style=for-the-badge)](https://pypi.org/project/gTTS/)

> SYSTEM INITIALIZED...
> LOADING FINANCIAL TELEMETRY...
> WARNING: CRITICAL DISCRETIONARY LEAKS DETECTED.
> INITIATING AI ROAST PROTOCOL...

**RoastMySpend** is a FinTech dashboard designed to analyze personal spending data, compute budget divergence metrics, and brutally roast discretionary financial leaks. Built with Streamlit and powered by the Google Gemini API, this application doesn't just track your expenses—it holds you aggressively accountable using multimodal text and generated audio feedback.

---

## 🔗 Live Application
*   **Live Demo:** [Insert your Streamlit Cloud / Render / HF Spaces URL here]
*   **MIRAI Capstone Submission:** [Insert link to your mandatory LinkedIn post tagging MirAI School of Technology]

---

## ⚡ Core Features

*   **Interactive Data Pipeline:** Upload a CSV or load a chaotic mock dataset. Tweak transactions live using Streamlit's `st.data_editor` without memory loss via `st.session_state`.
*   **50/30/20 Telemetry Engine:** Dynamic KPI cards (`st.metric`) track cumulative burn velocity, baseline essential spending, and pinpoint discretionary leaks against standard financial rules.
*   **Advanced Prompt Engineering:** Uses Gemini 1.5 Flash with injected `f-strings` to deliver tailored roasts based on a selected persona (e.g., Wall Street Quant, Disappointed Parent) and user-provided excuses.
*   **Multimodal Audio Feedback (TTS):** Automatically synthesizes a 1-sentence, brutal summary of your financial audit into a playable in-browser audio widget.
*   **Actionable Reporting:** Generates and allows users to download a strict 30-Day Markdown Budget Recovery Plan.

---

## 🗺️ System Architecture

```mermaid
flowchart TD
    A[User Ingestion: CSV / Data Editor] --> B[Pandas Pipeline & Aggregation]
    B --> C[Metric Telemetry: Burn Rate & Leak Detection]
    C --> D[Visual Dashboard: Plotly Sunburst & Area Charts]
    B --> E[Dynamic Prompt Engineering Engine]
    E --> F[Persona Selection & Excuse Context]
    F --> G[Gemini 1.5 Pro/Flash API]
    G --> H[Structured Output: Brutal Roast + Recovery Sprint]
    G --> I[gTTS Engine: 1-Sentence Audio Summary]
    H --> J[Streamlit Session State & Downloadable Markdown]
    I --> J
