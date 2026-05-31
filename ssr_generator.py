import os
from granite_service import GraniteService
from rag import RAGEngine

# Official NAAC Criteria Taxonomy for Dynamic UI Selection
NAAC_TAXONOMY = {
    "Criterion 1: Curricular Aspects": {
        "1.1 Curricular Planning and Implementation": [
            "1.1.1: Effective curriculum delivery through a well-planned and documented process.",
            "1.1.2: Number of programmes where syllabus revision was carried out."
        ],
        "1.2 Academic Flexibility": [
            "1.2.1: Percentage of new courses introduced across all programmes.",
            "1.2.2: Choice Based Credit System (CBCS) / Elective Course System implementation."
        ],
        "1.3 Curriculum Enrichment": [
            "1.3.1: Integration of cross-cutting issues (Professional Ethics, Gender, Human Values, Environment & Sustainability).",
            "1.3.2: Value-added courses imparting transferable and life skills."
        ],
        "1.4 Feedback System": [
            "1.4.1: Structured feedback obtained from students, teachers, employers, and alumni.",
            "1.4.2: Feedback process of the Institution (Feedback collected, analyzed, and action taken)."
        ]
    },
    "Criterion 2: Teaching-Learning and Evaluation": {
        "2.1 Student Enrollment and Profile": [
            "2.1.1: Average enrollment percentage (average of last five years).",
            "2.1.2: Percentage of seats filled against reserved categories (SC, ST, OBC, etc.)."
        ],
        "2.2 Student Diversity": [
            "2.2.1: Catering to student diversity, assessing learning levels (slow and advanced learners).",
            "2.2.2: Student-to-Teacher Ratio (full-time teachers only)."
        ],
        "2.3 Teaching-Learning Process": [
            "2.3.1: Student-centric methods (experiential, participatory, and problem-solving methodologies).",
            "2.3.2: Teachers use of ICT-enabled tools including online resources for effective teaching."
        ],
        "2.4 Teacher Profile and Quality": [
            "2.4.1: Percentage of full-time teachers against sanctioned posts.",
            "2.4.2: Percentage of full-time teachers with Ph.D. / NET / SET / SLET."
        ],
        "2.5 Evaluation Process and Reforms": [
            "2.5.1: Mechanism of internal assessment is transparent and robust.",
            "2.5.2: Mechanism to deal with internal examination-related grievances."
        ],
        "2.6 Student Performance and Learning Outcomes": [
            "2.6.1: Teachers and students are aware of the stated Programme and Course Outcomes.",
            "2.6.2: Attainment of Programme Outcomes and Course Outcomes are evaluated by the institution.",
            "2.6.3: Pass percentage of students (average of last five years)."
        ],
        "2.7 Student Satisfaction Survey": [
            "2.7.1: Online Student Satisfaction Survey (SSS) regarding teaching learning process."
        ]
    },
    "Criterion 3: Research, Innovations and Extension": {
        "3.1 Promotion of Research and Facilities": [
            "3.1.1: Seed money provided by the institution to its teachers for research.",
            "3.1.2: Percentage of teachers provided financial support to attend conferences / workshops."
        ],
        "3.2 Resource Mobilization for Research": [
            "3.2.1: Grants received from government and non-governmental agencies for research projects.",
            "3.2.2: Percentage of teachers having research projects."
        ],
        "3.3 Innovation Ecosystem": [
            "3.3.1: Ecosystem for innovations, including Incubation center and other initiatives.",
            "3.3.2: Workshops/seminars conducted on Intellectual Property Rights (IPR) and entrepreneurship."
        ],
        "3.4 Research Publications and Awards": [
            "3.4.1: Institution ensures implementation of its stated Code of Ethics for research.",
            "3.4.2: Number of Ph.Ds registered per eligible teacher.",
            "3.4.3: Number of research papers published per teacher in UGC care listed journals."
        ],
        "3.5 Consultancy": [
            "3.5.1: Revenue generated from consultancy and corporate training.",
            "3.5.2: Total amount spent on developing facilities, training teachers, and staff."
        ],
        "3.6 Extension Activities": [
            "3.6.1: Extension activities carried out in the community sensitizing students to social issues.",
            "3.6.2: Awards and recognitions received for extension activities from government bodies."
        ],
        "3.7 Collaboration": [
            "3.7.1: Collaborative activities for research, Faculty exchange, Student exchange/internship.",
            "3.7.2: Number of functional MoUs with institutions of national or international importance."
        ]
    },
    "Criterion 4: Infrastructure and Learning Resources": {
        "4.1 Physical Facilities": [
            "4.1.1: Availability of adequate infrastructure and physical facilities for teaching-learning.",
            "4.1.2: Facilities for cultural activities, sports, games, gym, etc."
        ],
        "4.2 Library as a Learning Resource": [
            "4.2.1: Library is automated using Integrated Library Management System (ILMS).",
            "4.2.2: Subscription for e-resources (e-journals, e-ShodhSindhu, Shodhganga)."
        ],
        "4.3 IT Infrastructure": [
            "4.3.1: Institution frequently updates its IT facilities including Wi-Fi.",
            "4.3.2: Student-to-Computer Ratio."
        ],
        "4.4 Maintenance of Campus Infrastructure": [
            "4.4.1: Expenditure incurred on maintenance of infrastructure (physical and academic support facilities)."
        ]
    },
    "Criterion 5: Student Support and Progression": {
        "5.1 Student Support": [
            "5.1.1: Percentage of students benefited by scholarships and free ships provided by the Government.",
            "5.1.2: Capacity building and skills enhancement initiatives."
        ],
        "5.2 Student Progression": [
            "5.2.1: Percentage of placement of outgoing students and progression to higher education.",
            "5.2.2: Percentage of students qualifying in state/national/international examinations."
        ],
        "5.3 Student Participation and Activities": [
            "5.3.1: Awards/medals won by students for outstanding performance in sports/cultural activities.",
            "5.3.2: Average number of sports and cultural events/competitions organized by the institution."
        ],
        "5.4 Alumni Engagement": [
            "5.4.1: There is a registered Alumni Association that contributes significantly through financial/other services."
        ]
    },
    "Criterion 6: Governance, Leadership and Management": {
        "6.1 Institutional Vision and Leadership": [
            "6.1.1: Governance of the institution is reflective of and in tune with the vision and mission.",
            "6.1.2: Effective leadership is visible in various institutional practices."
        ],
        "6.2 Strategy Development and Deployment": [
            "6.2.1: The institutional Strategic plan is effectively deployed.",
            "6.2.2: Functioning of the institutional bodies is effective and efficient."
        ],
        "6.3 Faculty Empowerment Strategies": [
            "6.3.1: Effective welfare measures for teaching and non-teaching staff.",
            "6.3.2: Percentage of teachers provided with financial support for professional growth."
        ],
        "6.4 Financial Management and Resource Mobilization": [
            "6.4.1: Institution conducts internal and external financial audits regularly.",
            "6.4.2: Funds / Grants received from non-government bodies, individuals, philanthropists."
        ],
        "6.5 Internal Quality Assurance System": [
            "6.5.1: Internal Quality Assurance Cell (IQAC) has contributed significantly for institutionalizing quality.",
            "6.5.2: Review of teaching learning process, structures & methodologies of operations."
        ]
    },
    "Criterion 7: Institutional Values and Best Practices": {
        "7.1 Institutional Values and Social Responsibilities": [
            "7.1.1: Measures initiated by the Institution for the promotion of gender equity.",
            "7.1.2: Facilities for alternate sources of energy and energy conservation measures."
        ],
        "7.2 Best Practices": [
            "7.2.1: Two best practices successfully implemented by the Institution as per NAAC format."
        ],
        "7.3 Institutional Distinctiveness": [
            "7.3.1: Portray the performance of the Institution in one area distinctive to its priority and thrust."
        ]
    }
}

class SSRGenerator:
    """
    Orchestrates RAG context searches and calls watsonx.ai IBM Granite 
    to generate detailed, audit-ready SSR drafts.
    """
    def __init__(self, granite_service: GraniteService, rag_engine: RAGEngine):
        self.granite = granite_service
        self.rag = rag_engine

    def generate_draft(self, criterion: str, key_indicator: str, metric: str, additional_instructions: str = "") -> dict:
        """
        Retrieves relevant local institutional context and generates a 
        professionally styled NAAC Self Study Report (SSR) draft response.
        """
        # Step 1: Query local vector DB using the metric and indicator as queries
        search_query = f"{criterion} {key_indicator} {metric}"
        rag_results = self.rag.query(search_query, n_results=6)
        
        retrieved_context = rag_results["context"]
        sources = rag_results["sources"]
        
        # Step 2: Formulate Prompt
        prompt = f"""You are a professional NAAC Accreditation Consultant. Your goal is to draft a comprehensive, audit-ready Self Study Report (SSR) response for the institution under the specific metric below.

[NAAC METRIC CONTEXT]
Criterion: {criterion}
Key Indicator: {key_indicator}
Metric Name/ID: {metric}

[RETRIEVED INSTITUTIONAL DOCUMENTS AND DATA]
Use ONLY the following retrieved records and institutional documents to write your response. If numbers, data points, or dates are available in the context, quote them exactly to make the draft robust and evidence-based.
{retrieved_context}

[USER ADDITIONAL SPECIFIC INSTRUCTIONS]
{additional_instructions if additional_instructions else "None. Write a highly detailed, professional evaluation."}

---

[INSTRUCTIONS]
Write a beautifully structured response following standard NAAC SSR guidelines. Do not make up facts or figures; only use the numbers and statements given in the retrieved data. 
If the retrieved documents contain no relevant data for this metric, explicitly state:
"I could not find sufficient information in the uploaded NAAC and institutional documents."

Format the response using these sections:
1. EXECUTIVE SUMMARY: A high-level overview of the metric's compliance.
2. DETAILED DEPLOYMENT: Describe the exact processes, systems, committees, and timelines used.
3. KEY DATA POINTS & EVIDENCE: List all relevant statistics, data, and evidence documents found in the context (include references to source files).
4. AWARDS & CHALLENGES RESOLVED: Highlight outstanding points or positive feedback.
5. RECOMMENDATIONS FOR IMPROVEMENT: Suggest immediate steps to bolster documentation.

Begin drafting the SSR response now.
"""
        
        # Step 3: Run LLM inference
        system_prompt = "You are a university accreditation expert. Your language is highly academic, formal, factual, and extremely precise."
        draft_text = self.granite.generate(prompt=prompt, system_prompt=system_prompt)
        
        return {
            "draft": draft_text,
            "sources": sources,
            "context_used": retrieved_context
        }
