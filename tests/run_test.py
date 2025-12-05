import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from wikihow_data import scrape_wikihow

url = "https://www.wikihow.com/Learn-French"
print("Fetching:", url)
data = scrape_wikihow(url)
print("Found methods:", len(data.get("methods", [])))
for m in data.get("methods", []):
    print(" -", m["method"], "steps:", len(m["steps"]))

assert len(data.get("methods", [])) > 0, "methods list is empty"
print("OK")
