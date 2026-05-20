"""Scrape Douban movie collection and output CSV."""
import re
import csv
import sys
import urllib.request

USER_ID = "159838615"
OUTPUT = f"/Users/haoxinlei/Desktop/开发/学习/notes/scripts/douban_movies.csv"


def fetch_page(start=0):
    url = f"https://movie.douban.com/people/{USER_ID}/collect?start={start}&sort=time&mode=grid"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode("utf-8")


def parse_movies(html):
    """Parse movie items from Douban grid page."""
    movies = []
    # Match each movie item
    pattern = re.compile(
        r'<li class="title">.*?'
        r'<a href="https://movie.douban.com/subject/(\d+)/".*?'
        r'<em>(.*?)</em>.*?'
        r'<span class="rating(\d)-t"></span>.*?'
        r'</li>',
        re.DOTALL,
    )

    # Also try alternative patterns for items without ratings
    items = re.findall(
        r'<div class="item">(.*?)</div>\s*</div>',
        html,
        re.DOTALL,
    )
    for item in items:
        title_m = re.search(r'<em>(.*?)</em>', item)
        link_m = re.search(r'href="https://movie\.douban\.com/subject/(\d+)/"', item)
        rating_m = re.search(r'<span class="rating(\d)-t"></span>', item)
        date_m = re.search(r'<span class="date">(.*?)</span>', item)

        if title_m:
            movies.append({
                "title": title_m.group(1).strip(),
                "douban_id": link_m.group(1) if link_m else "",
                "rating": rating_m.group(1) if rating_m else "",
                "date": date_m.group(1).strip() if date_m else "",
            })

    return movies


def main():
    all_movies = []
    start = 0

    for page in range(10):  # max 10 pages
        try:
            html = fetch_page(start)
            movies = parse_movies(html)
            if not movies:
                break
            all_movies.extend(movies)
            print(f"Page {page+1}: {len(movies)} movies (total {len(all_movies)})")
            start += 30
        except Exception as e:
            print(f"Error at page {page+1}: {e}")
            break

    # Write CSV
    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "douban_id", "rating", "date"])
        writer.writeheader()
        writer.writerows(all_movies)

    print(f"\nExported {len(all_movies)} movies to {OUTPUT}")


if __name__ == "__main__":
    main()
