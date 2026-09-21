import feedparser
from datetime import datetime


def fetch_feed(url, source="News Source"):
    stories = []

    try:
        feed = feedparser.parse(url)

        for entry in feed.entries[:10]:

            title = entry.get(
                "title",
                "Untitled"
            )

            summary = entry.get(
                "summary",
                ""
            )

            link = entry.get(
                "link",
                ""
            )

            published = entry.get(
                "published",
                str(datetime.now())
            )

            stories.append({
                "source": source,
                "title": title,
                "content": summary,
                "link": link,
                "published": published
            })

    except Exception:
        return []

    return stories


def fetch_multiple_feeds(feeds):
    all_stories = []

    for source, url in feeds.items():

        stories = fetch_feed(
            url,
            source
        )

        all_stories.extend(
            stories
        )

    return all_stories
