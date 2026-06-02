Slide 1 Problem Statement
The current accreditation process demands an overwhelming amount of manual coordination from faculty members to gather parse and organize thousands of pages of institutional data spanning multiple academic years.
Universities struggle to extract meaningful quantitative metrics and qualitative evidence from unstructured sources like policy manuals annual reports student logs and decentralized committee minutes.
Drafting official Self Study Reports and NAAC Best Practices by hand is highly tedious leading to inconsistencies formatting errors and missed compliance requirements.
Without an intelligent system to audit and structure this massive volume of documentation institutions frequently suffer from data gaps that directly result in lower accreditation grades and loss of prestige.
There is a critical need for an automated solution that can instantly retrieve relevant evidence and synthesize audit ready compliance reports with total accuracy and zero hallucinations.

Slide 2 Technology Used
The interactive frontend is powered by Streamlit which provides a secure and highly responsive dashboard tailored specifically for faculty members to upload and query university documents.
At the core of the system is the IBM Granite Instruct foundation model accessed securely via the Watsonx ai enterprise platform ensuring compliance and high quality academic text generation.
Local data retrieval relies on ChromaDB acting as a persistent private vector database that stores all document chunks strictly on the local machine without exposing sensitive records to the cloud.
SentenceTransformers leveraging the all MiniLM L6 v2 model are used to generate fast local semantic embeddings which eliminates embedding costs and prevents data leakage during the vectorization phase.
Robust file processing is handled through PyPDF python docx and Pandas allowing the system to seamlessly parse complex tables and dense text from various institutional formats.
Final output generation utilizes the ReportLab library to instantly compile the LLM responses into beautifully formatted academic grade PDF documents ready for immediate auditor review.

Slide 3 Proposed Solution
NAAC Assist AI is a purpose built Retrieval Augmented Generation platform that acts as a virtual accreditation assistant transforming raw university records into highly structured compliance drafts.
The system features a secure ingestion pipeline where faculty can drag and drop massive PDF and Word documents allowing the local AI engine to instantly read and index the entire institutional knowledge base.
A powerful AI chat interface allows users to ask complex freeform questions about specific NAAC criteria and instantly receive precise answers that are strictly anchored to the uploaded evidence.
The automated Self Study Report generator uses dynamic dropdowns for the official 7 NAAC criteria allowing faculty to instantly draft highly specific metric responses complete with quantitative data points.
A specialized Best Practices formulator accepts raw initiative details and automatically restructures them into the strict six part NAAC format by pulling corroborating evidence from the vector database.
By automating the heaviest lifting of document search and report synthesis this solution drastically reduces preparation time from months to minutes while guaranteeing strict adherence to NAAC taxonomy.

Slide 4 Langflow Component Used
The ingestion pipeline relies on Document Loaders such as PyPDFLoader and Docx2txtLoader to extract raw unstructured text from various complex university formats like policy manuals and audit reports.
A Recursive Character Text Splitter is utilized to strategically break these massive documents into smaller semantic chunks ensuring that critical context is preserved without exceeding the token limits of the LLM.
The system employs HuggingFace Embeddings powered by SentenceTransformers to mathematically represent these text chunks as high dimensional vectors allowing for rapid semantic similarity matching.
The Chroma Vector Store component is responsible for securely indexing and persistently storing these vectorized embeddings on local hardware ensuring instantaneous search retrieval during user queries.
Custom Prompt Templates are engineered with strict boundaries instructing the language model to adopt an academic tone and completely refuse generation if the retrieved context lacks sufficient evidence.
The final pipeline stage utilizes a Retrieval QA Chain that seamlessly links the vector store context and the user query directly to the Watsonx LLM component pointing to the IBM Granite generation model.

Slide 5 Langflow Workflow Diagram
The workflow begins when raw university documents are fed into the Document Loaders which extract the raw textual data and pass it into the processing pipeline.
This extracted text is immediately handed off to the Recursive Character Text Splitter which intelligently slices the massive documents into bite sized semantic chunks while preserving paragraph context.
These individual text chunks are then processed by the HuggingFace Embeddings model which converts the human readable text into dense numerical vectors for machine understanding.
The resulting vectors are securely stored and indexed inside the Chroma Vector Store creating a searchable knowledge base that resides entirely on the local machine for maximum privacy.
When a user submits a query it is instantly embedded into a vector and mathematically matched against the stored Chroma vectors to retrieve the top most relevant institutional data chunks.
This retrieved contextual evidence is merged with the user query inside a strict Prompt Template and sent to the Watsonx LLM which generates the final NAAC compliant academic response.

Slide 6 Architecture Diagram
The Presentation Layer is built on a Streamlit Web Interface that handles all user interactions document uploads dynamic criterion selections and immediate PDF downloads in a seamless dashboard.
The Application Layer consists of independent modular components including the Chatbot Module the SSR Generator Module and the Best Practice Generator Module orchestrating different user workflows.
The Data Ingestion Layer operates locally using robust document parsers for PDF and Word files ensuring that complex institutional data is accurately extracted before entering the AI pipeline.
The Knowledge Base layer is powered by ChromaDB acting as a highly optimized vector database that stores all processed document chunks securely on the local hardware to prevent data exposure.
The AI Engine layer utilizes SentenceTransformers for local embedding generation ensuring that the semantic translation of sensitive documents happens completely independent of external cloud networks.
The LLM Service layer connects securely to the Watsonx API passing only the most relevant retrieved chunks to the IBM Granite Instruct model for synthesis while the Output Layer compiles the results using ReportLab.

Slide 7 Role of Agentic AI in the Solution
Agentic AI elevates this platform from a simple search engine into a highly autonomous compliance auditor that actively assists faculty in structuring complex accreditation narratives.
Rather than requiring manual keyword searches the AI independently decides which specific institutional data chunks are most relevant to answering nuanced NAAC criterion metrics.
The agent seamlessly synthesizes raw unstructured data into highly structured academic formats ensuring that the tone vocabulary and layout perfectly match strict auditor expectations without human intervention.
Operating under strict generative boundaries the system acts as a virtual gatekeeper by refusing to generate responses or hallucinate facts if the retrieved documents do not contain sufficient supporting evidence.
By autonomously verifying the presence of quantitative data before drafting the AI guarantees total accuracy and reliability in the final Self Study Reports and Best Practice summaries.
This agentic behavior transforms weeks of tedious manual cross referencing into an instant automated workflow allowing faculty to focus on quality improvement rather than data entry.

Slide 8 Novelty and Uniqueness
The architecture guarantees one hundred percent Local Data Privacy by ensuring that all document parsing chunking and vector embedding occur strictly on local hardware keeping sensitive records completely off the cloud.
Unlike generic AI wrappers this system features strict NAAC Taxonomy Integration meaning it is hardcoded with the official 7 Criteria and their specific metrics to ensure highly relevant and targeted generation.
The inclusion of a Premium Fallback Simulation provides a unique offline mode capable of synthesizing high quality heuristic reports using only local RAG context even when active cloud LLM credentials are unavailable.
The platform achieves true End to End Automation by managing the entire lifecycle from raw document ingestion and semantic search to the instant generation and export of highly formatted academic PDF reports.
By eliminating the reliance on paid cloud embedding APIs the system drastically reduces operational costs for universities while simultaneously accelerating document processing speeds through local SentenceTransformers.

Slide 9 Future Scope
The system architecture can be expanded to include direct API integration with University Management Systems and ERPs to automatically pull live real time data for student enrollment fees and faculty profiles.
Future versions will implement Multi Agent Collaboration where distinct AI agents act as separate departmental auditors independently reviewing and verifying each others compliance reports for maximum accuracy.
The ingestion pipeline will be upgraded with Automated Evidence Cross Checking capabilities designed to instantly flag missing signatures stamps or dates in uploaded institutional proofs before the final audit.
Because the underlying architecture is highly modular the platform can be rapidly adapted to support other major accreditation standards such as NBA NIRF and ABET simply by updating the prompt taxonomy.
The integration of advanced optical character recognition and multi lingual document parsing will allow regional institutions to seamlessly process hand written ledgers and native language policy documents.
