import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GraniteService:
    """
    Dedicated service for interfacing with IBM Granite Instruct foundation models 
    via the watsonx.ai Python SDK.
    """
    
    def __init__(self):
        self.api_key = os.getenv("IBM_API_KEY")
        self.project_id = os.getenv("PROJECT_ID")
        self.url = os.getenv("IBM_URL", "https://us-south.ml.cloud.ibm.com")
        self.model_id = os.getenv("IBM_MODEL_ID", "ibm/granite-3-8b-instruct")
        
        self.client = None
        self.model = None
        self.is_configured = False
        
        # Try to initialize the watsonx.ai client
        if self.api_key and self.project_id:
            try:
                from ibm_watsonx_ai.foundation_models import ModelInference
                from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
                
                generate_params = {
                    GenParams.MAX_NEW_TOKENS: 1024,
                    GenParams.MIN_NEW_TOKENS: 1,
                    GenParams.DECODING_METHOD: "greedy",
                    GenParams.TEMPERATURE: 0.0,
                    GenParams.REPETITION_PENALTY: 1.1
                }
                
                self.model = ModelInference(
                    model_id=self.model_id,
                    params=generate_params,
                    credentials={
                        "apikey": self.api_key,
                        "url": self.url
                    },
                    project_id=self.project_id
                )
                self.is_configured = True
            except Exception as e:
                print(f"Error initializing Watsonx.ai ModelInference: {e}")
                self.is_configured = False
        else:
            print("Watsonx.ai credentials not fully specified in .env. Running in Fallback/Demo Mode.")
            self.is_configured = False

    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """
        Sends a prompt to the IBM Granite model or falls back to a high-quality local heuristic
        response if watsonx.ai credentials are not configured.
        """
        if self.is_configured and self.model:
            try:
                # Combine system prompt if provided
                full_prompt = prompt
                if system_prompt:
                    full_prompt = f"{system_prompt}\n\n{prompt}"
                
                response = self.model.generate_text(prompt=full_prompt)
                return response.strip()
            except Exception as e:
                print(f"Watsonx.ai generation error: {e}. Falling back to demo mode.")
                return self._generate_fallback(prompt)
        else:
            return self._generate_fallback(prompt)

    def _generate_fallback(self, prompt: str) -> str:
        """
        Generates a premium, high-quality fallback response by analyzing the prompt structure
        and extracting context references directly from the prompt text, ensuring a 
        fully functional offline/demo experience.
        """
        # Extract question if marked in prompt
        question_match = re.search(r"Question:\s*(.*)", prompt, re.IGNORECASE)
        question = question_match.group(1).strip() if question_match else ""
        
        # Extract context if present in prompt
        context_match = re.search(r"Context:\s*(.*?)(?=\n\nQuestion:|\Z)", prompt, re.DOTALL | re.IGNORECASE)
        context = context_match.group(1).strip() if context_match else ""
        
        # Check if they are asking a specific question but context is empty or says not found
        if not context or "sufficient information" in context.lower() or "no relevant context" in context.lower():
            # If they asked a generic criteria question, let's provide a useful default response
            if "criterion 3" in question.lower() or "criterion 3" in prompt.lower():
                return (
                    "**[DEMO MODE: Watsonx Credentials Not Configured]**\n\n"
                    "Based on standard NAAC manuals, **Criterion 3** covers **Research, Innovations and Extension**.\n\n"
                    "### Key Requirements:\n"
                    "1. **Promotion of Research and Facilities**: Availability of seed money, research fellowships, and state-of-the-art equipment.\n"
                    "2. **Resource Mobilization for Research**: Total grants received for research projects from government and non-government agencies.\n"
                    "3. **Innovation Ecosystem**: Initiatives like incubation centers, IP protection (patents), and start-up support.\n"
                    "4. **Research Publications and Awards**: Quality of journals indexed in UGC-CARE, Scopus, or Web of Science, and research papers published per teacher.\n"
                    "5. **Extension Activities**: Social outreach, Swachh Bharat initiatives, blood donation camps, and awards received for extension.\n"
                    "6. **Collaboration**: Functional MoUs, student exchanges, and collaborative research activities.\n\n"
                    "*Configure your `IBM_API_KEY` and `PROJECT_ID` in `.env` to enable full IBM Granite-powered analysis.*"
                )
            elif "criterion 2" in question.lower() or "criterion 2" in prompt.lower():
                return (
                    "**[DEMO MODE: Watsonx Credentials Not Configured]**\n\n"
                    "Based on standard NAAC guidelines, **Criterion 2** focuses on **Teaching-Learning and Evaluation**.\n\n"
                    "### Key Indicators & Requirements:\n"
                    "* **2.1 Student Enrollment and Profile**: Average enrollment percentage and compliance with reservation policies.\n"
                    "* **2.2 Student Diversity**: Assessment of learning levels (slow vs. advanced learners), and student-to-teacher ratios.\n"
                    "* **2.3 Teaching-Learning Process**: Student-centric methods, experiential learning, and implementation of ICT tools.\n"
                    "* **2.4 Teacher Quality**: Percentage of full-time teachers with Ph.D./NET/SET and their average experience.\n"
                    "* **2.5 Evaluation Process and Reforms**: Transparency, robustness, and grievance redressal systems for examinations.\n"
                    "* **2.6 Student Performance and Learning Outcomes**: Attainment of Program Outcomes (POs) and Course Outcomes (COs) (specifically Metric 2.6.1 requires explaining their public display and evaluation).\n\n"
                    "*Configure your `IBM_API_KEY` and `PROJECT_ID` in `.env` to generate fully custom reports via IBM Granite.*"
                )
            elif "criterion 5" in question.lower() or "criterion 5" in prompt.lower():
                return (
                    "**[DEMO MODE: Watsonx Credentials Not Configured]**\n\n"
                    "For **Criterion 5 (Student Support and Progression)**, the typical documentation and evidence required include:\n\n"
                    "### Required Evidence Checklist:\n"
                    "1. **Scholarship Records**: Government and non-government scholarship certificates, lists of beneficiary students, and audited statements.\n"
                    "2. **Capacity Building Schemes**: Reports, brochures, and photographs with date and caption for Soft Skills, Language & Communication, Life Skills, and ICT/Computing skills programs.\n"
                    "3. **Career Counseling and Guidance**: Annual reports, attendance registers, and resource person details for competitive exam coaching.\n"
                    "4. **Placement Records**: Placement letters, salary slips, and list of students placed with company names.\n"
                    "5. **Student Progression**: Higher education admission letters and enrollment records.\n"
                    "6. **Alumni Engagement**: Registration certificates, financial contributions, and lists of alumni-supported initiatives.\n\n"
                    "*To query uploaded files using active Granite LLM, specify the `IBM_API_KEY` and `PROJECT_ID` inside `.env`.*"
                )
            return (
                "I could not find sufficient information in the uploaded NAAC and institutional documents."
            )
        
        # We have context retrieved via RAG! Let's synthesize a summary from the retrieved chunks.
        # Clean up chunk tags and form a beautiful layout
        clean_context = re.sub(r"\[Source:.*?\]", "", context)
        lines = [line.strip() for line in clean_context.split("\n") if line.strip()]
        
        # Extract unique sentences to make it look professional
        sentences = []
        for line in lines[:10]:
            parts = re.split(r'(?<=[.!?])\s+', line)
            for part in parts:
                if len(part) > 20 and part not in sentences:
                    sentences.append(part)
        
        # Build synthesis
        synthesis = "\n".join([f"- {s}" for s in sentences[:5]])
        
        return (
            "**[DEMO MODE: Watsonx Credentials Not Configured. Using Local RAG Context]**\n\n"
            f"Based on the uploaded institutional and NAAC records, here is the retrieved documentation relevant to: *{question or 'your request'}*\n\n"
            f"{synthesis}\n\n"
            "*(Configure your Watsonx `IBM_API_KEY` and `PROJECT_ID` in your `.env` file to unlock standard generative summaries via IBM Granite).*"
        )
