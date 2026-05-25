def format_search_results(search_results: list) -> str:

    formatted_results = []

    for idx, result in enumerate(search_results, start=1):

        formatted_results.append(
            f"""
        SOURCE {idx}

        Title:
        {result['title']}

        Content:
        {result['content']}

        URL:
        {result['url']}
        """
        )

    return "\n\n".join(formatted_results)

def format_extracted_content(extracted_contents: list):

    formatted_sections = []

    for idx, item in enumerate(extracted_contents, start=1):

        formatted_sections.append(
            f"""
        SOURCE {idx}

        URL:
        {item['url']}

        CONTENT:
        {item['raw_content'][:4000]}
        """
        )

    return "\n\n".join(formatted_sections)