import json
import asyncio
from playwright.async_api import async_playwright
import time
import re
import csv
import argparse


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
                data["rating"] = re.search(
                    r"[\d.]+", rating_text).group() if rating_text else ""
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
            safe_title = url.split(
                "/place/")[-1].split("/")[0].replace("+", " ")
            print(f"⚠️ Skipped: {safe_title} (Reason: Timeout or navigation error)")
            data["name"] = safe_title
            data["error"] = "Navigation Timeout or Load Failure"
        finally:
            await page.close()
            return data


async def main(input_file, output_file_csv, failed_file_csv, max_concurrent_tasks, batch_size, url_limit):
    start_time = time.time()

    with open(input_file, "r") as f:
        urls = json.load(f)[:url_limit]

    print(f"📥 Loaded {len(urls)} links (limit: {url_limit})\n")
    all_results = []

    semaphore = asyncio.Semaphore(max_concurrent_tasks)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        for i in range(0, len(urls), batch_size):
            batch = urls[i:i + batch_size]
            print(f"\n🔄 Processing batch {   i // batch_size + 1} ({len(batch)} URLs)...")
            tasks = [scrape_page(context, url, semaphore) for url in batch]
            results = await asyncio.gather(*tasks)
            all_results.extend(results)

        await browser.close()

    # Remove duplicates by URL
    unique_results = list({item["url"]: item for item in all_results}.values())

    # Save successful results
    keys = sorted(set().union(*(d.keys() for d in unique_results)))
    with open(output_file_csv, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(unique_results)

    # Save failed URLs separately
    with open(failed_file_csv, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["url", "error"])
        for r in unique_results:
            if "error" in r:
                writer.writerow([r["url"], r["error"]])

    elapsed = int(time.time() - start_time)
    minutes, seconds = divmod(elapsed, 60)
    print(f"\n📊 Scraped: {len(unique_results)} total, with {  sum('error' in x for x in unique_results)} failed entries.")
    print(f"💾 Output saved to: {output_file_csv}")
    print(f"📂 Failed links saved to: {failed_file_csv}")
    print(f"⏱️ Time taken: {minutes:02d}:{seconds:02d}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Google Maps Scraper using Playwright")
    parser.add_argument("--input", required=True,
                        help="Input JSON file with URLs")
    parser.add_argument("--output", required=True,
                        help="Output CSV file for results")
    parser.add_argument("--failed", default="failed_links.csv",
                        help="Output CSV file for failed URLs")
    parser.add_argument("--max-concurrent", type=int,
                        default=10, help="Maximum concurrent tasks")
    parser.add_argument("--batch-size", type=int, default=20,
                        help="Batch size for processing URLs")
    parser.add_argument("--url-limit", type=int, default=100,
                        help="Maximum number of URLs to process")

    args = parser.parse_args()

    asyncio.run(main(
        input_file=args.input,
        output_file_csv=args.output,
        failed_file_csv=args.failed,
        max_concurrent_tasks=args.max_concurrent,
        batch_size=args.batch_size,
        url_limit=args.url_limit
    ))
