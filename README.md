# NAAC Assist AI 🎓
> **AI-Powered Faculty Assistant for Accreditation Excellence**

**NAAC Assist AI** is an intelligent, RAG-based Generative AI application engineered to help universities and college faculty members prepare, manage, and streamline their **NAAC (National Assessment and Accreditation Council)** accreditation documentation.

By leveraging **IBM Granite Instruct** (via watsonx.ai), a local high-performance vector database (**ChromaDB**), and local semantic embeddings (**SentenceTransformers**), the platform retrieves information from manuals, policy papers, annual reports, and student logs to auto-compile highly structured, audit-ready Self Study Reports (SSRs) and Best Practice summaries.

---

## 🛠️ Technology Stack
* **Language**: Python 3.12+ (Optimized for Python 3.13)
* **Frontend**: Streamlit
* **Foundation LLM**: IBM Granite Instruct (via Watsonx.ai)
* **Vector Store**: ChromaDB (Private Local Vector database)
* **Embeddings**: SentenceTransformers (`all-MiniLM-L6-v2` running locally)
* **File Processing**: PyPDF, python-docx, Pandas
* **Report compiler**: ReportLab (Academic-grade PDF compiler)
* **Configuration**: Python Dotenv

---

## 📁 Project Architecture
```
naac-assist-ai/
├── app.py                     # Streamlit Frontend and routing
├── chatbot.py                 # Chat logic and ReportLab PDF compiler
├── rag.py                     # Text loaders, splitters, ChromaDB client & SentenceTransformers
├── granite_service.py         # watsonx.ai client connector & fallback generator
├── ssr_generator.py           # NAAC Taxonomy and SSR Draft generator module
├── best_practice_generator.py # Formulator for 6-step NAAC best practices
├── documents/                 # Folder monitored for indexing PDFs/DOCX/TXT
├── chroma_db/                 # Local directory for persistent Chroma DB vectors
├── requirements.txt           # Package dependencies
├── .env                       # Environment credentials
└── README.md                  # System instruction manual
```

---

## 🚀 Getting Started

### 1. Clone & Navigate
Make sure your terminal is opened inside the project root directory `naac-assist-ai/`.

### 2. Set Up Virtual Environment
Create and activate a Python virtual environment to avoid package pollution:

**On macOS / Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
Run the pip installer to download and bind the components:
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables (`.env`)
Create a file named `.env` in the root folder (or edit the existing one) and specify your watsonx.ai project parameters:

```env
IBM_API_KEY=your_ibm_cloud_api_key_here
PROJECT_ID=your_watsonx_project_id_here
IBM_URL=https://us-south.ml.cloud.ibm.com
IBM_MODEL_ID=ibm/granite-3-8b-instruct
```

> **Note**: If you do not have active IBM Cloud credentials, **do not worry!** The application is equipped with a premium fallback simulation engine that leverages your locally retrieved RAG chunks to formulate accurate reports so you can test the entire RAG cycle offline out-of-the-box.

### 5. Launch the Application
Run the Streamlit server:
```bash
streamlit run app.py
```
A local web browser tab will automatically open at `http://localhost:8501`.

---

## 💡 Key Features Run-Down

1. **🏠 Interactive Dashboard**: Monitor total indexed files, vector chunks, total queries run, and review the official 7 NAAC criteria guidelines.
2. **💬 AI RAG Chat Assistant**: Ask freeform questions (e.g. *“Explain metric 2.6.1”* or *“What placement rates did we secure in 2024?”*). Expand the expandable boxes to view matching source files, and download responses instantly as highly formatted academic PDFs.
3. **📄 SSR Draft Generator**: Select a Criterion, Key Indicator, and Metric from dynamic dropdowns, add custom instructions, and get a drafted response referencing your institutional data, complete with a PDF export button.
4. **🌟 Best Practices Generator**: Input an initiative, its objectives, activities, and outcomes. The engine searches supporting records and writes a formal 6-part NAAC compliant report.
5. **🔍 Criteria Explorer**: Browse checklists of documents needed (e.g. syllabus copies, reservations, seed money records) to get your folders ready for auditor reviews.
6. **📁 Document Ingest & Search**: Ingest text/PDF/Word files instantly. Monitor files currently indexed, delete records, or review direct vector search text matches.
