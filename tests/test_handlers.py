from unittest.mock import AsyncMock, patch

import pytest
from aiogram import types

import app.database.user as db_user


@pytest.mark.asyncio
async def test_start_handler(mock_user, temp_db):
    original = db_user.DB_NAME
    db_user.DB_NAME = temp_db

    try:
        db_user.initialise()

        from_user_mock = AsyncMock()
        from_user_mock.id = mock_user["id"]
        from_user_mock.full_name = mock_user["full_name"]

        message = AsyncMock()
        message.from_user = from_user_mock
        message.answer = AsyncMock()

        from dotabot import start

        await start(message)

        message.answer.assert_called_once()
        assert "Dota2 Draft Sage" in message.answer.call_args[0][0]

    finally:
        db_user.DB_NAME = original


@pytest.mark.asyncio
async def test_draft_start_no_access(mock_user, temp_db):
    with patch("app.database.user.DB_NAME", temp_db):
        from app.database import user as db_user

        db_user.initialise()
        db_user.create_user(mock_user["id"], mock_user["full_name"])
        for _ in range(3):
            db_user.use_free_request(mock_user["id"])

        chat_mock = AsyncMock()
        chat_mock.id = mock_user["id"]
        chat_mock.full_name = mock_user["full_name"]

        message = AsyncMock(spec=types.Message)
        message.chat = chat_mock
        message.answer = AsyncMock()

        state = AsyncMock()

        with patch("dotabot.subscribe") as mock_subscribe:
            from dotabot import draft_start

            await draft_start(message, state)

        message.answer.assert_called_with("🚫 Лимит исчерпан!")
        mock_subscribe.assert_called_once_with(message)


@pytest.mark.asyncio
async def test_select_side():
    message_mock = AsyncMock()
    message_mock.edit_text = AsyncMock()

    callback = AsyncMock(spec=types.CallbackQuery)
    callback.data = "side_Radiant"
    callback.message = message_mock

    state = AsyncMock()
    state.get_data = AsyncMock(return_value={"page": 0})

    from dotabot import select_side

    await select_side(callback, state)

    state.update_data.assert_called()
    callback.message.edit_text.assert_called()
