## 📄 sec-edgar-fetcher

A Python tool to fetch and display company information and financial facts from the SEC EDGAR API using a company's **ticker symbol** (e.g., `MSFT`, `AAPL`).

### 🔍 What It Does

This script allows users to:

* Input a company’s **stock ticker** to automatically look up its Central Index Key (CIK)
* Access and display entity details (e.g., name, addresses, incorporation state)
* Extract and present **most recent financial facts** filed in the current year
* Communicate responsibly with the SEC EDGAR system using a valid User-Agent

---

### 🚀 Getting Started

#### 📦 Prerequisites

* Python 3.7 or higher
* Internet connection (to access SEC APIs)
* `requests` library installed

#### 💻 Installation

```bash
git clone https://github.com/Nabeel-Chohan/sec-edgar-fetcher.git
cd sec-edgar-fetcher
pip install -r requirements.txt
```

#### 📌 Usage

Run the script:

```bash
python edgar_fetcher.py
```

You’ll be prompted to enter:

* Your **name** and **email** (used as SEC-compliant User-Agent)
* A company’s **ticker symbol** (e.g., `MSFT`, `AAPL`, `TSLA`)

The script will:

* Look up the company's **CIK** from official SEC data
* Display mailing and business addresses
* Show state of incorporation and entity type
* Retrieve and print **most recent financial facts** for the current year

---

### 🛠 Example Output

```
Entity Information:
------------------------------
CIK: 0000789019
Entity Name: MICROSOFT CORP
Mailing Address: ...
State of Incorporation: WA
Entity Type: operating

Most Recent Filed Concepts:
------------------------------
Concept: Assets
  Value: 364840000000
  Filing Date: 2024-07-30
  Unit: USD
  Form Type: 10-K
```

---

### 📚 API Reference

* [SEC EDGAR API Docs](https://www.sec.gov/edgar/sec-api-documentation)
* [SEC Ticker to CIK Mapping](https://www.sec.gov/files/company_tickers.json)

---

### 🤝 Contributing

Pull requests are welcome! If you'd like to suggest enhancements, open an issue or submit a PR.

---

### ⚖️ License

This project is licensed under the [MIT License](LICENSE).

---

Let me know if you want this turned into a `README.md` file or would like badges (like Python version, license, etc.) added at the top.
