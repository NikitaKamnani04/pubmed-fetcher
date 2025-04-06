import requests
import xml.etree.ElementTree as ET
import re
from typing import List, Dict, Set

PHARMA_KEYWORDS = [
    "Pharma", "Biotech", "Inc.", "Ltd.", "GmbH", "Corporation", "Therapeutics",
    "Solutions", "Sciences", "Lifesciences", "Biosciences", "MedTech", "Biopharma",
    "Oncology", "Medicines", "Vaccines", "Diagnostics", "Biosystems", "Laboratories",
    "Genomics", "Biotechnology", "Theranostics", "Biologics", "Immunotherapy"
]

def is_academic(affiliation: str) -> bool:
    academic_keywords = ["University", "Institute", "Department", "Hospital",
                         "Research", "Clinic", "Center", "College", "Faculty"]
    return any(keyword.lower() in affiliation.lower() for keyword in academic_keywords)

def is_pharma_company(affiliation: str) -> bool:
    return any(re.search(rf"\b{re.escape(keyword)}\b", affiliation, re.IGNORECASE) for keyword in PHARMA_KEYWORDS)

def extract_emails(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)

def fetch_pubmed_ids(query: str, max_results: int = 50, debug: bool = False) -> List[str]:
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

def fetch_pubmed_articles(pubmed_ids: List[str], debug: bool = False) -> List[Dict[str, str]]:
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

        year = article.find(".//PubDate/Year")
        month = article.find(".//PubDate/Month")
        day = article.find(".//PubDate/Day")
        publication_date = "-".join(filter(None, [
            year.text if year is not None else "",
            month.text if month is not None else "",
            day.text if day is not None else ""
        ])) or "N/A"

        non_academic_authors = []
        company_affiliations: Set[str] = set()
        corresponding_author_emails: Set[str] = set()

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
