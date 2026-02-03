from wikihow_data import scrape_wikihow


def test_methods_not_empty():
    data = scrape_wikihow("https://www.wikihow.com/Learn-French")
    assert isinstance(data, dict)
    assert "methods" in data
    assert len(data["methods"]) > 0, "methods list should not be empty for this URL"
