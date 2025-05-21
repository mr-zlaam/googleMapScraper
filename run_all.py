import subprocess
print("\n🌀 Running fallback scraper...")
subprocess.run(["python", "fallback_playwright_scraper.py"], check=True)

print("\n✅ All steps completed.")
