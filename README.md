# 🗺️ Google Maps Business Scraper

This project automates the extraction of business data from Google Maps links. It includes two main Python scripts:

1. `convert_csv_to_json.py` – Converts URLs from a CSV file to a clean JSON format.
2. `fallback_playwright_scraper.py` – Uses Playwright to scrape business data from those URLs.

---

## 📂 Overview

**Step 1**: Convert your raw CSV file (e.g., exported from a lead list) into a clean JSON list of Google Maps URLs.

**Step 2**: Scrape business details such as:
- Name
- Address
- Phone number
- Website
- Rating
- Category
- Opening hours
- Short description

---

## 🛠️ Requirements

- Python 3.7 or higher
- pip (Python package manager)
- Google Chrome or Chromium (Playwright installs its own headless version)

---

## ⚙️ Installation (Step-by-Step)

### 1. Clone this repository

```bash
git clone https://github.com/HarisNadeem471/Google-maps-scrapper-for-business-.git
cd google-maps-scraper
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Playwright browser binaries

```bash
playwright install
```

---

## 🚀 Usage

### ✅ Option A: Run both scripts with one command

```bash
python run_all.py
```

### ⚙️ Option B: Run scripts manually

#### Step 1: Convert CSV to JSON

```bash
python convert_csv_to_json.py
```

#### Step 2: Scrape data from Google Maps

```bash
python fallback_playwright_scraper.py
```

---

## 📁 Output Files

| File Name             | Description                                           |
|----------------------|-------------------------------------------------------|
| `links.json`         | JSON array of cleaned Google Maps URLs               |
| `output_results.csv` | Final scraped business data                           |
| `failed_links.csv`   | List of URLs that failed during scraping with reason  |

