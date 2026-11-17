import importlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import AsyncMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
main = importlib.import_module(Path(__file__).resolve().parents[1].name + ".main")
UMO = "qq_bot:FriendMessage:349138581"
TEXT = (
    "提到《孤山独影》这硬核攀岩独立游戏。\nhttps://www.bilibili.com/video/BV1JbsJ6HEi5"
)


def plugin(*, delivered=True, cid="current"):
    manager = NS(
        get_curr_conversation_id=AsyncMock(return_value=cid),
        new_conversation=AsyncMock(return_value="new"),
        get_conversation=AsyncMock(
            return_value=NS(
                history=json.dumps([{"role": "user", "content": "上一条用户消息"}])
            )
        ),
        update_conversation=AsyncMock(),
    )
    context = NS(
        send_message=AsyncMock(return_value=delivered),
        conversation_manager=manager,
        get_registered_star=lambda _: None,
    )
    obj = object.__new__(main.ThirdPartyPlatforms)
    obj.context = context
    return obj, manager


@pytest.mark.parametrize("card", [False, True])
async def test_successful_delivery_is_visible_in_private_history(card):
    obj, manager = plugin()
    if card:
        await obj.deliver_card(UMO, TEXT, "/tmp/card.png")
    else:
        await obj.deliver(UMO, TEXT)
    args = manager.update_conversation.await_args
    assert args.args == (UMO, "current")
    history = args.kwargs["history"]
    assert history[0] == {"role": "user", "content": "上一条用户消息"}
    assert len(history) == 2 and history[-1]["role"] == "assistant"
    assert TEXT in history[-1]["content"]
    obj.context.send_message.assert_awaited_once()


async def test_unsent_message_never_enters_history():
    obj, manager = plugin(delivered=False)
    with pytest.raises(RuntimeError, match="owner_delivery_unconfirmed"):
        await obj.deliver(UMO, TEXT)
    manager.update_conversation.assert_not_awaited()


async def test_creates_history_in_the_exact_recipient_session():
    obj, manager = plugin(cid=None)
    await obj.deliver(UMO, TEXT)
    manager.new_conversation.assert_awaited_once_with(UMO)
    assert manager.update_conversation.await_args.args == (UMO, "new")


async def test_history_failure_does_not_resend_or_mark_delivery_failed():
    obj, manager = plugin()
    manager.update_conversation.side_effect = RuntimeError("database unavailable")
    await obj.deliver(UMO, TEXT)
    obj.context.send_message.assert_awaited_once()


async def test_companion_archives_with_its_existing_lock_and_without_fake_user_turn():
    obj, manager = plugin()
    archive = AsyncMock(return_value=True)
    obj.context.get_registered_star = lambda _: NS(
        activated=True, star_cls=NS(_archive_proactive_message_to_conversation=archive)
    )
    await obj.deliver(UMO, TEXT)
    archive.assert_awaited_once_with(
        user={"umo": UMO}, user_prompt="", assistant_response=TEXT, umo=UMO
    )
    manager.update_conversation.assert_not_awaited()


async def test_non_private_recipient_is_rejected_before_send():
    obj, manager = plugin()
    with pytest.raises(ValueError, match="private_recipient_required"):
        await obj.deliver("qq_bot:GroupMessage:123", TEXT)
    obj.context.send_message.assert_not_awaited()
    manager.update_conversation.assert_not_awaited()
