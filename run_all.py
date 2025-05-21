import subprocess
import os

# Default to "1" if CHUNK_NUM is not set
chunk_num = os.getenv("CHUNK_NUM", "1")
input_file = f"chunks/links_part_{chunk_num}.json"
output_file = f"output/output_scraper_{chunk_num}.json"
failed_file = f"output/failed_links_{chunk_num}.csv"

print("\n🌀 Running fallback scraper...")
subprocess.run([
    "python", "fallback_playwright_scraper.py",
    "--input", input_file,
    "--output", output_file,
    "--failed", failed_file,
    "--max-concurrent", "10",
    "--batch-size", "20",
    "--url-limit", "100"
], check=True)

print("\n✅ All steps completed.")
