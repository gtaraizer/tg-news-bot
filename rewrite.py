
import os
import re

SYSTEM_PROMPT = (
    "Ты редактор Telegram-канала о выплатах, льготах и господдержке. "
    "Пиши коротко, ясно и дружелюбно. Не искажай факты и не делай выводов, которых нет в источнике. "
    "Структура: 1) короткий яркий заголовок (1 строка), 2) 3–5 коротких предложений сути, "
    "3) в конце укажи 'Источник: <ссылка>'. Используй уместные эмодзи, сохраняй цифры и даты."
)

def _rewrite_openai(prompt: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY не задан")

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            max_tokens=500,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        import openai  # type: ignore
        openai.api_key = api_key
        resp = openai.ChatCompletion.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            max_tokens=500,
        )
        return resp["choices"][0]["message"]["content"].strip()

def build_prompt(title: str, text: str, link: str) -> str:
    body = (text or "").strip()
    body = re.sub(r"\s+", " ", body)[:2500]
    return (
        f"Заголовок: {title}\n\n"
        f"Текст статьи (фрагмент): {body}\n\n"
        f"Ссылка: {link}\n\n"
        "Перепиши по правилам."
    )

def rewrite_news(title: str, text: str, link: str) -> str:
    prompt = build_prompt(title, text, link)
    return _rewrite_openai(prompt)
