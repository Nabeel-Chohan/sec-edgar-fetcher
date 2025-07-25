import requests
from datetime import datetime

def get_cik_from_ticker(ticker_symbol, headers):
    """
    Retrieves the CIK number for a given ticker symbol from the SEC's company_tickers.json file.
    """
    sec_tickers_url = "https://www.sec.gov/files/company_tickers.json"

    try:
        print(f"Fetching CIK for ticker '{ticker_symbol}' from: {sec_tickers_url}")
        response = requests.get(sec_tickers_url, headers=headers)
        response.raise_for_status()

        ticker_data = response.json()
        print("Ticker data fetched successfully.\n")

        ticker_symbol = ticker_symbol.upper()

        for item in ticker_data.values():
            if item["ticker"].upper() == ticker_symbol:
                return str(item["cik_str"]).zfill(10)

        return None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching ticker data: {e}")
        return None

# --- Agent Information Prompt ---
user_name = input("Please enter your Name (e.g., John Doe): ")
user_email = input("Please enter your Email (e.g., john.doe@example.com): ")

# ✅ Updated headers block
headers = {
    "User-Agent": f"{user_name} ({user_email})",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Accept": "application/json",
    "Referer": "https://www.sec.gov"
}

# Prompt for ticker
ticker = input("Please enter the ticker symbol of the company (e.g., MSFT for Microsoft): ").strip().upper()

# Dynamically fetch the CIK
cik = get_cik_from_ticker(ticker, headers)

if not cik:
    print(f"Ticker symbol '{ticker}' not found.")
    exit()

# SEC API endpoints
url_entity = f"https://data.sec.gov/submissions/CIK{cik}.json"
url_facts = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"

# Fetch entity data
response_entity = requests.get(url_entity, headers=headers)
if response_entity.status_code == 200:
    entity_data = response_entity.json()

    entity_info = {
        "CIK": entity_data.get("cik"),
        "Entity Name": entity_data.get("name"),
        "Mailing Address": entity_data.get("addresses", {}).get("mailing", {}),
        "Business Address": entity_data.get("addresses", {}).get("business", {}),
        "State of Incorporation": entity_data.get("stateOfIncorporation", ""),
        "EntityType": entity_data.get("entityType", "")
    }

    print("\n" + "=" * 40)
    print("Entity Information:")
    print("-" * 30)
    print(f"CIK: {entity_info['CIK']}")
    print(f"Entity Name: {entity_info['Entity Name']}")

    mailing = entity_info['Mailing Address']
    print("\nMailing Address:")
    print(f"  Street: {mailing.get('street1', 'N/A')}")
    print(f"  City: {mailing.get('city', 'N/A')}")
    print(f"  State/Country: {mailing.get('stateOrCountry', 'N/A')}")
    print(f"  ZIP Code: {mailing.get('zipCode', 'N/A')}")

    business = entity_info['Business Address']
    print("\nBusiness Address:")
    print(f"  Street: {business.get('street1', 'N/A')}")
    print(f"  City: {business.get('city', 'N/A')}")
    print(f"  State/Country: {business.get('stateOrCountry', 'N/A')}")
    print(f"  ZIP Code: {business.get('zipCode', 'N/A')}")

    print(f"\nState of Incorporation: {entity_info['State of Incorporation']}")
    print(f"Entity Type: {entity_info['EntityType']}")
    print("=" * 40)
else:
    print(f"Failed to fetch entity data for CIK {cik}. HTTP Status Code: {response_entity.status_code}")
    exit()

# Fetch financial facts data
response_facts = requests.get(url_facts, headers=headers)
if response_facts.status_code == 200:
    facts_data = response_facts.json()
    facts = facts_data.get("facts", {})

    current_year = str(datetime.now().year)
    most_recent_concepts_current_year = {}

    for taxonomy, concepts in facts.items():
        for concept, details in concepts.items():
            for unit, values in details.get("units", {}).items():
                values_current_year = [v for v in values if v["filed"].startswith(current_year)]
                if values_current_year:
                    recent = sorted(values_current_year, key=lambda x: x["filed"], reverse=True)[0]
                    most_recent_concepts_current_year[concept] = {
                        "taxonomy": taxonomy,
                        "value": recent["val"],
                        "filing_date": recent["filed"],
                        "end_date": recent["end"],
                        "unit": unit,
                        "fiscal_period": recent.get("fp", "N/A"),
                        "form_type": recent.get("form", "N/A"),
                        "accession_number": recent["accn"]
                    }

    print("\n" + "=" * 40)
    print(f"Most Recent Filed Concepts for {entity_info['Entity Name']} (Current Year Only):")
    print("-" * 30)
    if most_recent_concepts_current_year:
        for concept, details in most_recent_concepts_current_year.items():
            print(f"\nConcept: {concept}")
            print(f"  Taxonomy: {details['taxonomy']}")
            print(f"  Value: {details['value']}")
            print(f"  Filing Date: {details['filing_date']}")
            print(f"  End Date: {details['end_date']}")
            print(f"  Unit: {details['unit']}")
            print(f"  Fiscal Period: {details['fiscal_period']}")
            print(f"  Form Type: {details['form_type']}")
            print(f"  Accession Number: {details['accession_number']}")
    else:
        print("No financial facts found for the current year.")
    print("=" * 40)
else:
    print(f"Failed to fetch financial facts for CIK {cik}. HTTP Status Code: {response_facts.status_code}")
