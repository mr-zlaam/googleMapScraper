import json
import asyncio
from playwright.async_api import async_playwright
import time
import re
import csv

INPUT_FILE = "links.json"
OUTPUT_FILE_CSV = "output_results.csv"
FAILED_FILE_CSV = "failed_links.csv"
MAX_CONCURRENT_TASKS = 10
BATCH_SIZE = 20
URL_LIMIT = 100

def clean_text(text):
    return re.sub(r"[^\x00-\x7F]+", "", text).strip()

async def scrape_page(context, url, semaphore):
    async with semaphore:
        data = {"url": url}
        page = await context.new_page()
        try:
            await page.goto(url, timeout=60000)
            await page.wait_for_load_state("domcontentloaded")

            try:
                title = await page.title()
                data["name"] = title.replace(" - Google Maps", "").strip()
            except:
                data["name"] = ""

            try:
                address_elem = await page.query_selector('//button[contains(@aria-label, "Address")]')
                data["address"] = clean_text(await address_elem.inner_text()) if address_elem else ""
            except:
                data["address"] = ""

            try:
                phone_elem = await page.query_selector('//button[contains(@aria-label, "Phone")]')
                data["phone"] = clean_text(await phone_elem.inner_text()) if phone_elem else ""
            except:
                data["phone"] = ""

            try:
                website_elem = await page.query_selector('//a[contains(@aria-label, "Website")]')
                data["website"] = await website_elem.get_attribute('href') if website_elem else ""
            except:
                data["website"] = ""

            try:
                rating_elem = await page.query_selector('//span[contains(@aria-label, "stars")] | //div[contains(@aria-label, "stars")]')
                rating_text = await rating_elem.get_attribute("aria-label") if rating_elem else ""
                data["rating"] = re.search(r"[\d.]+", rating_text).group() if rating_text else ""
            except:
                data["rating"] = ""

            try:
                cat_elem = await page.query_selector('//button[contains(@aria-label, "Category")]')
                if not cat_elem:
                    cat_elem = await page.query_selector('//span[contains(@class, "fontBodyMedium")]')
                data["category"] = await cat_elem.inner_text() if cat_elem else "All"
            except:
                data["category"] = "All"

            try:
                open_elem = await page.query_selector('//span[contains(text(), "Open") or contains(text(), "Closed") or contains(text(), "Closes")]')
                data["opening_hours"] = await open_elem.inner_text() if open_elem else ""
            except:
                data["opening_hours"] = ""

            try:
                desc_elem = await page.query_selector('//meta[@property="og:description"]')
                raw_desc = await desc_elem.get_attribute("content") if desc_elem else ""
                cleaned_desc = re.sub(r"[★☆]+ ?· ?", "", raw_desc).strip()
                data["short_description"] = cleaned_desc
            except:
                data["short_description"] = ""

            print(f"✅ {data['name']}")
        except Exception as e:
            summary = str(e).split("\n")[0][:100]
            safe_title = url.split("/place/")[-1].split("/")[0].replace("+", " ")
            print(f"⚠️ Skipped: {safe_title} (Reason: Timeout or navigation error)")
            data["name"] = safe_title
            data["error"] = "Navigation Timeout or Load Failure"
        finally:
            await page.close()
            return data

async def main():
    start_time = time.time()

    with open(INPUT_FILE, "r") as f:
        urls = json.load(f)[:URL_LIMIT]

    print(f"📥 Loaded {len(urls)} links (limit: {URL_LIMIT})\n")
    all_results = []

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        for i in range(0, len(urls), BATCH_SIZE):
            batch = urls[i:i + BATCH_SIZE]
            print(f"\n🔄 Processing batch {i // BATCH_SIZE + 1} ({len(batch)} URLs)...")
            tasks = [scrape_page(context, url, semaphore) for url in batch]
            results = await asyncio.gather(*tasks)
            all_results.extend(results)

        await browser.close()

    # Remove duplicates by URL
    unique_results = list({item["url"]: item for item in all_results}.values())

    # Save successful results
    keys = sorted(set().union(*(d.keys() for d in unique_results)))
    with open(OUTPUT_FILE_CSV, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(unique_results)

    # Save failed URLs separately
    with open(FAILED_FILE_CSV, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["url", "error"])
        for r in unique_results:
            if "error" in r:
                writer.writerow([r["url"], r["error"]])

    elapsed = int(time.time() - start_time)
    minutes, seconds = divmod(elapsed, 60)
    print(f"\n📊 Scraped: {len(unique_results)} total, with {sum('error' in x for x in unique_results)} failed entries.")
    print(f"💾 Output saved to: {OUTPUT_FILE_CSV}")
    print(f"📂 Failed links saved to: {FAILED_FILE_CSV}")
    print(f"⏱️ Time taken: {minutes:02d}:{seconds:02d}")

if __name__ == "__main__":
    asyncio.run(main())
