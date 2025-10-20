from app import keyboards as kb
from app.config import MONTH_PRICE, THREE_MONTH_PRICE


def test_start_keyboard():
    markup = kb.start_keyboard()
    buttons = markup.inline_keyboard[0]
    assert len(buttons) == 1
    assert buttons[0].text == "🚀 Начать анализ"
    assert buttons[0].callback_data == "start_draft"


def test_subscribe_keyboard():
    from app.sub_manager import User

    mock_user = User((1, 0, False, None, None, "Test"))
    markup = kb.subscribe_keyboard(mock_user)

    buttons = markup.inline_keyboard
    assert len(buttons) == 2
    assert buttons[0][0].text == f"💎 1 месяц {MONTH_PRICE} ⭐️"
    assert buttons[1][0].text == f"💎 3 месяца {THREE_MONTH_PRICE} ⭐️"


def test_build_side_keyboard():
    markup = kb.build_side_keyboard()
    buttons = markup.inline_keyboard[0]
    assert len(buttons) == 2
    assert buttons[0].text == "🌞 Radiant (Свет)"
    assert buttons[1].text == "🌚 Dire (Тьма)"


def test_build_hero_keyboard_pagination():
    heroes = [f"Hero {i}" for i in range(30)]
    data = {
        "allies": set(),
        "enemies": set(),
        "bans_allies": set(),
        "bans_enemies": set(),
    }

    markup1 = kb.build_hero_keyboard(heroes, page=0, data=data, step=0)
    assert len(markup1.inline_keyboard) > 2

    markup2 = kb.build_hero_keyboard(heroes, page=1, data=data, step=0)
    first_hero_page1 = markup1.inline_keyboard[0][0].text
    first_hero_page2 = markup2.inline_keyboard[0][0].text
    assert first_hero_page1 != first_hero_page2
