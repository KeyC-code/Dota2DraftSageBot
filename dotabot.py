import logging
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ContentType
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import LabeledPrice
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.sub_manager import SubscriptionManager
from app.api.gigachat import get_analysis
from app.api.steam import update_game_info, load_heroes_sync, HEROES
from dotenv import load_dotenv
from app.config import (
    MONTH_PRICE,
    THREE_MONTH_PRICE,
    DRAFT_ORDER,
    MAX_STEPS,
)
import app.keyboards as kb
from app.state import DraftState
import app.database.user as user

load_dotenv(".env")

GIGACHAT_AUTH_KEY = os.getenv("GIGACHAT_AUTH_KEY")
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
STEAM_API_KEY = str(os.getenv("STEAM_API_KEY"))
ADMIN_ID = int(os.getenv("ADMIN_ID"))


bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()



@dp.message(Command("start"))
async def start(message: types.Message) -> None:
    SubscriptionManager.get_user(message.from_user.id, message.from_user.full_name)

    text = """🎮 <b>Dota2 Draft Sage</b> — твой персональный стратег в Dota 2!
⚔️ Я анализирую составы команд и даю профессиональные советы:
    • Контрпики против вражеских героев
    • Оптимальные сборки предметов
    • Прокачка способностей по уровням
    • Тактические решения на разных стадиях игры

✨ <b>Бесплатно</b>: 3 анализа драфта
💎 <b>Премиум</b>: безлимитные запросы и приоритетная обработка

🚀 <b>Начни прямо сейчас:</b>
    /draft — анализ текущего драфта
    /subscribe — подписка Premium"""

    await message.answer(text, reply_markup=kb.start_keyboard())


@dp.callback_query(F.data == "start_draft")
async def start_draft_handler(callback: types.CallbackQuery, state: FSMContext):
    await draft_start(callback.message, state)


@dp.message(Command("draft"))
async def draft_start(message: types.Message, state: FSMContext):
    if not SubscriptionManager.check_access(
        message.chat.id, message.chat.full_name
    ):
        await message.answer("🚫 Лимит исчерпан!")
        await subscribe(message)
        return

    await state.set_state(DraftState.selecting_side)
    await state.update_data(
        side=None,
        step=0,
        allies=set(),
        enemies=set(),
        bans_allies=set(),
        bans_enemies=set(),
        page=0,
    )

    await message.answer(
        "🌅 Выберите вашу сторону:", reply_markup=kb.build_side_keyboard()
    )


@dp.callback_query(F.data.startswith("side_"))
async def select_side(callback: types.CallbackQuery, state: FSMContext):
    side = callback.data.split("_")[1]
    await state.update_data(side=side, step=0)

    await state.set_state(DraftState.drafting)

    step, side_turn = DRAFT_ORDER[0]
    data = await state.get_data()
    await callback.message.edit_text(
        f"Этап 1/{MAX_STEPS}: {step.upper()} ({side_turn})",
        reply_markup=kb.build_hero_keyboard(HEROES, data.get("page", 0), data, 0),
    )


@dp.callback_query(F.data.startswith("hero_"))
async def select_hero(callback: types.CallbackQuery, state: FSMContext):
    _, step_str, hero = callback.data.split("_", 2)
    step = int(step_str)

    data = await state.get_data()
    if step != data["step"]:
        await callback.answer("⚠️ Этот шаг уже завершён.")
        return

    action, side_turn = DRAFT_ORDER[step]
    user_side = data["side"]

    if action == "ban":
        if side_turn == user_side:
            data["bans_allies"].add(hero)
        else:
            data["bans_enemies"].add(hero)
    elif action == "pick":
        if side_turn == user_side:
            data["allies"].add(hero)
        else:
            data["enemies"].add(hero)

    new_step = step + 1
    data["step"] = new_step
    await state.update_data(**data)

    if new_step >= MAX_STEPS:
        await callback.message.edit_text(
            "✅ Драфт завершён! Жмите 📊 Анализ.",
            reply_markup=kb.build_hero_keyboard(
                HEROES, data.get("page", 0), data, new_step
            ),
        )
        return

    next_action, next_side_turn = DRAFT_ORDER[new_step]
    await callback.message.edit_text(
        f"Этап {new_step+1}/{MAX_STEPS}: {next_action.upper()} ({next_side_turn})",
        reply_markup=kb.build_hero_keyboard(HEROES, 0, data, new_step),
    )


@dp.callback_query(F.data.startswith("page_"))
async def change_page(callback: types.CallbackQuery, state: FSMContext):
    _, step_str, page_str = callback.data.split("_")
    step, page = int(step_str), int(page_str)

    data = await state.get_data()
    await state.update_data(page=page)

    await callback.message.edit_reply_markup(
        reply_markup=kb.build_hero_keyboard(HEROES, page, data, step)
    )


@dp.callback_query(F.data == "analyze_now")
async def analyze_now(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    side = data["side"]

    draft_order_lines = []
    for i, step_info in enumerate(DRAFT_ORDER):
        action, team_turn = step_info
        if action == "ban":
            hero = data["bans_allies"] if team_turn == side else data["bans_enemies"]
        else:
            hero = data["allies"] if team_turn == side else data["enemies"]
        hero_name = next(iter(hero), "—") if hero else "—"
        draft_order_lines.append(
            f"{i+1}. {'❌' if action=='ban' else '✅'} {hero_name} ({team_turn})"
        )

    prompt = (
        f"Сторона игрока: {side}\n"
        f"Текущий порядок бан/пиков:\n" + "\n".join(draft_order_lines) + "\n"
        "Дай полный анализ: кто следующий для пика и бана, какие аспекты героя выбрать "
        "(позиция, роль, предметы, прокачка способностей) и тактические рекомендации."
    )

    await callback.message.answer("🤔 Думаю...")
    analysis = await get_analysis(GIGACHAT_AUTH_KEY, prompt)

    user_id, user_name = callback.from_user.id, callback.from_user.full_name
    if SubscriptionManager.get_user(user_id, user_name).free_requests:
        SubscriptionManager.use_free_request(user_id)

    await callback.message.answer(f"📊 Результат анализа:\n\n{analysis}")


@dp.callback_query(F.data == "back_to_allies")
async def back_to_allies(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await callback.message.edit_text("🛡 Выберите героев своей команды:")
    await callback.message.edit_reply_markup(
        reply_markup=kb.build_hero_keyboard(
            HEROES, data.get("page", 0), data, data.get("step", 0)
        )
    )


@dp.message(Command("subscribe"))
async def subscribe(message: types.Message) -> None:
    user = SubscriptionManager.get_user(
        message.from_user.id, message.from_user.full_name
    )
    if user.free_requests <= 0:
        await message.answer(
            "💎 Подпишись и спрашивай сколько хочешь)",
            reply_markup=kb.subscribe_keyboard(user),
        )


@dp.callback_query(F.data.startswith("buy_subscription$"))
async def process_payment(callback: types.CallbackQuery) -> None:
    duration = int(callback.data.split("$")[1])
    amount = MONTH_PRICE if duration == 1 else THREE_MONTH_PRICE
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="Премиум подписка",
        description="Доступ профессиональному анализу драфтов на 1 месяц",
        currency="XTR",
        prices=[LabeledPrice(label="Подписка", amount=amount)],
        payload=f"subscription_{duration}",
    )


@dp.pre_checkout_query()
async def pre_checkout_handler(query: types.PreCheckoutQuery) -> None:
    await bot.answer_pre_checkout_query(query.id, ok=True)


@dp.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message) -> None:
    try:
        payload = message.successful_payment.invoice_payload
        if payload.startswith("subscription_"):
            duration = int(payload.split("_")[1])
            SubscriptionManager.activate_subscription(message.from_user.id, duration)
            await message.answer("✅ Подписка активирована!")
    except Exception as e:
        logging.error(f"Payment error: {str(e)}")
        await message.answer("❌ Ошибка активации подписки")


@dp.message(Command("stat"))
async def stats(message: types.Message) -> None:
    if message.from_user.id != ADMIN_ID:
        return

    stats = user.get_stats()

    text = (
        "📈 *Статистика бота*\n\n"
        f"• Всего пользователей: {stats[0]}\n"
        f"• Премиум подписок: {stats[1]}\n"
        f"• Среднее бесплатных запросов: {stats[2]:.1f}"
    )
    await message.answer(text)


@dp.message(Command("reload"))
async def reload_heroes(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    load_heroes_sync(STEAM_API_KEY)
    print(f"HEROES loaded: {len(HEROES)} heroes")
    await message.answer(f"✅ Герои обновлены: {len(HEROES)}")


async def on_startup() -> None:
    scheduler = AsyncIOScheduler()
    scheduler.start()
    scheduler.add_job(update_game_info, "cron", hour=2, minute=0, args=(STEAM_API_KEY,))
    user.initialise()
    load_heroes_sync(STEAM_API_KEY)
    logging.info("✅ Бот запущен. Герои загружены.")
    if ADMIN_ID:
        try:
            await bot.send_message(ADMIN_ID, f"🟢 Бот запущен. Героев: {len(HEROES)}")
        except:
            pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    dp.startup.register(on_startup)
    dp.run_polling(bot)
