import streamlit as st
import os
import io
import time
from dotenv import load_dotenv

# Import our backend services
from granite_service import GraniteService
from rag import RAGEngine, DOCUMENTS_DIR
from ssr_generator import SSRGenerator, NAAC_TAXONOMY
from best_practice_generator import BestPracticeGenerator
from chatbot import NAACChatbot, export_response_to_pdf

# Load env variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="NAAC Assist AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium UI Styling Injections (University Blue & Slate Theme)
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
    /* Global Overrides */
    * {
        font-family: 'Inter', sans-serif;
    }
    .reportview-container {
        background: #fdfdfd;
    }
    
    /* Elegant Title Banner */
    .title-banner {
        background: linear-gradient(135deg, #002244 0%, #003366 100%);
        color: white;
        padding: 2.2rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        margin-bottom: 2rem;
        border-left: 6px solid #0066cc;
    }
    .title-banner h1 {
        color: white !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    .title-banner p {
        font-size: 1.1rem !important;
        opacity: 0.9;
        margin-top: 0.5rem !important;
        margin-bottom: 0 !important;
    }
    
    /* Academic Cards */
    .metric-card {
        background-color: white;
        border: 1px solid #eef2f6;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02);
        transition: transform 0.2s, box-shadow 0.2s;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.05);
        border-color: #0066cc;
    }
    .metric-val {
        font-size: 2.2rem;
        font-weight: 700;
        color: #003366;
        margin-bottom: 0.2rem;
    }
    .metric-lbl {
        font-size: 0.9rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* NAAC Criterion Explorer Cards */
    .criterion-box {
        background: white;
        border: 1px solid #eef2f6;
        border-radius: 8px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        border-left: 4px solid #003366;
        box-shadow: 0 2px 6px rgba(0,0,0,0.01);
    }
    .criterion-box h4 {
        color: #003366 !important;
        margin-top: 0 !important;
        font-weight: 600;
    }
    .criterion-tag {
        background-color: #e6f0fa;
        color: #003366;
        font-size: 0.75rem;
        padding: 2px 8px;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 8px;
    }
    
    /* Status Badge styling */
    .status-badge {
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        text-align: center;
    }
    .status-active {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .status-demo {
        background-color: #fff3cd;
        color: #856404;
        border: 1px solid #ffeeba;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session States
if "query_count" not in st.session_state:
    st.session_state.query_count = 0
if "recent_searches" not in st.session_state:
    st.session_state.recent_searches = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_generated_doc" not in st.session_state:
    st.session_state.last_generated_doc = None
if "last_doc_title" not in st.session_state:
    st.session_state.last_doc_title = ""

# Single instances of backend engines stored in caching to maintain efficiency
@st.cache_resource
def get_backend_services():
    granite_service = GraniteService()
    rag_engine = RAGEngine()
    
    # Auto rebuild collection from existing documents in folder
    rag_engine.rebuild_db_from_documents_folder()
    
    ssr_generator = SSRGenerator(granite_service, rag_engine)
    bp_generator = BestPracticeGenerator(granite_service, rag_engine)
    chatbot = NAACChatbot(granite_service, rag_engine)
    
    return granite_service, rag_engine, ssr_generator, bp_generator, chatbot

granite_service, rag_engine, ssr_generator, bp_generator, chatbot = get_backend_services()

# --- SIDEBAR CONTROL PANEL ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/graduation-cap.png", width=70)
    st.markdown("<h2 style='color:#003366; margin-top:0;'>NAAC Assist AI</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.85rem; color:#666; margin-top:-10px;'>Accreditation Intelligence Suite</p>", unsafe_allow_html=True)
    st.write("---")
    
    # Navigation
    menu = st.radio(
        "NAVIGATION",
        [
            "🏠 Dashboard", 
            "💬 AI Chat Assistant", 
            "📄 SSR Draft Generator", 
            "🌟 Best Practices Generator", 
            "🔍 Criteria Explorer", 
            "📁 Document Ingest & Search",
            "ℹ️ About"
        ]
    )
    
    st.write("---")
    
    # System Status Panel
    st.markdown("### SYSTEM STATUS")
    
    # watsonx.ai Status Badge
    if granite_service.is_configured:
        st.markdown(
            f'<div class="status-badge status-active">● Active: IBM Granite<br><span style="font-size:0.7rem; font-weight:normal;">Model: {granite_service.model_id.split("/")[-1]}</span></div>', 
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="status-badge status-demo">● Fallback/Demo Mode<br><span style="font-size:0.75rem; font-weight:normal;">No Watsonx Credentials</span></div>', 
            unsafe_allow_html=True
        )
        
    st.write("")
    
    # Vector DB Status
    doc_count = len(rag_engine.get_indexed_documents())
    chunk_count = rag_engine.get_total_chunks()
    st.metric(label="Files in ChromaDB", value=f"{doc_count} files", delta=f"{chunk_count} chunks")
    
    st.markdown(
        "<div style='font-size:0.75rem; text-align:center; color:#999; margin-top:15px;'>"
        "NAAC Assist AI v1.0.0<br>Designed for Faculty Excellence"
        "</div>", 
        unsafe_allow_html=True
    )

# --- HEADER TITLE BANNER ---
st.markdown(
    f"""
    <div class="title-banner">
        <h1>NAAC Assist AI</h1>
        <p>AI-Powered Faculty Assistant for Accreditation Excellence</p>
    </div>
    """, 
    unsafe_allow_html=True
)

# ==========================================
# 1. PAGE: DASHBOARD
# ==========================================
if menu == "🏠 Dashboard":
    st.subheader("University Accreditation Overview")
    
    # 4-Column Metric Grid
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f'<div class="metric-card"><div class="metric-val">{doc_count}</div><div class="metric-lbl">Documents Indexed</div></div>', 
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f'<div class="metric-card"><div class="metric-val">{chunk_count}</div><div class="metric-lbl">Text Chunks</div></div>', 
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            f'<div class="metric-card"><div class="metric-val">{st.session_state.query_count}</div><div class="metric-lbl">Queries Processed</div></div>', 
            unsafe_allow_html=True
        )
    with col4:
        st.markdown(
            '<div class="metric-card"><div class="metric-val">7 / 7</div><div class="metric-lbl">Criteria Supported</div></div>', 
            unsafe_allow_html=True
        )
        
    st.write("---")
    
    # Two Column Layout: Criteria Status & Recent Searches
    dcol1, dcol2 = st.columns([2, 1])
    
    with dcol1:
        st.markdown("### NAAC Criteria Quick Reference")
        
        # Simple list of all criteria
        c_list = [
            ("Criterion 1: Curricular Aspects", "Focuses on curriculum design, revision systems, choice-based credits, and structured feedback mechanisms."),
            ("Criterion 2: Teaching-Learning & Evaluation", "Covers enrollment percentage, teacher profile quality, student ratios, exam assessment transparency, and learning outcomes (PO/CO)."),
            ("Criterion 3: Research, Innovations & Extension", "Reviews seed funds, project grants, innovation hubs, patent filings, UGC-indexed research publications, outreach activities, and MoUs."),
            ("Criterion 4: Infrastructure & Learning Resources", "Monitors smart classrooms, sports/cultural auditoriums, library automation (ILMS), computer ratio, and maintenance budgets."),
            ("Criterion 5: Student Support & Progression", "Tracks government/non-government scholarships, capability enhancement, placements, progression to higher education, and active alumni contributions."),
            ("Criterion 6: Governance, Leadership & Management", "Evaluates institutional vision, deployment strategies, welfare measures, audits, and Internal Quality Assurance Cell (IQAC) effectiveness."),
            ("Criterion 7: Institutional Values & Best Practices", "Highlights gender equity, clean solar/alternate energy, green audits, waste recycling, distinctive features, and standard Best Practices.")
        ]
        
        for name, desc in c_list:
            st.markdown(
                f"""
                <div class="criterion-box">
                    <span class="criterion-tag">Official NAAC Category</span>
                    <h4>{name}</h4>
                    <p style="font-size:0.9rem; color:#444; margin:0;">{desc}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
    with dcol2:
        st.markdown("### Accreditation Activities")
        
        # Interactive checklist to help faculty track goals
        st.info("💡 **Pro Tip**: Ingest your previous SSR records, annual reports, and committee minutes in the 'Document Ingest' page so the AI RAG engine can reference actual data points.")
        
        st.write("")
        st.markdown("##### Task Checklist")
        st.checkbox("Upload Institutional Policy Manuals", value=(doc_count > 0))
        st.checkbox("Index 2024 placement and publication records", value=(doc_count > 1))
        st.checkbox("Verify Criterion 2.6.1 public outcomes", value=False)
        st.checkbox("Draft Criterion 3 extension outreach report", value=False)
        st.checkbox("Export standard Green Campus Best Practice", value=False)
        
        st.write("")
        st.markdown("##### Recent Search Queries")
        if st.session_state.recent_searches:
            for q in st.session_state.recent_searches[-5:]:
                st.markdown(f"📝 *\"{q}\"*")
        else:
            st.caption("No queries run in this session yet.")

# ==========================================
# 2. PAGE: AI CHAT ASSISTANT
# ==========================================
elif menu == "💬 AI Chat Assistant":
    st.subheader("Accreditation RAG Chat Assistant")
    st.markdown(
        "Ask details regarding NAAC requirements, required evidence documents, or query actual data from "
        "your uploaded files. **Answers are strictly anchored to your indexed documents.**"
    )
    
    # Handle chat clear
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()
        
    st.write("---")
    
    # Display Chat History
    for role, message, sources in st.session_state.chat_history:
        if role == "user":
            st.chat_message("user").markdown(f"**Faculty:** {message}")
        else:
            with st.chat_message("assistant"):
                st.markdown(message)
                if sources:
                    with st.expander("📚 Retrieved Source Documents", expanded=False):
                        for src in sources:
                            st.write(f"📄 {src}")
                            
    # Chat Input Box
    user_query = st.chat_input("Ask a NAAC-specific question (e.g. 'What documents are required for Criterion 5?')")
    
    if user_query:
        # Display user input immediately
        st.chat_message("user").markdown(f"**Faculty:** {user_query}")
        
        # Run chatbot query
        with st.spinner("Analyzing NAAC documents and synthesizing answers..."):
            st.session_state.query_count += 1
            st.session_state.recent_searches.append(user_query)
            
            result = chatbot.ask(user_query)
            answer = result["answer"]
            sources = result["sources"]
            
        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(answer)
            if sources:
                with st.expander("📚 Retrieved Source Documents", expanded=False):
                    for src in sources:
                        st.write(f"📄 {src}")
                        
        # Append to state history
        st.session_state.chat_history.append(("user", user_query, []))
        st.session_state.chat_history.append(("assistant", answer, sources))
        
        # Save last response globally for PDF compilation
        st.session_state.last_generated_doc = answer
        st.session_state.last_doc_title = f"RAG Query Response - {user_query[:30]}"
        st.rerun()

    # Sticky Footer for downloading the last answer
    if st.session_state.last_generated_doc:
        st.write("---")
        st.markdown("##### 📥 Export Last Assistant Response")
        pdf_bytes = export_response_to_pdf(
            st.session_state.last_doc_title, 
            st.session_state.last_generated_doc
        )
        st.download_button(
            label="📥 Download Answer as Academic PDF",
            data=pdf_bytes,
            file_name="naac_assist_response.pdf",
            mime="application/pdf"
        )

# ==========================================
# 3. PAGE: SSR DRAFT GENERATOR
# ==========================================
elif menu == "📄 SSR Draft Generator":
    st.subheader("Self Study Report (SSR) Draft Generator")
    st.markdown(
        "Select a specific Criterion, Key Indicator, and Metric. The assistant will retrieve all matching "
        "institutional data chunks and compose a detailed, audit-compliant academic draft response."
    )
    st.write("---")
    
    # 3-Column Dropdown triggers (Taxonomy-driven dynamic dropdowns)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        crit_keys = list(NAAC_TAXONOMY.keys())
        selected_crit = st.selectbox("Select NAAC Criterion", crit_keys)
        
    with col2:
        ki_keys = list(NAAC_TAXONOMY[selected_crit].keys())
        selected_ki = st.selectbox("Select Key Indicator (KI)", ki_keys)
        
    with col3:
        metrics_list = NAAC_TAXONOMY[selected_crit][selected_ki]
        selected_metric = st.selectbox("Select Specific Metric ID", metrics_list)
        
    # Additional Context from user
    additional_notes = st.text_area(
        "Additional Directives (Optional)", 
        placeholder="e.g., Focus on our 2024 energy audit numbers, mention the 100kW solar installation, and quote the strategic green planning committee."
    )
    
    if st.button("🚀 Compose Professional SSR Draft"):
        with st.spinner("Mining institutional records and compiling SSR draft..."):
            st.session_state.query_count += 1
            
            result = ssr_generator.generate_draft(
                criterion=selected_crit,
                key_indicator=selected_ki,
                metric=selected_metric,
                additional_instructions=additional_notes
            )
            
            st.session_state.last_generated_doc = result["draft"]
            st.session_state.last_doc_title = f"SSR Draft - Metric {selected_metric.split(':')[0]}"
            
    if st.session_state.last_generated_doc and st.session_state.last_doc_title.startswith("SSR Draft"):
        st.write("---")
        st.markdown(f"### {st.session_state.last_doc_title}")
        st.markdown(st.session_state.last_generated_doc)
        
        # Download PDF button
        pdf_bytes = export_response_to_pdf(
            st.session_state.last_doc_title, 
            st.session_state.last_generated_doc
        )
        st.download_button(
            label="📥 Download SSR Draft as PDF",
            data=pdf_bytes,
            file_name=f"{st.session_state.last_doc_title.replace(' ', '_').lower()}.pdf",
            mime="application/pdf"
        )

# ==========================================
# 4. PAGE: BEST PRACTICES GENERATOR
# ==========================================
elif menu == "🌟 Best Practices Generator":
    st.subheader("NAAC Best Practices Formulator")
    st.markdown(
        "Compile your university's special quality initiatives into the strict, standard 6-part NAAC Best Practice layout. "
        "The system will search and pull corroborating evidence (green audits, MoUs, financial ledgers) from the vector database."
    )
    st.write("---")
    
    # Input Form
    bp_title = st.text_input("1. Name / Title of the Practice", placeholder="e.g., Eco-Campus: Decentralized Solid and Liquid Waste Management Program")
    bp_objectives = st.text_area("2. Key Objectives & Goals", placeholder="e.g., Achieve 100% sorting at source, recycle solid plastic waste, treat sewage water for gardening...")
    bp_activities = st.text_area("3. Activities Conducted & Deployment Details", placeholder="e.g., Installed sorting bins across campus, built a sewage treatment plant with 50KLD capacity, partnered with local organic farms...")
    bp_outcomes = st.text_area("4. Quantifiable Outcomes", placeholder="e.g., Successfully treated 45,000 liters daily, reduced paper waste dump by 35% within 12 months...")
    
    if st.button("⚙️ Synthesize NAAC-Compliant Report"):
        if not bp_title:
            st.warning("⚠️ Please provide an Initiative Title to get started.")
        else:
            with st.spinner("Structuring best practice and fetching vector records..."):
                st.session_state.query_count += 1
                
                result = bp_generator.generate_practice(
                    initiative=bp_title,
                    objective=bp_objectives,
                    activities=bp_activities,
                    outcomes=bp_outcomes
                )
                
                st.session_state.last_generated_doc = result["report"]
                st.session_state.last_doc_title = f"NAAC Best Practice - {bp_title[:40]}"
                
    if st.session_state.last_generated_doc and st.session_state.last_doc_title.startswith("NAAC Best Practice"):
        st.write("---")
        st.markdown(f"### {st.session_state.last_doc_title}")
        st.markdown(st.session_state.last_generated_doc)
        
        # Download PDF Button
        pdf_bytes = export_response_to_pdf(
            st.session_state.last_doc_title, 
            st.session_state.last_generated_doc
        )
        st.download_button(
            label="📥 Download Best Practice Document as PDF",
            data=pdf_bytes,
            file_name="naac_best_practice.pdf",
            mime="application/pdf"
        )

# ==========================================
# 5. PAGE: CRITERIA EXPLORER
# ==========================================
elif menu == "🔍 Criteria Explorer":
    st.subheader("NAAC Criteria & Evidence Explorer")
    st.markdown(
        "Explore the requirements for each of the 7 NAAC criteria and check the checklist of standard supporting documents and evidence required."
    )
    st.write("---")
    
    # Selector for Criteria
    selected_c = st.selectbox(
        "Select a Criterion to Study:",
        [
            "Criterion 1: Curricular Aspects",
            "Criterion 2: Teaching-Learning and Evaluation",
            "Criterion 3: Research, Innovations and Extension",
            "Criterion 4: Infrastructure and Learning Resources",
            "Criterion 5: Student Support and Progression",
            "Criterion 6: Governance, Leadership and Management",
            "Criterion 7: Institutional Values and Best Practices"
        ]
    )
    
    # Evidence data sheets
    evidence_checklist = {
        "Criterion 1: Curricular Aspects": [
            "University syllabus copies highlighting revisions",
            "Syllabus revision committee minutes/resolutions",
            "Structured Feedback questionnaires (Students, Teachers, Alumni, Employers)",
            "Action Taken Reports (ATRs) on feedback with public display proofs",
            "List of new academic courses introduced in last 5 years"
        ],
        "Criterion 2: Teaching-Learning and Evaluation": [
            "Official student enrollment ledgers and seat allotment certificates",
            "Compliance proofs for SC/ST/OBC seat quotas",
            "Student-to-Teacher ratio documentation",
            "Lists of full-time teachers along with Ph.D./NET/SET qualifications",
            "Program Outcomes (POs) and Course Outcomes (COs) displays (e.g. syllabus headers, websites)",
            "University exam results and pass percentages"
        ],
        "Criterion 3: Research, Innovations and Extension": [
            "Official letters for seed money grants to faculty",
            "Research project sanction letters from Government agencies",
            "Incubation center pamphlets, event photos with dates",
            "Patents published or awarded documentation",
            "UGC-CARE list of faculty research publication links",
            "Reports and photo-evidence of community extension campaigns (e.g. Swachh Bharat)",
            "Collaborative MoUs and student internship records"
        ],
        "Criterion 4: Infrastructure and Learning Resources": [
            "LCR (Lecture Hall / Class Rooms) inventory logs with ICT facilities",
            "Cultural center, sports ground, and auditorium maps/photos",
            "ILMS (Integrated Library Management System) subscription bills",
            "E-resources access links (Shodhganga, e-journals)",
            "Student-to-Computer inventory tallies",
            "Audited balance sheets showing maintenance expenditure"
        ],
        "Criterion 5: Student Support and Progression": [
            "Government scholarship disbursement student lists",
            "Institutional freeship records and audited statements",
            "Reports for soft-skill, ICT guidance, and life-skill seminars",
            "Placement letters, salary slips, and corporate listings",
            "Higher education admission letters for progressing students",
            "Alumni Association registration certificates & annual donation ledgers"
        ],
        "Criterion 6: Governance, Leadership and Management": [
            "University strategic planning policy and deployment results",
            "Organogram of the university governance system",
            "Staff welfare scheme lists (insurance, medical, housing)",
            "Professional development program completion proofs for faculty",
            "Internal and external financial audit certificates",
            "Annual IQAC report drafts and action outcomes"
        ],
        "Criterion 7: Institutional Values and Best Practices": [
            "Gender sensitization action plans and annual program listings",
            "Solar panel and LED lighting purchase invoices & site photos",
            "Decentralized waste sorting policy brochures",
            "Green Audit, Energy Audit, and Environment Audit certificates",
            "Institutional distinctiveness summary statement and pictures"
        ]
    }
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"#### 📋 Required Evidence Checklist: *{selected_c.split(':')[0]}*")
        for item in evidence_checklist[selected_c]:
            st.markdown(f"✅ **{item}**")
            
    with col2:
        st.markdown("#### 💬 Criterion Quick-Query")
        st.info("Submit a fast query related specifically to this Criterion to explore matches in your indexed files.")
        quick_q = st.text_input("Enter your Criterion-specific question:", placeholder="e.g. What extension activities did we record?")
        
        if st.button("🔍 Run Quick-Query"):
            if quick_q:
                with st.spinner("Searching..."):
                    res = chatbot.ask(f"{selected_c}: {quick_q}")
                st.markdown("##### Response Summary:")
                st.write(res["answer"])
                if res["sources"]:
                    st.success(f"Sources identified: {', '.join(res['sources'])}")

# ==========================================
# 6. PAGE: DOCUMENT SEARCH & INGESTION
# ==========================================
elif menu == "📁 Document Ingest & Search":
    st.subheader("Document Ingestion & Semantic Search")
    st.markdown(
        "Upload files directly to index them in ChromaDB, or browse the active text index. "
        "Supported formats include **PDF, DOCX, and TXT**."
    )
    st.write("---")
    
    # Section: Upload & Indexing
    st.markdown("### Ingest New Accreditation Documents")
    uploaded_files = st.file_uploader(
        "Drag and drop files here (PDF, DOCX, TXT)", 
        type=["pdf", "docx", "txt"], 
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if st.button("📥 Parse and Index Uploaded Files"):
            for ufile in uploaded_files:
                file_path = os.path.join(DOCUMENTS_DIR, ufile.name)
                # Write to disk
                with open(file_path, "wb") as f:
                    f.write(ufile.getvalue())
                
                # Load to DB
                with st.spinner(f"Ingesting & chunking {ufile.name}..."):
                    success = rag_engine.load_and_index_file(file_path)
                    if success:
                        st.success(f"Indexed successfully: {ufile.name}")
                    else:
                        st.error(f"Error index file: {ufile.name}")
            time.sleep(1)
            st.rerun()
            
    st.write("---")
    
    # Section: Manage Files
    st.markdown("### Manage Indexed Documents")
    files = rag_engine.get_indexed_documents()
    
    if files:
        for idx, filename in enumerate(files):
            col_fn, col_del = st.columns([5, 1])
            with col_fn:
                st.markdown(f"📄 **{filename}**")
            with col_del:
                if st.button("🗑️ Delete", key=f"del_{idx}"):
                    rag_engine.delete_document(filename)
                    st.warning(f"Deleted: {filename}")
                    time.sleep(1)
                    st.rerun()
    else:
        st.caption("No files currently indexed in ChromaDB.")
        
    st.write("---")
    
    # Section: Semantic search details
    st.markdown("### Browse Matching Text Chunks")
    st.info("Input a search query to pull matching chunks from ChromaDB and audit the RAG output.")
    
    search_q = st.text_input("Enter search phrase:", placeholder="e.g. placements in 2024")
    if search_q:
        with st.spinner("Retrieving similar vectors..."):
            res = rag_engine.query(search_q, n_results=3)
        st.markdown("##### Relevant Chunks:")
        st.markdown(res["context"])

# ==========================================
# 7. PAGE: ABOUT
# ==========================================
elif menu == "ℹ️ About":
    st.subheader("About NAAC Assist AI")
    st.markdown(
        """
        **NAAC Assist AI** is a state-of-the-art Generative AI decision suite engineered specifically 
        for academic institutions facing rigorous accreditation audits by the National Assessment 
        and Accreditation Council (NAAC).
        
        Preparing accreditation records represents a massive coordination challenge for faculty members, 
        requiring the extraction, organization, and compliance formatting of thousands of pages of institutional data. 
        
        ### Core Technology Highlights:
        1. **IBM Granite Foundation Model**: Interfaced using the official `ibm-watsonx-ai` Python SDK to ensure secure, compliant, enterprise-grade text generation.
        2. **Local Vector Database (ChromaDB)**: Offers secure, private, instant similarity matching that operates directly on the user's workspace without external storage.
        3. **Local SentenceTransformers (`all-MiniLM-L6-v2`)**: Generates rapid sentence embeddings locally, eliminating embedding costs and latency.
        4. **Structured RAG Pipelines**: Integrates strict prompt templates enforcing RAG boundary validation to prevent generative hallucinations, ensuring responses remain 100% anchored to official records.
        5. **ReportLab Compiler**: Exports highly styled, university-grade academic PDF drafts immediately.
        
        ---
        Developed by Antigravity for Advanced Agentic Coding.
        """
    )
