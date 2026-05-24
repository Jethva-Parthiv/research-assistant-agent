from app.graph.builder import research_graph


def main():

    while True:

        query = input("\nAsk Research Question: ")

        if query.lower() == "exit":
            break

        response = research_graph.invoke(
            {
                "query": query
            }
        )

        print("\n")
        print(response["final_answer"])


if __name__ == "__main__":
    main()