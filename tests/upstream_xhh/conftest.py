import pytest
from astrbot_plugin_third_party_platforms.providers.xhh_client.database import Database
from astrbot_plugin_third_party_platforms.providers.xhh_client.repository import Repository

@pytest.fixture
async def repository(tmp_path):
 database=Database(tmp_path/'xhh.db');await database.open()
 yield Repository(database)
 await database.close()
