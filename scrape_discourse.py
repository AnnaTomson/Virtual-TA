import requests
import json
from datetime import datetime

BASE_URL = "https://discourse.onlinedegree.iitm.ac.in/t/"

def is_within_date_range(date_str, start, end):
    post_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    return start <= post_date <= end

def scrape_discourse(start_date, end_date, max_topics=10000):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    collected = []

    for topic_id in range(1, max_topics):
        url = f"{BASE_URL}{topic_id}.json"
        try:
            r = requests.get(url, timeout=5)
            if r.status_code != 200:
                continue
            data = r.json()
            for post in data.get("post_stream", {}).get("posts", []):
                created = post["created_at"]
                if is_within_date_range(created, start, end):
                    collected.append({
                        "url": url,
                        "post": post["cooked"].replace("<p>", "").replace("</p>", "").strip()
                    })
        except Exception as e:
            print(f"Error scraping topic {topic_id}: {e}")
            continue

    with open("data/discourse_posts.json", "w") as f:
        json.dump(collected, f, indent=2)
    print(f"Saved {len(collected)} posts.")

if __name__ == "__main__":
    scrape_discourse("2025-01-01", "2025-04-14")
