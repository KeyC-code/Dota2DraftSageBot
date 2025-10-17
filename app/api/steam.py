import requests
import logging
import aiohttp
from app.config import CURRENT_PATCH

HEROES = []

def load_heroes_sync(steam_api_key: str) -> None:
    global HEROES, CURRENT_PATCH
    try:
        response = requests.get(
            "https://api.steampowered.com/IEconDOTA2_570/GetHeroes/v1",
            params={"key": steam_api_key, "language": "ru"},
        )
        data = response.json()
        HEROES[:] = sorted(
            [
                hero["name"].split("npc_dota_hero_")[-1].replace("_", " ").title()
                for hero in data["result"]["heroes"]
            ]
        )
        logging.info(f"[INIT] Загружено {len(HEROES)} героев")

        match_resp = requests.get(
            "https://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/v1",
            params={"key": steam_api_key, "matches_requested": 1},
        )
        match_data = match_resp.json()
        if matches := match_data.get("result", {}).get("matches"):
            CURRENT_PATCH = matches[0].get("patch", CURRENT_PATCH)
        logging.info(f"[INIT] Текущий патч: {CURRENT_PATCH}")

    except Exception as e:
        logging.error(f"[INIT] Ошибка загрузки данных: {e}")


async def update_game_info(steam_api_key: str) -> None:
    global HEROES, CURRENT_PATCH
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/v1",
                params={"key": steam_api_key, "matches_requested": 1},
            ) as resp:
                match_data = await resp.json()
                if matches := match_data.get("result", {}).get("matches"):
                    CURRENT_PATCH = matches[0].get("patch", CURRENT_PATCH)
                    logging.info(f"Updated patch: {CURRENT_PATCH}")

            async with session.get(
                "https://api.steampowered.com/IEconDOTA2_570/GetHeroes/v1",
                params={"key": steam_api_key, "language": "ru"},
            ) as resp:
                hero_data = await resp.json()
                HEROES = sorted(
                    [
                        hero["name"]
                        .split("npc_dota_hero_")[-1]
                        .replace("_", " ")
                        .title()
                        for hero in hero_data["result"]["heroes"]
                    ]
                )
                logging.info(f"Updated heroes: {len(HEROES)} heroes")

    except Exception as e:
        logging.error(f"Update error: {str(e)}")