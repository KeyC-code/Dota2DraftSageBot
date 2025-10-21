import os
import platform
import shutil
import tempfile
from unittest.mock import AsyncMock, patch

import pytest


@pytest.fixture(autouse=True)
def mock_env_autouse():
    """Автоматически применяет моки env для всех тестов"""
    with patch.dict(
        os.environ,
        {
            "TELEGRAM_BOT_TOKEN": "1234:test_token",
            "ADMIN_ID": "123456789",
            "STEAM_API_KEY": "test_steam_key",
            "GIGACHAT_AUTH_KEY": "dGVzdF9rZXk=",
            "CURRENT_PATCH": "7.36",
            "SYSTEM_PROMPT": "You are a Dota 2 expert.",
        },
    ):
        yield


# остальные фикстуры без изменений
@pytest.fixture
def temp_db():
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")
    yield db_path
    if platform.system() == "Windows":
        try:
            shutil.rmtree(temp_dir)
        except PermissionError:
            pass
    else:
        shutil.rmtree(temp_dir)


@pytest.fixture
def mock_bot():
    return AsyncMock()


@pytest.fixture
def mock_user():
    return {
        "id": 987654321,
        "full_name": "Test User",
        "chat": {"id": 987654321, "full_name": "Test User"},
    }
