
# Telegram News Autoposter (Render Free Plan, Web Service)

Автопостинг новостей (banki.ru + РИА Экономика) в Telegram-канал.
Работает на Render **Free** как **Web Service**: FastAPI отдаёт healthcheck, в фоне крутится воркер.

## 🚀 Деплой на Render (Free)

1. Загрузите содержимое этого проекта в новый GitHub-репозиторий.
2. На Render → New + → Web Service → подключите репозиторий.
3. Настройки:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.server:app --host 0.0.0.0 --port $PORT`
   - Environment: Python 3
4. Environment Variables (Settings → Environment):
   - TELEGRAM_TOKEN — токен бота от @BotFather
   - CHANNEL_ID — @имя_вашего_канала (бот админ с правом постинга)
   - OPENAI_API_KEY — ключ OpenAI
   - (опц.) OPENAI_MODEL — по умолчанию gpt-4o-mini
   - CHECK_INTERVAL — интервал проверки (сек), напр. 1200
   - DB_PATH — путь к SQLite, по умолчанию state.db (эфемерно на Free)
   - LOG_LEVEL — INFO
   - RUN_ON_STARTUP — true
5. Deploy.

## Локальный запуск

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.template .env && nano .env  # заполните токены
export $(grep -v '^#' .env | xargs)  # Windows: set по одному
uvicorn app.server:app --host 0.0.0.0 --port 8000
```

## Как это работает

- `app/news.py` — парсит источники (banki.ru HTML, РИА RSS).
- `app/news.fetch_article_text()` — извлекает основной текст (readability).
- `app/rewrite.py` — переписывает с помощью OpenAI.
- `app/publish.py` — постит в Telegram.
- `app/storage.py` — SQLite база с таблицей `posted` (антидубли).
- `app/server.py` — FastAPI + фоновый цикл.
