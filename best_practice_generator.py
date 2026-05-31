import os
from granite_service import GraniteService
from rag import RAGEngine

class BestPracticeGenerator:
    """
    Formulates NAAC-compliant Best Practice reports based on user inputs 
    and supporting evidence extracted from ChromaDB.
    """
    def __init__(self, granite_service: GraniteService, rag_engine: RAGEngine):
        self.granite = granite_service
        self.rag = rag_engine

    def generate_practice(self, initiative: str, objective: str, activities: str, outcomes: str) -> dict:
        """
        Takes raw initiative details, performs a semantic search to identify corroborating institutional documents,
        and prompts IBM Granite to generate a formal NAAC Best Practice report.
        """
        # Step 1: Query ChromaDB for supporting metrics or evidence
        search_query = f"{initiative} {objective} {outcomes}"
        rag_results = self.rag.query(search_query, n_results=5)
        
        retrieved_context = rag_results["context"]
        sources = rag_results["sources"]
        
        # Step 2: Create structured Prompt for NAAC compliant best practice
        prompt = f"""You are a senior university quality assurance officer. Your task is to draft a comprehensive "Best Practice" document in the official NAAC format. 

[USER INITIATIVE SUMMARY]
Initiative Name / Title: {initiative}
Objectives stated: {objective}
Activities conducted: {activities}
Stated outcomes: {outcomes}

[SUPPORTING EVIDENCE & EVIDENCE FOUND IN SYSTEM]
Integrate references and quantitative data points from these retrieved files:
{retrieved_context}

---

[STRUCTURE REQUIREMENTS]
Your output MUST follow the official 6-part NAAC Best Practice format exactly:

1. TITLE OF THE PRACTICE: A catchy, professional title.
2. OBJECTIVES OF THE PRACTICE: Bulleted list outlining what the practice intends to achieve, its conceptual framework, and goals.
3. THE CONTEXT: Describe the contextual features or challenging issues that needed to be addressed in designing and implementing this practice. (What problem was the university facing?)
4. THE PRACTICE: Elaborate on the practice and its implementation. Describe how it is unique in the context of Indian Higher Education. Highlight constraints or limitations faced.
5. EVIDENCE OF SUCCESS: Provide concrete, quantifiable evidence of success (e.g., stats, percentages, specific outcomes). Use figures from the retrieved files if available. Show how the practice has improved the university.
6. PROBLEMS ENCOUNTERED AND RESOURCES REQUIRED: Identify the main obstacles, bottlenecks, or challenges faced during implementation, and specify the resources (financial, human, technical) required to resolve them.

Begin drafting the NAAC Best Practice report now.
"""
        
        # Step 3: Run LLM Inference
        system_prompt = "You are a university Quality Director. Your tone is highly professional, inspiring, authoritative, and extremely detailed."
        report_text = self.granite.generate(prompt=prompt, system_prompt=system_prompt)
        
        return {
            "report": report_text,
            "sources": sources,
            "context_used": retrieved_context
        }
