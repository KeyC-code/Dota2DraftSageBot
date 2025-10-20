from unittest.mock import MagicMock, patch

import pytest

from app.api.gigachat import get_analysis


@pytest.mark.asyncio
async def test_get_analysis_success():
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Анализ: играйте Anti-Mage."}}]
    }
    mock_response.status_code = 200

    with patch("app.api.gigachat.requests.post", return_value=mock_response), \
         patch("app.api.gigachat.get_gigachat_token", return_value="fake_token"):

        result = await get_analysis("fake_key", "Test prompt")
        assert "Anti-Mage" in result


@pytest.mark.asyncio
async def test_get_analysis_auth_fail():
    with patch("app.api.gigachat.get_gigachat_token", return_value=None):
        result = await get_analysis("fake_key", "Test prompt")
        assert "Ошибка сервиса" in result


@pytest.mark.asyncio
async def test_get_analysis_empty_response():
    mock_response = MagicMock()
    mock_response.json.return_value = {"choices": []}

    with patch("app.api.gigachat.requests.post", return_value=mock_response), \
         patch("app.api.gigachat.get_gigachat_token", return_value="fake_token"):

        result = await get_analysis("fake_key", "Test prompt")
        assert "Пустой ответ" in result