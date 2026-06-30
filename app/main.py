from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.rule import Rule
from rich.status import Status

from app.graph.workflows.research_router import research_router


console = Console()


def show_banner():
    console.print(
        Panel.fit(
            "[bold cyan]Research Assistant[/bold cyan]\n"
            "[green]Powered by LangGraph + Gemini[/green]",
            border_style="blue",
        )
    )


def process_query(query: str):

    with console.status(
        "[bold green]Researching...[/bold green]",
        spinner="dots",
    ):

        response = research_router.invoke(
            {
                "query": query
            }
        )

    return response


def display_answer(answer: str):

    console.print()
    console.rule("[bold blue]Research Result[/bold blue]")

    md = Markdown(answer)

    console.print(md)

    console.rule()


def main():

    while True:
        
        show_banner()

        query = Prompt.ask(
            "\n[bold cyan]Ask Question[/bold cyan]"
        )

        if query.lower() in ["exit", "quit" , "bye"]:

            console.print(
                "\n[yellow]Goodbye![/yellow]"
            )

            break

        try:

            response = process_query(query)

            report_content = response.get("verified_report") or response.get("final_answer", "No answer compiled.")
            display_answer(
                report_content
            )

        except KeyboardInterrupt:

            console.print(
                "\n[red]Interrupted by user[/red]"
            )

        except Exception as error:

            console.print(
                Panel(
                    str(error),
                    title="ERROR",
                    border_style="red",
                )
            )


if __name__ == "__main__":
    main()