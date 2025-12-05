import requests
from bs4 import BeautifulSoup

url = "https://www.wikihow.com/Learn-French"
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
text = r.text

counts = {
    'class="method"': text.count('class="method"'),
    'class="steps"': text.count('class="steps"'),
    'class="step"': text.count('class="step"'),
    "data-testid": text.count("data-testid"),
    "section class": text.count("<section"),
}
print("counts:", counts)

soup = BeautifulSoup(text, "html.parser")
# print top-level section tags and their classes
sections = soup.find_all(["section", "div", "ol", "ul"], limit=60)
for i, s in enumerate(sections[:40]):
    cls = s.get("class")
    id = s.get("id")
    name = s.name
    txt = " ".join(cls) if cls else ""
    if id or cls:
        print(i, name, id, txt)

# search for 'method' anywhere
if "method" in text:
    print('\n-- "method" appears in page text --')
    loc = text.find("method")
    print(text[loc - 120 : loc + 120])

# show any element containing 'steps'
for el in soup.find_all(
    lambda tag: tag.name in ["div", "section", "ol", "ul"]
    and tag.get("class")
    and any("step" in c for c in " ".join(tag.get("class")).split())
):
    print("\nFound element with step in class:", el.name, el.get("class"))
    break

# Try to find any headings (h2/h3/h4) that contain "Method" or the word "Method" in their text
print('\n-- Scanning headings for "Method" --')
found = 0
for tag in soup.find_all(["h2", "h3", "h4", "h5"]):
    t = tag.get_text(strip=True)
    if "Method" in t or "method" in t:
        print("Heading:", tag.name, "-", t[:120])
        found += 1
        if found > 15:
            break

print('\n-- Looking for containers that include the word "method" in class names --')
for el in soup.find_all(
    lambda tag: tag.get("class") and any("method" in c for c in tag.get("class"))
):
    print("Element:", el.name, el.get("class"))
    break

print('\n-- Inspecting all "steps" containers and their headings/parents --')
for i, el in enumerate(
    soup.find_all(
        lambda tag: tag.get("class") and any("steps" in c for c in tag.get("class"))
    )
):
    print("\nSTEPS CONTAINER", i, el.name, el.get("class"))
    # try to find a previous header in the DOM
    prev = el.find_previous(["h2", "h3", "h4", "h5"])
    if prev:
        print("  previous heading:", prev.name, repr(prev.get_text(strip=True)[:120]))
    # try to find a parent block with section in class
    parent_with_section = el.find_parent(
        lambda tag: tag.get("class") and any("section" in c for c in tag.get("class"))
    )
    if parent_with_section:
        print(
            "  parent section class:",
            parent_with_section.name,
            parent_with_section.get("class"),
        )
    if i > 8:
        break
