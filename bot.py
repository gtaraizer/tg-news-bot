import requests
from bs4 import BeautifulSoup
import time
import openai
import logging

# ============== НАСТРОЙКИ ==============
TELEGRAM_TOKEN = "ТОКЕН_ТВОЕГО_БОТА"
CHANNEL_ID = "@твой_канал"   # например, @gosviplaty_news
OPENAI_API_KEY = "ТОКЕН_OPENAI"  # ключ от OpenAI API
CHECK_INTERVAL = 1800  # проверять каждые 30 мин

openai.api_key = OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)

# Источники новостей
SOURCES = {
    "banki": "https://www.banki.ru/news/",
    "ria": "https://ria.ru/economy/"
}

# Хранилище уже опубликованных ссылок (чтобы не дублировать)
posted_links = set()


# ============== ФУНКЦИИ ==============

def fetch_banki():
    """Парсим новости с banki.ru"""
    url = SOURCES["banki"]
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "html.parser")
    articles = soup.select("a.WidgetNews__title")[:3]  # последние 3 новости
    news = []
    for a in articles:
        link = "https://www.banki.ru" + a["href"]
        title = a.get_text(strip=True)
        news.append({"title": title, "link": link})
    return news


def fetch_ria():
    """Парсим новости с ria.ru"""
    url = SOURCES["ria"]
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "html.parser")
    articles = soup.select("a.list-item__title")[:3]
    news = []
    for a in articles:
        link = a["href"]
        if not link.startswith("http"):
            link = "https://ria.ru" + link
        title = a.get_text(strip=True)
        news.append({"title": title, "link": link})
    return news


def rewrite_with_ai(title, link):
    """Переписывание новости ИИ"""
    prompt = f"""
    Перепиши новость простым, живым языком для Telegram-канала о выплатах и льготах.
    Текст должен быть коротким (3-5 предложений), с эмодзи, понятный обычному человеку.
    Вот заголовок: "{title}"
    Вот ссылка: {link}
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )
    return response["choices"][0]["message"]["content"]


def post_to_telegram(text):
    """Отправка текста в канал"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHANNEL_ID, "text": text, "parse_mode": "HTML"}
    r = requests.post(url, data=payload)
    if r.status_code != 200:
        logging.error(f"Ошибка отправки: {r.text}")


# ============== ОСНОВНОЙ ЦИКЛ ==============
def main():
    while True:
        try:
            logging.info("Проверяем новые новости...")
            news = fetch_banki() + fetch_ria()
            for item in news:
                if item["link"] not in posted_links:
                    text = rewrite_with_ai(item["title"], item["link"])
                    post_to_telegram(text)
                    posted_links.add(item["link"])
                    logging.info(f"Опубликовано: {item['title']}")
        except Exception as e:
            logging.error(f"Ошибка: {e}")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
