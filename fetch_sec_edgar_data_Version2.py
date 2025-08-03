import requests
import csv
from datetime import datetime
import pandas as pd

def get_cik_from_ticker(ticker_symbol, headers):
    sec_tickers_url = "https://www.sec.gov/files/company_tickers.json"
    try:
        print(f"Fetching CIK for ticker '{ticker_symbol}' from: {sec_tickers_url}")
        response = requests.get(sec_tickers_url, headers=headers)
        response.raise_for_status()
        ticker_data = response.json()
        ticker_symbol = ticker_symbol.upper()
        for item in ticker_data.values():
            if item["ticker"].upper() == ticker_symbol:
                return str(item["cik_str"]).zfill(10)
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching ticker data: {e}")
        return None

# --- User Input ---
user_name = input("Please enter your Name (e.g., John Doe): ")
user_email = input("Please enter your Email (e.g., john.doe@example.com): ")

headers = {
    "User-Agent": f"{user_name} ({user_email})",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Accept": "application/json",
    "Referer": "https://www.sec.gov"
}

ticker = input("Please enter the ticker symbol of the company (e.g., MSFT for Microsoft): ").strip().upper()
cik = get_cik_from_ticker(ticker, headers)

if not cik:
    print(f"Ticker symbol '{ticker}' not found.")
    exit()

# --- Fetch Entity Info ---
url_entity = f"https://data.sec.gov/submissions/CIK{cik}.json"
response_entity = requests.get(url_entity, headers=headers)
if response_entity.status_code == 200:
    entity_data = response_entity.json()
    mailing_address = entity_data.get("addresses", {}).get("mailing", {})
    business_address = entity_data.get("addresses", {}).get("business", {})
    entity_info_flat = {
        "CIK": entity_data.get("cik"),
        "Entity Name": entity_data.get("name"),
        "Mailing Street 1": mailing_address.get('street1', 'N/A'),
        "Mailing City": mailing_address.get('city', 'N/A'),
        "Mailing State/Country": mailing_address.get('stateOrCountry', 'N/A'),
        "Mailing ZIP Code": mailing_address.get('zipCode', 'N/A'),
        "Business Street 1": business_address.get('street1', 'N/A'),
        "Business City": business_address.get('city', 'N/A'),
        "Business State/Country": business_address.get('stateOrCountry', 'N/A'),
        "Business ZIP Code": business_address.get('zipCode', 'N/A'),
        "State of Incorporation": entity_data.get("stateOfIncorporation", ""),
        "EntityType": entity_data.get("entityType", "")
    }

    print("\n" + "=" * 40)
    print("Entity Information:")
    for key, value in entity_info_flat.items():
        print(f"  {key}: {value}")
    print("=" * 40)

    # Save entity info
    entity_csv_file = 'entity_information.csv'
    with open(entity_csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=entity_info_flat.keys())
        writer.writeheader()
        writer.writerow(entity_info_flat)
    print(f"Entity information written to {entity_csv_file}")
else:
    print(f"Failed to fetch entity data. Status: {response_entity.status_code}")
    exit()

# --- Fetch Financial Facts ---
url_facts = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
response_facts = requests.get(url_facts, headers=headers)
if response_facts.status_code == 200:
    facts_data = response_facts.json()
    facts = facts_data.get("facts", {})

    all_financial_facts = []

    for taxonomy, concepts in facts.items():
        for concept, details in concepts.items():
            for unit, values in details.get("units", {}).items():
                for fact in values:
                    all_financial_facts.append({
                        "Concept": concept,
                        "Taxonomy": taxonomy,
                        "Value": fact["val"],
                        "Filing Date": fact["filed"],
                        "End Date": fact["end"],
                        "Unit": unit,
                        "Fiscal Period": fact.get("fp", "N/A"),
                        "Form Type": fact.get("form", "N/A"),
                        "Accession Number": fact["accn"]
                    })

    print(f"\nExtracted {len(all_financial_facts)} financial facts.")

    if all_financial_facts:
        facts_csv_file = 'financial_facts.csv'
        fieldnames = all_financial_facts[0].keys()
        with open(facts_csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_financial_facts)
        print(f"Raw financial facts written to {facts_csv_file}")

        # ✅ Filter only the latest facts
        df = pd.DataFrame(all_financial_facts)
        df['Filing Date'] = pd.to_datetime(df['Filing Date'])
        df['End Date'] = pd.to_datetime(df['End Date'])
        df_sorted = df.sort_values(by='Filing Date', ascending=False)
        df_latest = df_sorted.drop_duplicates(subset=['Concept', 'End Date'], keep='first')

        filtered_csv_file = 'financial_facts_latest.csv'
        df_latest.to_csv(filtered_csv_file, index=False)
        print(f"Filtered (latest) financial facts written to {filtered_csv_file}")

    else:
        print("No financial facts to process.")
else:
    print(f"Failed to fetch financial facts. Status: {response_facts.status_code}")
