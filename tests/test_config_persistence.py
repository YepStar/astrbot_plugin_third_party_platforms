import json
from pathlib import Path
from astrbot.api import AstrBotConfig

def test_dynamic_account_mappings_survive_real_astrbot_reload(tmp_path):
 schema=json.loads((Path(__file__).parents[1]/'_conf_schema.json').read_text())
 p=tmp_path/'config.json';config=AstrBotConfig(str(p),schema=schema)
 config['platforms']['bilibili']['accounts']['named-account']={'enabled':True,'reply':{'private_scope':'owner'},'actions':{'reply':True}}
 config['platforms']['netease']['accounts']['default']={'enabled':True,'actions':{'listen':True}}
 config.save_config()
 loaded=AstrBotConfig(str(p),schema=schema)
 assert loaded['platforms']['bilibili']['accounts']['named-account']['actions']['reply']
 assert loaded['platforms']['netease']['accounts']['default']['actions']['listen']


def test_extension_platform_and_options_survive_real_config_reload(tmp_path):
 schema=json.loads((Path(__file__).parents[1]/'_conf_schema.json').read_text())
 p=tmp_path/'config.json';config=AstrBotConfig(str(p),schema=schema)
 config['platforms']['future_media']={'enabled':True,'accounts':{'account':{'enabled':True,'browse':{'provider_options':{'category':'games'}}}}}
 config.save_config()
 loaded=AstrBotConfig(str(p),schema=schema)
 assert loaded['platforms']['future_media']['accounts']['account']['browse']['provider_options']['category']=='games'


def test_platform_weights_survive_real_config_reload(tmp_path):
 schema=json.loads((Path(__file__).parents[1]/'_conf_schema.json').read_text())
 p=tmp_path/'config.json';config=AstrBotConfig(str(p),schema=schema)
 config['platform_weights']={'bilibili':3.5,'future_media':0}
 config.save_config();loaded=AstrBotConfig(str(p),schema=schema)
 assert loaded['platform_weights']=={'bilibili':3.5,'future_media':0}
