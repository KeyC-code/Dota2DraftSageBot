from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.sub_manager import User
from app.config import MONTH_PRICE, THREE_MONTH_PRICE
PAGE_SIZE = 20


def start_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🚀 Начать анализ", callback_data="start_draft")
    return builder.as_markup()

def subscribe_keyboard(user: User) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f"💎 1 месяц {MONTH_PRICE} ⭐️",
        callback_data="buy_subscription$1",
    )
    builder.button(
        text=f"💎 3 месяца {THREE_MONTH_PRICE} ⭐️",
        callback_data="buy_subscription$3",
    )
    builder.adjust(1)
    return builder.as_markup()

def build_side_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="🌞 Radiant (Свет)", callback_data="side_Radiant"),
        InlineKeyboardButton(text="🌚 Dire (Тьма)", callback_data="side_Dire"),
    )
    builder.adjust(2)
    return builder.as_markup()


def build_hero_keyboard(
    heroes: list, page: int, data: dict, step: int
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    banned_or_picked = (
        set(data.get("allies", set()))
        | set(data.get("enemies", set()))
        | set(data.get("bans_allies", set()))
        | set(data.get("bans_enemies", set()))
    )

    available_heroes = [h for h in heroes if h not in banned_or_picked]

    start_idx = page * PAGE_SIZE
    current_page_heroes = available_heroes[start_idx : start_idx + PAGE_SIZE]

    if not current_page_heroes:
        builder.add(
            InlineKeyboardButton(text="❌ Нет доступных героев", callback_data="noop")
        )
        return builder.as_markup()

    for hero in current_page_heroes:
        builder.button(text=hero, callback_data=f"hero_{step}_{hero}")
    builder.adjust(2)

    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(text="⬅️ Назад", callback_data=f"page_{step}_{page-1}")
        )
    if start_idx + PAGE_SIZE < len(available_heroes):
        nav_buttons.append(
            InlineKeyboardButton(text="➡️ Вперед", callback_data=f"page_{step}_{page+1}")
        )
    if nav_buttons:
        builder.row(*nav_buttons)

    builder.row(
        InlineKeyboardButton(
            text="📊 Анализ текущего драфта", callback_data="analyze_now"
        )
    )

    return builder.as_markup()
