import argparse
import json
from pubmed_scraper.pubmed import fetch_pubmed_papers, fetch_paper_details, save_to_csv

def main():
    parser = argparse.ArgumentParser(description="Fetch research papers from PubMed based on a query.")
    parser.add_argument("query", type=str, help="Search query for PubMed")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("-f", "--file", type=str, help="Specify output CSV file")

    args = parser.parse_args()

    if args.debug:
        print(f"Fetching papers for query: {args.query}")

    pubmed_ids = fetch_pubmed_papers(args.query)

    if args.debug:
        print(f"Found {len(pubmed_ids)} papers.")

    papers = fetch_paper_details(pubmed_ids)

    if args.file:
        save_to_csv(papers, args.file)
        print(f"Results saved to {args.file}")
    else:
        print(json.dumps(papers, indent=2))

if __name__ == "__main__":
    main()

