import requests
import pandas as pd
import re
from xml.etree import ElementTree as ET
from typing import List, Dict, Optional

# ✅ PubMed API URLs
PUBMED_API_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

# ✅ Keywords for detecting company affiliations
NON_ACADEMIC_KEYWORDS = [
    "pharma", "biotech", "inc", "ltd", "corp", "gmbh", "s.a.", "s.r.l.", "llc",
    "co.", "laboratories", "technologies", "research institute", "private limited",
    "medical center", "hospital", "research lab", "clinical research", "drug development"
]

def extract_email(text: str) -> Optional[str]:
    """Extract the first email address from a given text."""
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else None

def clean_affiliation(affiliation: str) -> str:
    """Remove email addresses from affiliations to avoid duplicates."""
    return re.sub(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "", affiliation).strip()

def fetch_pubmed_papers(query: str, max_results: int = 10) -> List[str]:
    """Fetch PubMed paper IDs based on a query."""
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": max_results
    }
    response = requests.get(PUBMED_API_URL, params=params)
    response.raise_for_status()
    data = response.json()
    return data.get("esearchresult", {}).get("idlist", [])

def fetch_paper_details(pubmed_ids: List[str]) -> List[Dict[str, Optional[str]]]:
    """Fetch detailed information about each paper, ensuring unique authors and affiliations."""
    if not pubmed_ids:
        return []

    params = {
        "db": "pubmed",
        "id": ",".join(pubmed_ids),
        "retmode": "xml"
    }
    response = requests.get(PUBMED_FETCH_URL, params=params)
    response.raise_for_status()

    root = ET.fromstring(response.text)
    papers = []

    for article in root.findall(".//PubmedArticle"):
        try:
            pmid = article.find(".//PMID").text
            title = article.find(".//ArticleTitle").text if article.find(".//ArticleTitle") is not None else "N/A"

            # ✅ Extract publication date correctly
            pub_date = article.find(".//PubDate/Year")
            if pub_date is None:
                pub_date = article.find(".//PubDate/MedlineDate")
            pub_date = pub_date.text if pub_date is not None else "N/A"

            non_academic_authors = set()
            company_affiliations = set()
            corresponding_email = None  # ✅ Start with None instead of "N/A"

            # ✅ Iterate through all authors
            for author in article.findall(".//Author"):
                last_name = author.find("LastName")
                first_name = author.find("ForeName")
                full_name = f"{first_name.text} {last_name.text}" if first_name is not None and last_name is not None else "Unknown"

                # ✅ Extract affiliations from multiple sources
                affiliations = set()
                
                # 1️⃣ **Extract from `<AffiliationInfo>/<Affiliation>`**
                for affil in author.findall(".//AffiliationInfo/Affiliation"):
                    if affil.text:
                        affiliations.add(affil.text)

                # 2️⃣ **Check `<Affiliation>` outside `<AffiliationInfo>`**
                for affil in article.findall(".//Affiliation"):
                    if affil.text:
                        affiliations.add(affil.text)

                # ✅ **Extract the first email before cleaning affiliations**
                for affil_text in affiliations:
                    if corresponding_email is None:  # ✅ Extract first valid email
                        extracted_email = extract_email(affil_text)
                        if extracted_email:
                            corresponding_email = extracted_email

                # ✅ **Check if affiliations match company-related keywords**
                for affil_text in affiliations:
                    cleaned_affil = clean_affiliation(affil_text)  # ✅ Remove emails before storing
                    if any(keyword in cleaned_affil.lower() for keyword in NON_ACADEMIC_KEYWORDS):
                        non_academic_authors.add(full_name)
                        company_affiliations.add(cleaned_affil)  # ✅ Ensures unique affiliations

            # ✅ **Only include papers that have company affiliations**
            if company_affiliations:
                papers.append({
                    "PubmedID": pmid,
                    "Title": title,
                    "Publication Date": pub_date,
                    "Non-academic Author(s)": ", ".join(sorted(non_academic_authors)),  # Unique authors
                    "Company Affiliation(s)": ", ".join(sorted(company_affiliations)),  # Unique affiliations
                    "Corresponding Author Email": corresponding_email if corresponding_email else "N/A"  # ✅ Set "N/A" if no email found
                })

        except Exception as e:
            print(f"Error parsing article {pmid}: {str(e)}")

    return papers

def save_to_csv(papers: List[Dict[str, Optional[str]]], filename: str):
    """Save the filtered research papers to a well-structured CSV file."""
    if not papers:
        print("No records found. CSV file not created.")
        return

    # ✅ Define the column order explicitly
    columns = ["PubmedID", "Title", "Publication Date", "Non-academic Author(s)",
               "Company Affiliation(s)", "Corresponding Author Email"]

    # ✅ Create a DataFrame
    df = pd.DataFrame(papers, columns=columns)

    # ✅ Save as CSV with proper encoding and formatting
    df.to_csv(filename, index=False, encoding="utf-8-sig")

    print(f"CSV file saved: {filename}")
