import requests
import uuid
import logging
from app.config import SYSTEM_PROMPT
from typing import Any

def get_gigachat_token(gigachat_auth_key) -> Any | None:
    try:
        response = requests.post(
            "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "RqUID": str(uuid.uuid4()),
                "Authorization": f"Basic {gigachat_auth_key}",
            },
            data={"scope": "GIGACHAT_API_PERS"},
            verify=False,
        )
        return response.json()["access_token"]
    except Exception as e:
        logging.error(f"GigaChat auth error: {str(e)}")
        return None


async def get_analysis(gigachat_auth_key: str, prompt: str) -> str:
    token = get_gigachat_token(gigachat_auth_key)
    if not token:
        return "🚫 Ошибка сервиса, попробуйте позже"

    try:
        response = requests.post(
            "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json={
                "model": "GigaChat",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.4,
                "max_tokens": 1800,
            },
            verify=False,
        )

        result = response.json()

        if "choices" not in result or not result["choices"]:
            logging.error(f"GigaChat пустой ответ: {result}")
            return "⚠️ Пустой ответ от анализа, попробуйте ещё раз"

        analysis = result["choices"][0]["message"]["content"].strip()

        return analysis.replace("**", "").replace("#", "")

    except Exception as e:
        logging.error(f"GigaChat error: {str(e)}")
        return "⚠️ Ошибка анализа, попробуйте другой состав"