import requests
from datetime import datetime

# --- Agent Information Prompt ---
# The SEC EDGAR API requires a descriptive User-Agent header to identify the source of requests.
# This helps them manage traffic and provide better service. Please provide your name and email.
user_name = input("Please enter your Name (e.g., John Doe): ")
user_email = input("Please enter your Email (e.g., john.doe@example.com): ")

# SEC EDGAR User-Agent details
headers = {
   "User-Agent": f"{user_name} ({user_email})",
   "Accept-Encoding": "gzip, deflate",
   "Host": "data.sec.gov",
   "Connection": "keep-alive",
}

# PROMPT FOR CIK
# Define the CIK and API URLs
cik = input("Please enter the CIK code of the company (e.g., 0000789019 for Microsoft): ")
# Ensure CIK is zero-padded to 10 digits as required by SEC API for some endpoints
cik = cik.zfill(10)

url_entity = f"https://data.sec.gov/submissions/CIK{cik}.json"
url_facts = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"

# Fetch entity data
response_entity = requests.get(url_entity, headers=headers)
if response_entity.status_code == 200:
   entity_data = response_entity.json()
   # Extract basic entity information
   entity_info = {
       "CIK": entity_data.get("cik"),
       "Entity Name": entity_data.get("name"),
       "Mailing Address": entity_data.get("addresses", {}).get("mailing", {}),
       "Business Address": entity_data.get("addresses", {}).get("business", {}),
       "State of Incorporation": entity_data.get("stateOfIncorporation", ""),
       "EntityType": entity_data.get("entityType", "")
   }
   # Print the extracted entity information
   print("\n" + "="*40)
   print("Entity Information:")
   print("-" * 30)
   print(f"CIK: {entity_info['CIK']}")
   print(f"Entity Name: {entity_info['Entity Name']}")
   print("\nMailing Address:")
   mailing_address = entity_info['Mailing Address']
   print(f"  Street: {mailing_address.get('street1', 'N/A')}")
   print(f"  City: {mailing_address.get('city', 'N/A')}")
   print(f"  State/Country: {mailing_address.get('stateOrCountry', 'N/A')}")
   print(f"  ZIP Code: {mailing_address.get('zipCode', 'N/A')}")

   print("\nBusiness Address:")
   business_address = entity_info['Business Address']
   print(f"  Street: {business_address.get('street1', 'N/A')}")
   print(f"  City: {business_address.get('city', 'N/A')}")
   print(f"  State/Country: {business_address.get('stateOrCountry', 'N/A')}")
   print(f"  ZIP Code: {business_address.get('zipCode', 'N/A')}")

   print(f"\nState of Incorporation: {entity_info['State of Incorporation']}")
   print(f"Entity Type: {entity_info['EntityType']}")
   print("="*40)
else:
   print(f"Failed to fetch entity data for CIK {cik}. HTTP Status Code: {response_entity.status_code}")
   print("Please ensure the CIK is correct and try again.")
   exit() # Exit if entity data cannot be fetched, as facts data won't work either

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
               # Filter values filed in the current year
               values_current_year = [v for v in values if v["filed"].startswith(current_year)]
               if values_current_year:
                   # Sort by filing date to get the most recent entry for each concept in the current year
                   recent_data = sorted(values_current_year, key=lambda x: x["filed"], reverse=True)[0]
                   most_recent_concepts_current_year[concept] = {
                       "taxonomy": taxonomy,
                       "value": recent_data["val"],
                       "filing_date": recent_data["filed"],
                       "end_date": recent_data["end"],
                       "unit": unit,
                       "fiscal_period": recent_data.get("fp", "N/A"),
                       "form_type": recent_data.get("form", "N/A"),
                       "accession_number": recent_data["accn"]
                   }

   print("\n" + "="*40)
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
       print(f"No financial facts found for {entity_info['Entity Name']} in the current year.")
   print("="*40)
else:
   print(f"Failed to fetch financial facts data for CIK {cik}. HTTP Status Code: {response_facts.status_code}")
   print("Please ensure the CIK is correct and try again.")