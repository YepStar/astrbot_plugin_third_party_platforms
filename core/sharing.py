"""Owner routes are configuration, never inferred from platform messages or model text."""
import asyncio
import hashlib
from .models import Receipt


def routes(provider, item):
    mode = item.get('share_delivery', 'qq_private')
    umo = item.get('owner_umo', '')
    uid = str(item.get('owner_uid', ''))
    name = item.get('owner_bili_name', '')
    available = {}
    if umo:
        available['qq_private'] = umo
    if provider == 'bilibili' and not item.get('reply',{}).get('dry_run',False) and uid.isdigit() and uid != str(item.get('self_uid', '')):
        available['private_message'] = uid
        if name and '\n' not in name and '@' not in name:
            available['comment'] = uid
    modes = {'both': ['private_message', 'comment'],
             'bili_private_and_qq': ['private_message', 'qq_private'],
             'all': ['private_message', 'comment', 'qq_private']}
    if mode == 'off':
        return []
    if mode == 'auto':
        return [(kind, available[kind]) for kind in ['qq_private', 'private_message'] if kind in available][:1]
    selected = modes.get(mode, [mode])
    # An explicitly selected route must not silently change to a different recipient/channel.
    if any(kind not in available for kind in selected):
        return []
    return [(kind, available[kind]) for kind in selected]


def delivery_key(provider, external_id, kind, recipient):
    # Retain the original QQ key so imported legacy receipts suppress duplicate sends.
    destination = recipient if kind == 'qq_private' else f'{kind}:{recipient}'
    return 'owner_share:' + hashlib.sha256(f'{provider}|{external_id}|{destination}'.encode()).hexdigest()


async def share(service, content, evaluation, text, item):
    if service.store.action(f'legacy_owner_share:{content.provider}:{content.account}:{content.external_id}'):
        return
    cooldown_key=f'last_owner_share:{content.provider}:{content.account}'
    last=service.store.setting(cooldown_key,0)
    if last and service.clock()-last<int(item.get('share_gap_seconds',0)):return
    selected = routes(content.provider, item)
    if not selected:
        return
    keys = [delivery_key(content.provider, content.external_id, kind, recipient) for kind, recipient in selected]
    # One recommendation consumes one shared quota, even when it has multiple deliveries.
    group_key = 'share_group:' + hashlib.sha256('|'.join(sorted(keys)).encode()).hexdigest()

    async def operation():
        receipts = []
        for (kind, recipient), key in zip(selected, keys):
            current = service.executor.policy.permit(content.provider, content.account, 'owner_share', evaluation)
            if (kind, recipient) not in routes(content.provider, current):
                receipts.append(Receipt('failed', code='route_changed'))
                continue
            if not service.store.claim_action(key, content.provider, content.account, 'share_delivery', [], service.clock()):
                record = service.store.action(key)
                state = record['state'] if record else 'unknown'
                receipts.append(Receipt(state if state in {'succeeded', 'failed'} else 'unknown'))
                continue
            try:
                if kind == 'qq_private':
                    await service.deliver(recipient, text)
                    result = Receipt('succeeded')
                else:
                    provider = service.registry.get(content.provider)
                    if kind == 'private_message':
                        action, params = 'private_reply', {'receiver': recipient, 'text': text}
                    else:
                        action = 'comment'
                        name = current['owner_bili_name']
                        params = {'oid': content.metadata['aid'], 'text': f'@{name} {text}',
                                  'at_name_to_mid': {name: int(recipient)}}
                    result = await provider.execute(content.account, action, params, key)
                    if not isinstance(result, Receipt):
                        raise TypeError('invalid_provider_receipt')
            except asyncio.CancelledError:
                service.store.finish_action(key, Receipt('unknown', code='cancelled_during_io'))
                raise
            except Exception as exc:
                result = Receipt('unknown', code=type(exc).__name__)
            service.store.finish_action(key, result)
            if result.state in {'succeeded','unknown'}:service.store.set_setting(cooldown_key,service.clock())
            receipts.append(result)
            # Ambiguous writes never trigger another delivery as an automatic fallback.
            if result.state == 'unknown':
                break
        if any(r.state == 'unknown' for r in receipts):
            return Receipt('unknown', code='delivery_uncertain')
        if any(r.state == 'succeeded' for r in receipts):
            return Receipt('succeeded')
        return Receipt('failed', code='no_delivery_succeeded')

    return await service.executor.execute(content.provider, content.account, 'owner_share', {}, group_key,
                                          evaluation=evaluation, operation=operation)
