from rich import print
from app.services.document_saver import save_document
# from app.graph.workflows.simple_research import research_graph
from app.graph.workflows.deep_research import research_graph


def main():

    print("\n[bold green]=== Research Assistant ===[/bold green]")

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
            save_document(response["final_answer"])
            print(response["final_answer"])

        except Exception as error:

            print(f"\n[red]ERROR:[/red] {error}")


if __name__ == "__main__":
    main()