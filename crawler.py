import os
import time
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote_plus

from wikihow_data import scrape_wikihow

USER_AGENT = {"User-Agent": "Mozilla/5.0 (compatible; goal-scraper/1.0)"}


def search_topic(topic, max_results=10):
    """Search wikihow for a topic and return a list of article URLs.

    This uses the site search page `https://www.wikihow.com/wikiHowTo?search=...`
    and extracts article links by the 'result_link' class. Handles pagination by
    following 'Next' buttons. Returns absolute URLs to article pages only.
    """
    q = quote_plus(topic)
    links = []
    seen = set()
    page_url = f"https://www.wikihow.com/wikiHowTo?search={q}"

    while len(links) < max_results:
        try:
            r = requests.get(page_url, headers=USER_AGENT, timeout=25)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")

            # Extract article links by 'result_link' class
            for a in soup.find_all("a", class_="result_link"):
                if a.get("href"):
                    href = a["href"]
                    full = urljoin("https://www.wikihow.com", href)
                    # Filter: skip internal wiki pages and duplicates
                    if "/wikiHow:" in full or full in seen:
                        continue
                    seen.add(full)
                    links.append(full)
                    if len(links) >= max_results:
                        break

            if len(links) >= max_results:
                break

            # Look for 'Next' button in footer to follow pagination
            next_btn = soup.find("a", href=True, class_="primary")
            if next_btn and "Next" in next_btn.get_text(strip=True):
                next_href = next_btn["href"]
                page_url = urljoin("https://www.wikihow.com", next_href)
            else:
                # No more pages
                break
        except Exception as e:
            print(f"  Error fetching page {page_url}: {e}")
            break
    # print ("urls",len(links),links)
    return links


def crawl_topics(topics, per_topic=5, out_dir="data"):
    os.makedirs(out_dir, exist_ok=True)
    results = {}
    for topic in topics:
        print(f"Searching topic: {topic}")
        try:
            urls = search_topic(topic, max_results=per_topic * 2)
        except Exception as e:
            print(f"  Search failed for {topic}: {e}")
            urls = []

        # Take first `per_topic` article pages
        selected = urls[:per_topic]

        scraped = []
        for i, u in enumerate(selected):
            print(f"  [{i+1}/{len(selected)}] Scraping: {u}")
            try:
                # Pre-fetch page and do lightweight check
                r = requests.get(u, headers=USER_AGENT, timeout=15)
                r.raise_for_status()
                page_text = r.text

                # Quick heuristics: detect article pages by markers
                markers = [
                    'id="section_0"',
                    'class="mw-parser-output"',
                    'class="method_toc"',
                    'class="section steps"',
                ]
                if not any(m in page_text for m in markers):
                    print(f"    Skipping {u}: not an article (no markers)")
                    continue

                data = scrape_wikihow(u, html=page_text)
                # Include source URL
                data["url"] = u
                scraped.append(data)
            except Exception as e:
                print(f"    Failed to scrape {u}: {e}")
            # Be polite
            time.sleep(1.0)

        out_path = os.path.join(out_dir, f"{topic.replace(' ', '_')}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(
                {"topic": topic, "count": len(scraped), "articles": scraped},
                f,
                ensure_ascii=False,
                indent=2,
            )
        print(f"  Saved {len(scraped)} articles to {out_path}")
        results[topic] = {"count": len(scraped), "file": out_path}

    return results


if __name__ == "__main__":
    TOPICS = [
        "learning",
        # "study",
        # "fitness",
        # "cooking",
        # "productivity",
        # "money",
        # "health",
        # "relationships",
    ]
    # For a quick verification run, use 2 articles per topic. Increase as needed.
    res = crawl_topics(TOPICS, per_topic=50)
    print("\nDone. Summary:")
    for k, v in res.items():
        print(f" - {k}: {v['count']} -> {v['file']}")
