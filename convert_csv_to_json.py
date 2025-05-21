import pandas as pd
import json

# Load CSV
df = pd.read_csv("links.csv")

# Extract columns that contain URLs
link_columns = [col for col in df.columns if ".url" in col]

# Flatten and clean
all_links = df[link_columns].values.flatten()
clean_links = [link for link in all_links if pd.notna(link) and isinstance(link, str) and link.strip() != ""]

# Limit to 2000 for testing
#clean_links = clean_links[:500]

# Save to JSON
with open("links.json", "w") as f:
    json.dump(clean_links, f, indent=2)

print(f"✅ Saved {len(clean_links)} links to links.json")
