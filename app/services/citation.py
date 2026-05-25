def extract_citations(search_results: list) -> str:

    citations = []

    for idx, result in enumerate(search_results, start=1):

        citations.append(
            f"[{idx}] {result['url']}"
        )

    return "\n".join(citations)