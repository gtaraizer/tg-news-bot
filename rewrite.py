
import os
import re

SYSTEM_PROMPT = (
    "Ты редактор Telegram-канала о выплатах, льготах и господдержке. "
    "Пиши коротко, понятно и дружелюбно. Не обещай того, чего нет в источнике. "
    "Структура: яркий заголовок (1 строка), затем 3–5 коротких предложений сути, "
    "добавь эмодзи уместно, в конце — ссылка-источник. Если есть цифры/даты — сохрани их. "
    "Избегай жаргона и сложных терминов."
)

def _rewrite_openai(prompt: str) -> str:
    """Supports both new and legacy OpenAI Python SDKs."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY не задан")

    # Try the new SDK first
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
            max_tokens=450,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        # Legacy fallback
        try:
            import openai  # type: ignore
            openai.api_key = api_key
            resp = openai.ChatCompletion.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
                max_tokens=450,
            )
            return resp["choices"][0]["message"]["content"].strip()
        except Exception as e:
            raise

def build_prompt(title: str, text: str, link: str) -> str:
    # Keep prompt compact; include up to ~2000 chars of article body
    body = (text or "").strip()
    body = re.sub(r"\s+", " ", body)
    body = body[:2000]
    return (
        f"Заголовок: {title}\n\n"
        f"Текст статьи (фрагмент): {body}\n\n"
        f"Ссылка: {link}\n\n"
        "Перепиши по правилам."
    )

def rewrite_news(title: str, text: str, link: str) -> str:
    prompt = build_prompt(title, text, link)
    return _rewrite_openai(prompt)
