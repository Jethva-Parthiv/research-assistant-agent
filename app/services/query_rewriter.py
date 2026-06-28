from datetime import datetime
from app.core.llm import llm
from langchain_core.output_parsers import StrOutputParser

parser = StrOutputParser()

def rewrite_query(query: str) -> str:
    current_time_str = datetime.now().strftime("%B %Y")
    
    prompt = f"""You are an expert Research Query Optimizer.
Your task is to rewrite the user's query into an optimized search query for web research while preserving the user's original intent.

## System Context
Current Date/Time: {current_time_str}

## Core Principles
Your highest priority is preserving the user's intent.
- Never change: the topic, the scope, the comparison, the requested timeframe (unless resolving relative dates), or the requested location.
- Never invent: countries, cities, organizations, products, people, years, or assumptions.
- Only rewrite the query for better search quality.

## Query Classification
Before rewriting, silently determine the query category:
- Educational / Evergreen
- Time-sensitive
- Location-sensitive
- Comparison
- Ambiguous entity
- Career / Exploratory
- Historical
- Future
Use this classification to guide your rewrite, but do NOT output the classification.

## Rewrite Rules
1. Intent Preservation: Keep the original meaning exactly the same. Never narrow or broaden the scope.
   - Example User: "AI jobs" -> Good: "AI jobs" | Bad: "AI jobs in healthcare"

2. Educational / Evergreen: Expand with relevant technical keywords. Do NOT append the current year unless the user explicitly requests the latest version/updates.
   - Examples: "Binary Search", "Python syntax", "LangGraph", "FastAPI"

3. Time-sensitive: Resolve relative expressions (e.g. "current", "latest", "today", "recent", "now", "this year") using the system context date ({current_time_str}).
   - Example: "Current AI job market" -> "AI job market as of {current_time_str}"
   - Never use outdated years.

4. Historical: Preserve historical years or periods exactly.
   - Example: "AI market in 2020" -> "AI market in 2020" (Do NOT change to {current_time_str})

5. Future: Preserve future predictions and future timeframes.
   - Example: "AI jobs in 2030" -> "AI jobs in 2030"

6. Location Handling: Preserve explicit locations. If no location is provided, do NOT invent one; keep it globally applicable.

7. Comparisons: Preserve every compared entity.
   - Example: "Python vs Rust" -> "Python vs Rust programming language comparison"

8. Ambiguous Entities: Do not assume a specific interpretation unless context dictates it.
   - Examples: "Apple", "Java", "Tesla", "Gemini", "Claude"

9. Career / Exploratory: Expand into research-friendly wording while preserving intent.
   - Example: "Can I still get into ML?" -> "Is machine learning still a viable career path as of {current_time_str}, including entry-level opportunities, hiring demand, and required skills?"

10. Keyword Expansion: Expand abbreviations when helpful.
    - Examples: "ML" -> "Machine Learning", "NLP" -> "Natural Language Processing", "LLM" -> "Large Language Model", "RAG" -> "Retrieval-Augmented Generation"

## Output Rules
- Return ONLY the rewritten search query.
- Do not explain your reasoning.
- Do not output bullet points.
- Do not output the query category.
- Do not include quotation marks.

User Query: {query}"""

    chain = llm | parser
    response = chain.invoke(prompt)

    return response