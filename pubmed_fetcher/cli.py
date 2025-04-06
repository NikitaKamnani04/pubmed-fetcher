import click
import csv
from .core import fetch_pubmed_ids, fetch_pubmed_articles

@click.command()
@click.argument("query")
@click.option("-f", "--filename", default="results.csv", help="Output CSV file name")
@click.option("-m", "--max-results", default=30, help="Maximum number of results to fetch")
@click.option("-d", "--debug", is_flag=True, help="Enable debug mode")
def get_papers_list(query: str, filename: str, max_results: int, debug: bool):
    pubmed_ids = fetch_pubmed_ids(query, max_results=max_results, debug=debug)
    articles = fetch_pubmed_articles(pubmed_ids, debug=debug)

    if not articles:
        print("No articles with pharma/biotech affiliations found.")
        return

    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "PubMed_ID", "Title", "Publication Date",
            "Non Academic Author(s)", "Company Affiliations", "Corresponding Author Email"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(articles)

    print(f"Results saved to {filename}")

def main():
    get_papers_list()

if __name__ == "__main__":
    main()
