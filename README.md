# goal_data_collection

Small project to scrape wikihow articles for chosen topics and save them to JSON.

Quick start

1. Create a virtualenv and install dependencies:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Run the crawler (this will fetch a small number of pages per topic):

```powershell
python crawler.py
```

Outputs are written to the `data/` directory as `{topic}.json` files.

Notes
- Be polite and avoid scraping aggressively; adjust `per_topic` and add delays as needed.
- Consider recording HTML fixtures for unit tests to avoid live requests.
