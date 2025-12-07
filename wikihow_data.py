from datetime import datetime
import requests
from bs4 import BeautifulSoup
import json
import re


def scrape_wikihow(url, html=None):
    # Accept pre-fetched HTML to avoid duplicate requests when caller already
    # fetched the page. If `html` is None, fetch it here.
    if html is None:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        r.raise_for_status()
        html = r.text
    soup = BeautifulSoup(html, "html.parser")

    # --- Goal ---
    # Title: try several fallbacks since some pages vary in structure
    goal_el = (
        soup.find("h1", {"id": "section_0"})
        or soup.find("h1")
        or soup.find("h1", class_="firstHeading")
    )
    goal = goal_el.get_text(strip=True) if goal_el else ""
    # --- Last Updated Date ---
    sp_text_data_list = soup.findAll("span", class_="sp_text_data")
    last_update_text=sp_text_data_list[1].get_text(strip=True)if len(sp_text_data_list) > 2 else "N/A"
    last_update_date=datetime.strptime(last_update_text,"%B %d, %Y").date().isoformat() if last_update_text!="N/A" else "N/A"

    # --- Methods ---
    methods = []

    # Helper to normalize class checks
    def class_contains(tag, *substrs):
        cls = tag.get("class")
        if not cls:
            return False
        joined = " ".join(cls)
        return any(s in joined for s in substrs)

    def extract_steps_from_container(container):
        steps = []
        # ol-based lists (li items) are commonly used
        if container.name == "ol" or class_contains(container, "steps_list"):
            for li in container.find_all("li", recursive=False):
                title_el = li.find("b")
                task = (
                    title_el.get_text(strip=True)
                    if title_el
                    else li.get_text(strip=True)
                )
                subtasks = []
                for ul in li.find_all("ul"):
                    for sub_li in ul.find_all("li"):
                        subtasks.append(sub_li.get_text(strip=True))
                steps.append({"task": task, "subtasks": subtasks})
            return steps

        # div-based steps (div.step)
        for step in container.find_all(
            lambda tag: tag.name == "div" and class_contains(tag, "step")
        ):
            title_el = step.find("b")
            task = (
                title_el.get_text(strip=True) if title_el else step.get_text(strip=True)
            )
            subtasks = [
                li.get_text(strip=True)
                for ul in step.find_all("ul")
                for li in ul.find_all("li")
            ]
            steps.append({"task": task, "subtasks": subtasks})
        return steps

    # The site's structure places method headings (usually h3) followed by a
    # steps container (ol.steps_list_2 or div.section.steps). Walk headings and
    # pick the following steps container for each.
    content = (
        soup.find("div", class_="mw-parser-output")
        or soup.find("div", class_="mw-content-text")
        or soup
    )

    # Consider h2/h3/h4 headings as possible method titles (but skip generic ones)
    skip_words = {
        "steps",
        "summary",
        "references",
        "tips",
        "related",
        "introduction",
        "materials",
    }
    for header in content.find_all(["h2", "h3", "h4"]):
        title = header.get_text(strip=True)
        if not title:
            continue
        if title.strip().lower() in skip_words:
            continue

        # find the nearest next element that looks like a steps container
        candidate = header.find_next(
            lambda tag: tag.name in ("ol", "div")
            and (
                class_contains(tag, "steps")
                or class_contains(tag, "steps_list")
                or class_contains(tag, "step")
            )
        )
        if not candidate:
            continue

        steps = extract_steps_from_container(candidate)
        if not steps:
            continue

        methods.append({"method": title, "steps": steps})

    return {"goal": goal,"last_update":last_update_date, "methods": methods}


# # --- Example test ---
# data = scrape_wikihow("https://www.wikihow.com/Learn-French")
# print(json.dumps(data, indent=2, ensure_ascii=False))
