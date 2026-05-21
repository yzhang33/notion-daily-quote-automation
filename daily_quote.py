import os
import sys
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

NOTION_VERSION = "2022-06-28"

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
QUOTES_DB_ID = os.environ["NOTION_QUOTES_DB_ID"]
API_NINJAS_KEY = os.environ["API_NINJAS_KEY"]

TIMEZONE = os.environ.get("TIMEZONE", "America/New_York")
QUOTE_CATEGORY = os.environ.get("QUOTE_CATEGORY", "wisdom").strip()

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json",
}


def notion_post(url, payload):
    response = requests.post(url, headers=NOTION_HEADERS, json=payload, timeout=30)
    if not response.ok:
        print("Notion API error:", response.status_code)
        print(response.text)
        response.raise_for_status()
    return response.json()


def notion_patch(url, payload):
    response = requests.patch(url, headers=NOTION_HEADERS, json=payload, timeout=30)
    if not response.ok:
        print("Notion API error:", response.status_code)
        print(response.text)
        response.raise_for_status()
    return response.json()


def fetch_quote_by_category(category):
    """
    Fetch a random quote from API Ninjas by category.
    Example category: wisdom
    Example multiple categories: wisdom,success
    """

    url = "https://api.api-ninjas.com/v2/randomquotes"

    headers = {
        "X-Api-Key": API_NINJAS_KEY
    }

    params = {}
    if category:
        params["categories"] = category

    response = requests.get(url, headers=headers, params=params, timeout=30)

    if not response.ok:
        print("Quote API error:", response.status_code)
        print(response.text)
        response.raise_for_status()

    data = response.json()

    if not data or not isinstance(data, list):
        raise RuntimeError("Unexpected quote API response.")

    item = data[0]

    quote_text = item.get("quote", "").strip()
    author = item.get("author", "").strip()
    work = item.get("work", "").strip()
    categories = item.get("categories", [])

    if not quote_text:
        raise RuntimeError("Quote text is empty.")

    if not categories:
        categories = [c.strip() for c in category.split(",") if c.strip()]

    return {
        "quote": quote_text,
        "author": author,
        "work": work,
        "categories": categories,
        "source_url": "https://api.api-ninjas.com/api/quotes",
    }


def find_existing_quote_page(today_iso, categories):
    """
    Prevent duplicate rows for the same date and same first category.
    If you use multiple categories, this checks the first category.
    """

    primary_category = categories[0] if categories else QUOTE_CATEGORY

    payload = {
        "filter": {
            "and": [
                {
                    "property": "Date",
                    "date": {
                        "equals": today_iso
                    }
                },
                {
                    "property": "Category",
                    "multi_select": {
                        "contains": primary_category
                    }
                }
            ]
        },
        "page_size": 10,
    }

    data = notion_post(
        f"https://api.notion.com/v1/databases/{QUOTES_DB_ID}/query",
        payload,
    )

    results = data.get("results", [])
    return results[0] if results else None


def build_quote_properties(quote_data, today_iso):
    categories = quote_data["categories"]

    return {
        "Quote": {
            "title": [
                {
                    "text": {
                        "content": quote_data["quote"]
                    }
                }
            ]
        },
        "Author": {
            "rich_text": [
                {
                    "text": {
                        "content": quote_data["author"]
                    }
                }
            ]
        },
        "Date": {
            "date": {
                "start": today_iso
            }
        },
        "Category": {
            "multi_select": [
                {
                    "name": category
                }
                for category in categories
            ]
        },
        "Work": {
            "rich_text": [
                {
                    "text": {
                        "content": quote_data["work"]
                    }
                }
            ]
        },
        "Source": {
            "url": quote_data["source_url"]
        },
        "Created By": {
            "select": {
                "name": "GitHub Actions"
            }
        },
    }


def create_quote_page(quote_data, today_iso):
    quote_text = quote_data["quote"]
    author = quote_data["author"]

    payload = {
        "parent": {
            "database_id": QUOTES_DB_ID
        },
        "properties": build_quote_properties(quote_data, today_iso),
        "children": [
            {
                "object": "block",
                "type": "quote",
                "quote": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": f"{quote_text}\n— {author}" if author else quote_text
                            }
                        }
                    ]
                }
            }
        ],
    }

    return notion_post("https://api.notion.com/v1/pages", payload)


def update_quote_page(page_id, quote_data, today_iso):
    payload = {
        "properties": build_quote_properties(quote_data, today_iso)
    }

    return notion_patch(
        f"https://api.notion.com/v1/pages/{page_id}",
        payload,
    )


def main():
    today = datetime.now(ZoneInfo(TIMEZONE)).date()
    today_iso = today.isoformat()

    quote_data = fetch_quote_by_category(QUOTE_CATEGORY)
    existing_page = find_existing_quote_page(today_iso, quote_data["categories"])

    if existing_page:
        update_quote_page(existing_page["id"], quote_data, today_iso)
        print(f"Updated quote for {today_iso}")
    else:
        create_quote_page(quote_data, today_iso)
        print(f"Created quote for {today_iso}")

    print(f"Category: {', '.join(quote_data['categories'])}")
    print(f"Quote: {quote_data['quote']}")
    if quote_data["author"]:
        print(f"Author: {quote_data['author']}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Failed:", str(e))
        sys.exit(1)