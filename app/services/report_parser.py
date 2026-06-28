from app.core.llm import llm
from app.models.report import ReportSchema
from app.core.logging import logger
from datetime import datetime

def parse_markdown_to_report(query: str, markdown_report: str, route_used: str, confidence: dict = None) -> dict:
    prompt = f"""
    You are an expert data parsing assistant.
    Your task is to parse the following markdown research report into a structured research report data schema.

    ORIGINAL USER QUERY:
    {query}

    MARKDOWN REPORT:
    {markdown_report}

    Instructions:
    1. Extract a clear title.
    2. Write a 2-3 sentence executive summary of the report.
    3. Decompose the report into its primary sections.
    4. For each section, extract the heading, the main body content, and compile a list of source citations (URLs, webpage titles, and excerpts under 30 words) used inside that section.
    """
    
    try:
        structured_llm = llm.with_structured_output(ReportSchema)
        parsed_report = structured_llm.invoke(prompt)
        
        # Override metadata details to ensure precise accuracy
        parsed_report.route_used = route_used
        parsed_report.confidence = confidence
        parsed_report.generated_at = datetime.now()
        
        return parsed_report.model_dump()
    except Exception as err:
        logger.error(f"Failed to parse markdown report to structured schema: {err}", exc_info=True)
        # Safe fallback dictionary if LLM parsing fails
        return {
            "title": f"Research Report: {query}",
            "summary": "This is a structured representation of the generated markdown research report.",
            "sections": [
                {
                    "heading": "Introduction",
                    "body": markdown_report,
                    "citations": []
                }
            ],
            "confidence": confidence,
            "route_used": route_used,
            "generated_at": datetime.now()
        }
