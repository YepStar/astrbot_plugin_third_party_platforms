import importlib
from pathlib import Path
import sys
from types import SimpleNamespace as NS
from unittest.mock import AsyncMock
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
base=Path(__file__).resolve().parents[1].name
extensions=importlib.import_module(base+'.core.extensions')


def provider():
 return NS(id='example_media',capabilities={'browse','owner_share'},status=AsyncMock(),browse=AsyncMock(),close=AsyncMock())


def test_manifest_and_bounded_provider_configuration():
 definition=extensions.manifest(provider(),{'api':1,'name':'Example','fields':{
  'section':{'type':'string','default':'games'},'page_count':{'type':'int','default':2,'min':1,'max':5}}})
 assert extensions.options(definition,{'page_count':3})=={'section':'games','page_count':3}
 for bad in [{'page_count':True},{'page_count':6},{'unknown':'value'}]:
  with pytest.raises(ValueError):extensions.options(definition,bad)


@pytest.mark.parametrize('manifest',[{'api':2},{'fields':{'access_token':{'type':'string'}}},
 {'fields':{'x':{'type':'int','default':False}}},{'fields':{'x':{'type':'file'}}}])
def test_manifest_rejects_incompatible_versions_and_public_credentials(manifest):
 with pytest.raises(ValueError):extensions.manifest(provider(),manifest)
