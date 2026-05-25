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