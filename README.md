This project is a CLI-based PubMed scraper that fetches research papers based on a search query. It retrieves PubMed IDs, paper titles, publication dates, authors, affiliations, and corresponding author emails, filtering papers with company affiliations.

📂 Project Structure
graphql
Copy
Edit
pubmed_scraper/
│── pubmed_scraper/
│   ├── __init__.py
│   ├── cli.py           # CLI command-line interface script
│   ├── pubmed.py        # Fetching and processing PubMed data
│── pyproject.toml       # Poetry project configuration
│── README.md            # Documentation
│── requirements.txt     # Dependencies (if not using Poetry)


🛠 Installation & Setup
1️⃣ Install Poetry
Poetry is required to manage dependencies. Install it using:

pip install poetry

poetry new pubmed_scraper
cd pubmed_scraper

poetry install
✅ This installs all required dependencies, including requests, pandas, and xml.etree.ElementTree.

The program provides a command-line tool called get-papers-list that allows users to search PubMed for papers and filter them based on company affiliations.

poetry run get-papers-list "cancer treatment"
This fetches PubMed papers matching the search query "cancer treatment" and prints the results in JSON format.

🔹 2️⃣ Enable Debug Mode (-d)
To see debug information while running the script:

poetry run get-papers-list "cancer treatment" -d
✅ This prints debug messages, such as fetched PubMed IDs and filtering steps.

🔹 3️⃣ Save Results to a CSV File (-f)
To save the results to a file:

poetry run get-papers-list "cancer treatment" -f results.csv
✅ The output will be stored in results.csv, which can be opened in Excel or any text editor.

🔹 4️⃣ Show Help Menu (-h)
To display available options:
