"""Exercise real executor/facade cancellation and persisted scheduler receipts."""
import asyncio
import importlib
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
package = Path(__file__).resolve().parents[1].name
models = importlib.import_module(package + '.core.models')
execution = importlib.import_module(package + '.core.execution')
Store = importlib.import_module(package + '.core.store').Store
Music = importlib.import_module(package + '.integrations.music').Music


def policy():
    return SimpleNamespace(permit=lambda *args: {}, limits=lambda *args: [])


@pytest.mark.asyncio
async def test_music_survives_short_request_timeout_and_reaches_reflection(tmp_path, monkeypatch):
    phases = []
    async def roundtrip(*args, **kwargs):
        phases.append('playing')
        try:
            await asyncio.sleep(.08)
        except asyncio.CancelledError:
            phases.append('interrupted')
            raise
        phases.append('reflect_and_consider_invitation')
        return {'state': 'succeeded', 'code': 'decision_processed'}
    facade = SimpleNamespace(third_party_scheduler_api=1,
        third_party_scheduler_acquire=AsyncMock(return_value=True),
        third_party_scheduler_run=roundtrip)
    music = Music(SimpleNamespace(get_registered_star=lambda _: SimpleNamespace(star_cls=facade)))
    # Scale the session budget down so this reproduces the 45-second regression quickly.
    monkeypatch.setattr(music, 'action_timeouts', {'listen': .5}, raising=False)
    store = Store(tmp_path / 'db')
    registry = models.Registry(); registry.register(music)
    engine = execution.Executor(store, registry, policy(), timeout=.02)
    receipt = await engine.execute('netease', 'default', 'listen', {}, 'listen:test')
    assert receipt.state == 'succeeded'
    assert phases == ['playing', 'reflect_and_consider_invitation']
    assert store.actions()[0]['state'] == 'succeeded'
    assert await engine.execute('netease', 'default', 'listen', {}, 'listen:test') is None


@pytest.mark.asyncio
async def test_normal_network_action_keeps_short_timeout(tmp_path):
    class Provider:
        id = 'p'; capabilities = {'comment'}
        async def execute(self, *args):
            await asyncio.sleep(.2)
            return models.Receipt('succeeded')
    registry = models.Registry(); registry.register(Provider())
    engine = execution.Executor(Store(tmp_path / 'db'), registry, policy(), timeout=.02)
    receipt = await engine.execute('p', 'default', 'comment', {}, 'comment:test')
    assert receipt.state == 'unknown' and receipt.code == 'TimeoutError'


@pytest.mark.asyncio
@pytest.mark.parametrize('state', ['succeeded', 'unknown', 'failed'])
async def test_scheduler_persists_actual_music_receipt(tmp_path, state):
    store = Store(tmp_path / 'db')
    registry = models.Registry(); registry.register(SimpleNamespace(id='netease', capabilities={'listen'}))
    engine = execution.Executor(store, registry, policy())
    key = store.create_task('netease', 'default', 'listen', 1, 100)
    handler = AsyncMock(return_value=models.Receipt(state, code='fixture'))
    scheduler = execution.Scheduler(store, registry, engine, {'listen': handler}, clock=lambda: 50)
    await scheduler.tick()
    await asyncio.gather(*(future for _, future in list(scheduler.running.values())))
    assert next(row for row in store.tasks() if row['id'] == key)['state'] == state


def test_music_session_budget_covers_longest_supported_song():
    assert 1800 < Music.action_timeouts['listen'] <= 3600


@pytest.mark.asyncio
@pytest.mark.parametrize('publication_allowed', [True, False])
async def test_real_music_facade_finishes_audio_then_respects_invitation_gate(tmp_path, monkeypatch, publication_allowed):
    # Optional integration test: clone netease_browser beside this repository.
    music_root = Path(__file__).resolve().parents[2] / 'astrbot_plugin_netease_browser'
    if not (music_root / 'music/scheduler_control.py').is_file():
        pytest.skip('install the netease_browser repository alongside this plugin for integration tests')
    control = importlib.import_module('astrbot_plugin_netease_browser.music.scheduler_control')
    autonomy = importlib.import_module('astrbot_plugin_netease_browser.music.autonomy')
    config = importlib.import_module('astrbot_plugin_netease_browser.music.config')
    storage = importlib.import_module('astrbot_plugin_netease_browser.music.storage')
    from unittest.mock import MagicMock
    cfg = {**config.DEFAULTS, 'autonomous_enabled': True, 'autonomous_invite': True,
           'owner_uid': '1', 'owner_umo': 'qq:FriendMessage:1', 'start_hour': 0, 'end_hour': 24}
    journal = storage.Store(tmp_path / 'music'); journal.save_cookie('test-fixture')
    ctl = control.SchedulerControl(journal.root)
    song = {'id': '101', 'name': 'Fixture', 'artists': 'Fixture', 'duration_ms': 180000}
    service = SimpleNamespace(current=None, search=AsyncMock(return_value={'songs': [song]}),
                              read=AsyncMock(return_value={'lyric': 'fixture'}))
    async def listen(sid, key, origin):
        async def audio():
            await asyncio.sleep(.08)
            journal.data['operations'][key] = {'kind': 'listen', 'status': 'completed', 'at': 1}
        service.play_task = asyncio.create_task(audio())
        return {'status': 'started'}
    service.listen = listen
    flow = SimpleNamespace(pending=lambda: False, propose=AsyncMock())
    generate = AsyncMock(side_effect=[{'action': 'listen', 'query': 'fixture'}, {'song_id': '101'},
                                      {'action': 'invite', 'note': 'fixture', 'private_message': '一起听Fixture吗？'}])
    plugin = SimpleNamespace(settings=cfg, store=journal, service=service)
    plugin.autonomy = autonomy.Autonomy(cfg, journal, service, MagicMock(), generate, flow)
    publication_gate = AsyncMock(return_value=publication_allowed)
    facade = SimpleNamespace(third_party_scheduler_api=1, third_party_scheduler_filter_api=1,
        third_party_scheduler_acquire=ctl.acquire,
        third_party_scheduler_run=lambda owner, key, **kw: ctl.run(plugin, owner, key, **kw))
    adapter = Music(SimpleNamespace(get_registered_star=lambda _: SimpleNamespace(star_cls=facade)))
    adapter.publication_gate = publication_gate
    monkeypatch.setattr(adapter, 'action_timeouts', {'listen': .5})
    registry = models.Registry(); registry.register(adapter)
    engine = execution.Executor(Store(tmp_path / 'host.db'), registry, policy(), timeout=.02)
    result = await engine.execute('netease', 'default', 'listen', {}, 'integration')
    assert result.state == 'succeeded'
    assert next(iter(journal.data['operations'].values()))['status'] == 'completed'
    assert generate.await_args_list[-1].args[0] == 'reflect'
    publication_gate.assert_awaited_once_with('invite', song, {'lyric': 'fixture'})
    assert flow.propose.await_count == int(publication_allowed)
    assert control.PUBLICATION_GATE.get() is None
