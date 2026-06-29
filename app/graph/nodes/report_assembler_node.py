import re
import difflib
from typing import List
from app.graph.state import ResearchState
from app.models.claims import ClaimResult
from app.core.logging import logger

def report_assembler_node(state: ResearchState):
    final_answer = state.get("final_answer", "").strip()
    claims: List[ClaimResult] = state.get("claims") or []
    
    if not final_answer:
        logger.warning("No final_answer found to assemble.")
        return {
            "verified_report": ""
        }
        
    lines = final_answer.split('\n')
    
    for claim in claims:
        best_score = 0.0
        best_line_idx = -1
        best_sentence_idx = -1
        
        for line_idx, line in enumerate(lines):
            stripped = line.strip()
            # Skip empty lines, headers, code blocks, or horizontal rules
            if not stripped or stripped.startswith('#') or stripped.startswith('```') or stripped.startswith('---'):
                continue
                
            # Split line into sentences
            sentences = re.split(r'(?<=[.!?])\s+', line)
            
            for s_idx, s in enumerate(sentences):
                s_clean = s.strip()
                # Ignore very short sentences or sentences that already have HTML badges injected
                if len(s_clean) < 8 or 'style="color:' in s_clean:
                    continue
                    
                score = difflib.SequenceMatcher(None, claim.claim_text, s_clean).ratio()
                if score > best_score:
                    best_score = score
                    best_line_idx = line_idx
                    best_sentence_idx = s_idx
                    
        # Apply threshold check
        if best_score > 0.45 and best_line_idx != -1:
            status = claim.status
            badge = ""
            
            if status == "verified":
                url = claim.source_url or "#"
                badge = f" [<span style=\"color:#27500A\">✓</span> source]({url})"
            elif status == "weak":
                url = claim.source_url or "#"
                badge = f" [<span style=\"color:#633806\">~</span> source]({url})"
            elif status == "unverified":
                badge = " [<span style=\"color:#791F1F\">?</span> unverified]"
            elif status == "conflicted":
                badge = " [<span style=\"color:#791F1F\">⚡</span> conflicted]"
                
            if badge:
                line_to_modify = lines[best_line_idx]
                sentences = re.split(r'(?<=[.!?])\s+', line_to_modify)
                
                # Inject badge immediately after matched sentence
                sentences[best_sentence_idx] = sentences[best_sentence_idx] + badge
                lines[best_line_idx] = " ".join(sentences)
                
    # Build ## Sources section
    sources_section = "\n\n## Sources\n"
    source_count = 1
    
    for claim in claims:
        if claim.status in ["verified", "weak"] and claim.source_url:
            url = claim.source_url
            excerpt = (claim.source_passage or "").strip()
            
            # Truncate excerpt to 30 words if necessary
            words = excerpt.split()
            if len(words) > 30:
                truncated_excerpt = " ".join(words[:30]) + "..."
            else:
                truncated_excerpt = excerpt
                
            if url and truncated_excerpt:
                sources_section += f"\n- [{source_count}] [{url}]({url})\n  - *Excerpt*: \"{truncated_excerpt}\"\n"
                source_count += 1
                
    if source_count > 1:
        verified_report = "\n".join(lines) + sources_section
    else:
        verified_report = "\n".join(lines)
        
    logger.info("Report assembly complete. Injected status badges and compiled Sources list.")
    
    return {
        "verified_report": verified_report
    }
