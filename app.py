import requests
import xml.etree.ElementTree as ET
import csv
import argparse
import re

# Pharma/Biotech keyword list
PHARMA_KEYWORDS = [
    "Pharma", "Biotech", "Inc.", "Ltd.", "GmbH", "Corporation", "Therapeutics",
    "Solutions", "Sciences", "Lifesciences", "Biosciences", "MedTech", "Biopharma",
    "Oncology", "Medicines", "Vaccines", "Diagnostics", "Biosystems", "Laboratories",
    "Genomics", "Biotechnology", "Theranostics", "Biologics", "Immunotherapy"
]

def is_academic(affiliation):
    academic_keywords = ["University", "Institute", "Department", "Hospital",
                         "Research", "Clinic", "Center", "College", "Faculty"]
    return any(keyword.lower() in affiliation.lower() for keyword in academic_keywords)

def is_pharma_company(affiliation):
    return any(re.search(rf"\b{re.escape(keyword)}\b", affiliation, re.IGNORECASE) for keyword in PHARMA_KEYWORDS)

def extract_emails(text):
    return re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)

def fetch_pubmed_ids(query, max_results=50, debug=False):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {"db": "pubmed", "term": query, "retmode": "xml", "retmax": max_results}

    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        print(" Error fetching PubMed IDs")
        return []

    root = ET.fromstring(response.text)
    pubmed_ids = [id_elem.text for id_elem in root.findall(".//Id")]

    if debug:
        print(f"[DEBUG] PubMed IDs fetched: {pubmed_ids}")

    return pubmed_ids

def fetch_pubmed_articles(pubmed_ids, debug=False):
    if not pubmed_ids:
        return []

    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {"db": "pubmed", "id": ",".join(pubmed_ids), "retmode": "xml"}

    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        print(" Error fetching article details")
        return []

    root = ET.fromstring(response.text)
    articles = []

    for article in root.findall(".//PubmedArticle"):
        pmid = article.find(".//PMID").text if article.find(".//PMID") is not None else "N/A"
        title = article.find(".//ArticleTitle").text if article.find(".//ArticleTitle") is not None else "N/A"

        # Extract full publication date
        year = article.find(".//PubDate/Year")
        month = article.find(".//PubDate/Month")
        day = article.find(".//PubDate/Day")
        publication_date = "-".join(filter(None, [
            year.text if year is not None else "",
            month.text if month is not None else "",
            day.text if day is not None else ""
        ])) or "N/A"

        non_academic_authors = []
        company_affiliations = set()
        corresponding_author_emails = set()

        for author in article.findall(".//Author"):
            last_name = author.find("LastName")
            fore_name = author.find("ForeName")
            affiliation = author.find(".//AffiliationInfo/Affiliation")

            last = last_name.text if last_name is not None else ""
            fore = fore_name.text if fore_name is not None else ""
            full_name = f"{fore} {last}".strip()

            if affiliation is not None and affiliation.text:
                aff_text = affiliation.text.strip()

                if not is_academic(aff_text):
                    non_academic_authors.append(f"{full_name} ({aff_text})")

                if is_pharma_company(aff_text):
                    company_affiliations.add(aff_text)

                corresponding_author_emails.update(extract_emails(aff_text))

        if company_affiliations:
            articles.append({
                "PubMed_ID": pmid,
                "Title": title,
                "Publication Date": publication_date,
                "Non Academic Author(s)": "; ".join(non_academic_authors) if non_academic_authors else "None",
                "Company Affiliations": "; ".join(company_affiliations),
                "Corresponding Author Email": "; ".join(corresponding_author_emails) if corresponding_author_emails else "N/A"
            })

    if debug:
        print(f"[DEBUG] Total articles found with pharma affiliations: {len(articles)}")

    return articles

def main():
    parser = argparse.ArgumentParser(description="Fetch PubMed papers with pharma/biotech affiliations.")
    parser.add_argument("query", type=str, help="PubMed search query (quoted)")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug output")
    parser.add_argument("-f", "--file", type=str, help="CSV file to save results")
    parser.add_argument("-m", "--max-results", type=int, default=50, help="Max number of articles (default=50)")

    args = parser.parse_args()

    pubmed_ids = fetch_pubmed_ids(args.query, args.max_results, args.debug)
    if not pubmed_ids:
        print(" No results found for this query.")
        return

    articles = fetch_pubmed_articles(pubmed_ids, args.debug)

    if not articles:
        print(" No articles with pharma/biotech affiliations found.")
        return

    if args.file:
        with open(args.file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "PubMed_ID", "Title", "Publication Date",
                "Non Academic Author(s)", "Company Affiliations", "Corresponding Author Email"
            ])
            writer.writeheader()
            writer.writerows(articles)
        print(f" Results saved to {args.file}")
    else:
        for article in articles:
            print("\n--- Article ---")
            for key, value in article.items():
                print(f"{key}: {value}")

if __name__ == "__main__":
    main()
