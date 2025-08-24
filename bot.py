
import os
import time
import logging
from typing import Dict

from .news import get_candidates, fetch_article_text
from .rewrite import rewrite_news
from .publish import post_to_telegram
from .storage import is_posted, mark_posted

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(message)s"
)

CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "1200"))  # default 20 min

def compose_message(title: str, rewritten: str, link: str) -> str:
    # Ensure we always include a source link at the end
    if "http" not in rewritten:
        rewritten += f"\n\nИсточник: {link}"
    return rewritten.strip()

def process_item(item: Dict):
    url = item["link"]
    if is_posted(url):
        logging.debug(f"Already posted: {url}")
        return

    logging.info(f"Processing: {item['title']} | {url}")
    article_text = fetch_article_text(url)
    rewritten = rewrite_news(item["title"], article_text, url)
    message = compose_message(item["title"], rewritten, url)
    post_to_telegram(message)
    mark_posted(url)
    logging.info(f"Posted: {item['title']}")

def main():
    logging.info("Bot started. Interval: %s sec", CHECK_INTERVAL)
    while True:
        try:
            candidates = get_candidates()
            for it in candidates:
                try:
                    process_item(it)
                except Exception as e:
                    logging.exception(f"Error processing item: {it.get('link')} | {e}")
        except Exception as e:
            logging.exception(f"Cycle error: {e}")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
