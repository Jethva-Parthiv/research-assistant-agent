from app.graph.builder import research_graph


def main():

    print("\n=== Research Assistant Agent ===")

    while True:

        query = input("\nAsk Question: ")

        if query.lower() == "exit":
            break

        try:

            response = research_graph.invoke(
                {
                    "query": query
                }
            )

            print("\n")
            print(response["final_answer"])

        except Exception as error:

            print(f"\nError: {error}")


if __name__ == "__main__":
    main()