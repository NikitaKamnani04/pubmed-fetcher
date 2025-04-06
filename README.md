# PubMed Paper Fetcher

A Python command-line tool to fetch and analyze PubMed research papers based on a custom search query.  
The tool identifies papers with at least one **non-academic author** affiliated with a **pharmaceutical or biotech company**, and outputs the results in a structured CSV format.


##  Project Structure

pubmed-fetcher/
├── pubmed_fetcher/
│   ├── __init__.py          # Package initializer
│   ├── core.py              # Core logic (moved from app.py)
│   └── cli.py               # CLI entry point for argument parsing
├── results.csv              # Output file
├── README.md                # Project documentation
├── pyproject.toml           # Poetry configuration
├── poetry.lock              # Poetry lock file
└── .gitignore               # Git ignored files


##  Code Overview

- **`pubmed_fetcher/core.py`**:  
  - Sends queries to the PubMed API  
  - Parses XML responses  
  - Extracts metadata (titles, authors, affiliations, etc.)  
  - Identifies **non-academic authors** based on heuristics (absence of academic terms in affiliation)  
  - Detects **pharma/biotech** affiliations using internal keyword list  
  - Extracts email addresses using regex  
  - Saves results to a CSV

- **`pubmed_fetcher/cli.py`**:  
  Handles CLI arguments using `argparse`, supports:
  - Custom query string
  - Max number of results
  - Output file
  - Debug mode


##  Installation Instructions

1. Clone the repository:

```bash
git clone https://github.com/your-username/pubmed-fetcher.git
cd pubmed-fetcher

Install Poetry (if not installed):

curl -sSL https://install.python-poetry.org | python3 -


#Install dependencies:

poetry install

#Run the program using:

poetry run get-papers-list "your query here"

Optional CLI Flags:
Flag	Description
-f, --file	Output results to a CSV file
-d, --debug	Enable debug logs
-m, --max-results	Limit number of results (default: 50)
-h, --help	Show usage

Example:

poetry run get-papers-list "biotech industry" -f results.csv -m 30 -d


# Use of External Tools
This project was built using conventional Python libraries.

However, ChatGPT by OpenAI was used to assist in:

Designing the module-based structure

Improving regex for email/keyword matching

Writing clean and modular Python code

Drafting this README.md for clarity and completeness

#Tools & Libraries Used
requests – HTTP requests to the PubMed API

xml.etree.ElementTree – XML parsing

argparse – CLI argument parsing

re – Regular expressions for email/keyword matching

csv – Exporting results

Poetry – Dependency management and packaging


#Output Format
The output CSV contains:

PubMed_ID

Title

Publication Date

Non Academic Author(s)

Company Affiliations

Corresponding Author Email

Only articles with at least one company affiliation matching a curated list of pharma/biotech keywords are included.


# Author
Nikita Kamnani
Email: nikitakamnani01@gmail.com

# License
This project is licensed under the MIT License.